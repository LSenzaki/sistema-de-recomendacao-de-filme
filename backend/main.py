from fastapi import FastAPI, HTTPException
# Trigger reload
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
import unicodedata
import os
import subprocess
import ast

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Loading and Startup Check
DATA_PATH = "data/processed_movies.csv"
PROCESSOR_SCRIPT = "backend/data_processor.py"

if not os.path.exists(DATA_PATH):
    print(f"Processed data not found at {DATA_PATH}. Running data processor...")
    try:
        subprocess.run(["python", PROCESSOR_SCRIPT], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running data processor: {e}")
        # Try to load fallback or exit? For now, we'll let pandas fail if file still missing

try:
    df_movies = pd.read_csv(DATA_PATH)
    # Ensure list columns are parsed correctly if they were saved as strings
    # But for TF-IDF we might just treat them as strings.
    # Let's fill NaNs first
    df_movies = df_movies.fillna('')
except FileNotFoundError:
    print("Error: Data file not found even after attempting to generate it.")
    df_movies = pd.DataFrame() # Empty fallback

# Text Preprocessing
def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    
    # Normalization
    text = text.lower()
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Tokenization
    tokens = word_tokenize(text)
    
    # Stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [t for t in tokens if t not in stop_words]
    
    return " ".join(tokens)

def create_combined_features(row):
    # Combine title, genre, description, director, cast, and keywords
    # Weighting (optimized for keyword matching): 
    # Keywords (6x) - HIGHEST PRIORITY for keyword-based searches
    # Title (3x)
    # Director (3x)
    # Cast (2x), Genre (2x)
    # Description (1x)
    
    # Helper to handle list-like strings or lists
    def get_str(val):
        if isinstance(val, list):
            return " ".join(val)
        if isinstance(val, str) and val.startswith('['):
            try:
                # It's a string representation of a list
                return " ".join(ast.literal_eval(val))
            except:
                return val
        return str(val)

    genre_str = get_str(row['genre'])
    cast_str = get_str(row['cast'])
    keyword_str = get_str(row.get('keywords', '')) # Handle missing keywords column gracefully
    director_str = str(row['director'])
    
    features = [
        keyword_str * 6,  # Increased from 3x to 6x for better keyword matching
        str(row['title']) * 3,
        director_str * 3,
        cast_str * 2,
        genre_str * 2,
        str(row['description'])
    ]
    combined_text = " ".join(features)
    return preprocess_text(combined_text)

# Prepare TF-IDF
if not df_movies.empty:
    df_movies['processed_features'] = df_movies.apply(create_combined_features, axis=1)
    # Use n-grams (1, 2) to capture phrases
    tfidf = TfidfVectorizer(ngram_range=(1, 2))
    tfidf_matrix = tfidf.fit_transform(df_movies['processed_features'])
else:
    tfidf_matrix = None

class RecommendationRequest(BaseModel):
    query: str

@app.get("/movies")
def get_movies():
    if df_movies.empty:
        return []
    # Return top 200 movies sorted by popularity
    return df_movies.nlargest(200, 'popularity').to_dict(orient="records")

@app.get("/genres")
def get_genres():
    """Get all unique genres from the dataset."""
    if df_movies.empty:
        return []
    
    # Extract all genres from all movies
    all_genres = set()
    for genres_str in df_movies['genre']:
        try:
            if isinstance(genres_str, str):
                genres_list = ast.literal_eval(genres_str)
                if isinstance(genres_list, list):
                    all_genres.update(genres_list)
        except:
            pass
    
    return sorted(list(all_genres))

@app.get("/movies/by-genre/{genre}")
def get_movies_by_genre(genre: str, limit: int = 20):
    """Get movies filtered by genre, sorted by popularity."""
    if df_movies.empty:
        return []
    
    # Filter movies that contain the specified genre
    filtered_movies = []
    for idx, row in df_movies.iterrows():
        try:
            genres_str = row['genre']
            if isinstance(genres_str, str):
                genres_list = ast.literal_eval(genres_str)
                if isinstance(genres_list, list) and genre in genres_list:
                    filtered_movies.append(row.to_dict())
        except:
            pass
    
    # Sort by popularity and limit
    filtered_df = pd.DataFrame(filtered_movies)
    if not filtered_df.empty:
        filtered_df = filtered_df.nlargest(limit, 'popularity')
        return filtered_df.to_dict(orient="records")
    
    return []

@app.post("/recommend")
def recommend(request: RecommendationRequest):
    if df_movies.empty or tfidf_matrix is None:
        return []

    query_processed = preprocess_text(request.query)
    query_vec = tfidf.transform([query_processed])
    
    similarity = cosine_similarity(query_vec, tfidf_matrix).flatten()
    
    # Get top 10 recommendations
    indices = similarity.argsort()[-10:][::-1]
    
    recommendations = []
    
    # Find max score to normalize
    max_score = 0
    if len(indices) > 0:
        max_score = similarity[indices[0]]
    
    for i in indices:
        if similarity[i] > 0: 
            movie = df_movies.iloc[i].to_dict()
            
            # Normalize score
            if max_score > 0:
                normalized_score = (similarity[i] / max_score) * 0.95
            else:
                normalized_score = 0
                
            movie['score'] = float(normalized_score)
            
            # Handle NaN in dictionary
            for k, v in movie.items():
                if pd.isna(v):
                    movie[k] = ""
                    
            recommendations.append(movie)
            
    return recommendations

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
