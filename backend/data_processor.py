import pandas as pd
import ast
import numpy as np

def parse_list(x):
    try:
        if isinstance(x, str):
            return ast.literal_eval(x)
        return []
    except:
        return []

def get_director(crew_list):
    for member in crew_list:
        if member.get('job') == 'Director':
            return member.get('name')
    return np.nan

def get_cast_names(cast_list):
    if isinstance(cast_list, list):
        names = [member.get('name') for member in cast_list]
        return names[:5] # Top 5 cast members
    return []

def get_genres(genre_list):
    if isinstance(genre_list, list):
        return [g.get('name') for g in genre_list]
    return []

def get_keywords(keyword_list):
    if isinstance(keyword_list, list):
        names = [k.get('name') for k in keyword_list]
        return names[:10] # Top 10 keywords
    return []

def get_production_companies(companies_list):
    if isinstance(companies_list, list):
        return [c.get('name') for c in companies_list]
    return []

def process_data():
    print("Loading datasets...")
    # Load movies metadata
    meta = pd.read_csv('data/extracted/movies_metadata.csv', low_memory=False, on_bad_lines='skip')
    
    # Load credits
    credits = pd.read_csv('data/extracted/credits.csv', low_memory=False, on_bad_lines='skip')

    # Load keywords
    keywords = pd.read_csv('data/extracted/keywords.csv', low_memory=False, on_bad_lines='skip')

    print("Cleaning IDs...")
    # Convert ID to numeric and handle errors
    meta['id'] = pd.to_numeric(meta['id'], errors='coerce')
    credits['id'] = pd.to_numeric(credits['id'], errors='coerce')
    keywords['id'] = pd.to_numeric(keywords['id'], errors='coerce')
    
    # Drop rows with NaN IDs
    meta = meta.dropna(subset=['id'])
    credits = credits.dropna(subset=['id'])
    keywords = keywords.dropna(subset=['id'])
    
    # Convert to integer for merging
    meta['id'] = meta['id'].astype(int)
    credits['id'] = credits['id'].astype(int)
    keywords['id'] = keywords['id'].astype(int)

    print("Merging datasets...")
    # Merge metadata with credits
    movies = meta.merge(credits, on='id')
    
    # Merge with keywords
    movies = movies.merge(keywords, on='id')

    print("Processing features...")
    # Parse JSON columns
    movies['genres'] = movies['genres'].apply(parse_list)
    movies['cast'] = movies['cast'].apply(parse_list)
    movies['crew'] = movies['crew'].apply(parse_list)
    movies['keywords'] = movies['keywords'].apply(parse_list)
    movies['production_companies'] = movies['production_companies'].apply(parse_list)

    # Extract useful info
    movies['director'] = movies['crew'].apply(get_director)
    movies['cast_names'] = movies['cast'].apply(get_cast_names)
    movies['genre_names'] = movies['genres'].apply(get_genres)
    
    # Enrich keywords with production companies
    movies['keyword_names'] = movies['keywords'].apply(get_keywords)
    movies['company_names'] = movies['production_companies'].apply(get_production_companies)
    
    # Combine keywords and companies into one list for the 'keywords' column
    movies['final_keywords'] = movies.apply(lambda x: x['keyword_names'] + x['company_names'], axis=1)

    # Filter for valid images
    # Must have a poster_path and it must be a string of reasonable length
    movies = movies[movies['poster_path'].notna()]
    movies = movies[movies['poster_path'].apply(lambda x: isinstance(x, str) and len(x) > 5)]

    # Create image URL
    # Ensure poster_path starts with /
    def format_image_url(path):
        if not isinstance(path, str):
            return ""
        if not path.startswith('/'):
            path = '/' + path
        return f"https://image.tmdb.org/t/p/w500{path}"

    movies['image_url'] = movies['poster_path'].apply(format_image_url)

    # Select and rename columns
    final_df = movies[[
        'id', 
        'title', 
        'overview', 
        'genre_names', 
        'image_url', 
        'director', 
        'cast_names', 
        'final_keywords',
        'vote_average', 
        'vote_count',
        'popularity'
    ]].copy()

    final_df.rename(columns={
        'overview': 'description',
        'genre_names': 'genre',
        'cast_names': 'cast',
        'final_keywords': 'keywords'
    }, inplace=True)

    # Filter for quality
    # Lower threshold to include more movies (Vote count >= 50)
    # This should give us a much larger dataset while still filtering out complete noise
    final_df = final_df[final_df['vote_count'] >= 50]

    # Fill NaNs
    final_df['description'] = final_df['description'].fillna('')
    final_df['director'] = final_df['director'].fillna('')
    final_df['genre'] = final_df['genre'].apply(lambda x: x if isinstance(x, list) else [])
    final_df['cast'] = final_df['cast'].apply(lambda x: x if isinstance(x, list) else [])
    final_df['keywords'] = final_df['keywords'].apply(lambda x: x if isinstance(x, list) else [])

    print(f"Saving {len(final_df)} processed movies...")
    final_df.to_csv('data/processed_movies.csv', index=False)
    print("Done!")

if __name__ == "__main__":
    process_data()
