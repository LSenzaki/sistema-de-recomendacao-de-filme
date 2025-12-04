"""
Wagner Approves - Sistema de Recomendação de Filmes (Versão Semântica)
======================================================================

Melhorias implementadas:
1. Sentence-BERT para embeddings semânticos
2. Busca híbrida: TF-IDF + BM25 + SBERT
3. Compreensão semântica real de queries
4. Cache de embeddings para performance

Autor: Wagner Approves Team
Versão: 3.0 (Semantic)
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
import string
import unicodedata
import os
import subprocess
import ast
from functools import lru_cache
import hashlib
import logging
import pickle
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download NLTK resources
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('averaged_perceptron_tagger_eng', quiet=True)

app = FastAPI(
    title="Wagner Approves API",
    description="Sistema de Recomendação de Filmes com Busca Semântica (SBERT)",
    version="3.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# CONFIGURAÇÕES E CONSTANTES
# =============================================================================

DATA_PATH = "data/processed_movies.csv"
PROCESSOR_SCRIPT = "backend/data_processor.py"
EMBEDDINGS_CACHE_PATH = "data/sbert_embeddings.pkl"

# Modelo SBERT (leve e eficiente)
SBERT_MODEL_NAME = "all-MiniLM-L6-v2"  # ~80MB, rápido e preciso

# Pesos para o sistema híbrido triplo
HYBRID_WEIGHTS = {
    'semantic': {        # Query semântica complexa
        'sbert': 0.50,   # SBERT domina
        'tfidf': 0.30,
        'bm25': 0.20
    },
    'person': {          # Busca por pessoa
        'sbert': 0.30,
        'tfidf': 0.50,
        'bm25': 0.20
    },
    'genre': {           # Busca por gênero
        'sbert': 0.40,
        'tfidf': 0.30,
        'bm25': 0.30
    },
    'general': {         # Busca geral
        'sbert': 0.40,
        'tfidf': 0.35,
        'bm25': 0.25
    }
}

# Pesos para re-ranking
RERANK_WEIGHTS = {
    'similarity': 0.60,
    'popularity': 0.15,
    'rating': 0.15,
    'confidence': 0.10
}

# Gêneros conhecidos
KNOWN_GENRES = [
    'action', 'adventure', 'animation', 'comedy', 'crime', 'documentary',
    'drama', 'family', 'fantasy', 'foreign', 'history', 'horror', 'music',
    'mystery', 'romance', 'science fiction', 'thriller', 'war', 'western'
]

# Palavras que indicam busca semântica complexa
SEMANTIC_INDICATORS = [
    'like', 'similar', 'about', 'where', 'when', 'story', 'plot',
    'feel', 'mood', 'vibe', 'style', 'theme', 'emotional', 'funny',
    'scary', 'sad', 'happy', 'exciting', 'boring', 'interesting'
]

# =============================================================================
# VARIÁVEIS GLOBAIS
# =============================================================================

df_movies = pd.DataFrame()
tfidf = None
tfidf_matrix = None
bm25 = None
tokenized_corpus = None
sbert_model = None
sbert_embeddings = None

# =============================================================================
# CLASSES E MODELOS
# =============================================================================

class RecommendationRequest(BaseModel):
    query: str
    algorithm: Optional[str] = "hybrid"  # "tfidf", "bm25", "sbert", "hybrid"
    top_n: Optional[int] = 10

class RecommendationResponse(BaseModel):
    movies: List[Dict]
    query_info: Dict
    algorithm_used: str

# =============================================================================
# PROCESSAMENTO DE TEXTO
# =============================================================================

lemmatizer = WordNetLemmatizer()

def get_wordnet_pos(tag: str) -> str:
    """Converte POS tag do Penn Treebank para formato WordNet"""
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    return wordnet.NOUN

def lemmatize_tokens(tokens: List[str]) -> List[str]:
    """Aplica lemmatização considerando POS tags"""
    if not tokens:
        return []
    try:
        pos_tags = pos_tag(tokens)
        return [lemmatizer.lemmatize(word, get_wordnet_pos(tag)) 
                for word, tag in pos_tags]
    except Exception as e:
        logger.warning(f"Erro na lemmatização: {e}")
        return tokens

def preprocess_text(text: str, use_lemmatization: bool = True) -> str:
    """Pré-processamento de texto para TF-IDF/BM25"""
    if not isinstance(text, str):
        return ""
    
    text = text.lower()
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    try:
        tokens = word_tokenize(text)
    except Exception:
        tokens = text.split()
    
    stop_words = set(stopwords.words('english'))
    tokens = [t for t in tokens if t not in stop_words and len(t) > 1]
    
    if use_lemmatization:
        tokens = lemmatize_tokens(tokens)
    
    return " ".join(tokens)

def detect_query_type(query: str) -> str:
    """Detecta o tipo de busca para ajustar pesos"""
    query_lower = query.lower()
    
    # Busca semântica complexa
    if any(ind in query_lower for ind in SEMANTIC_INDICATORS):
        return 'semantic'
    
    # Busca por pessoa
    person_keywords = ['directed by', 'starring', 'actor', 'actress', 'director', 
                       'with', 'featuring', 'played by']
    if any(kw in query_lower for kw in person_keywords):
        return 'person'
    
    # Busca por gênero
    if any(genre in query_lower for genre in KNOWN_GENRES):
        return 'genre'
    
    # Query longa geralmente é semântica
    if len(query.split()) > 4:
        return 'semantic'
    
    return 'general'

# =============================================================================
# CARREGAMENTO E PROCESSAMENTO DE DADOS
# =============================================================================

def load_sbert_model():
    """Carrega o modelo Sentence-BERT"""
    global sbert_model
    logger.info(f"Carregando modelo SBERT: {SBERT_MODEL_NAME}...")
    sbert_model = SentenceTransformer(SBERT_MODEL_NAME)
    logger.info("Modelo SBERT carregado com sucesso!")

def create_movie_text_for_sbert(row) -> str:
    """Cria texto descritivo do filme para embedding SBERT"""
    def get_str(val):
        if isinstance(val, list):
            return ", ".join(val)
        if isinstance(val, str) and val.startswith('['):
            try:
                items = ast.literal_eval(val)
                return ", ".join(items) if isinstance(items, list) else val
            except:
                return val
        return str(val) if val else ""

    title = str(row.get('title', ''))
    genre = get_str(row.get('genre', ''))
    description = str(row.get('description', ''))
    keywords = get_str(row.get('keywords', ''))
    director = str(row.get('director', ''))
    cast = get_str(row.get('cast', ''))
    
    # Formato mais natural para SBERT entender
    text = f"{title}. {description} Genres: {genre}. Keywords: {keywords}. Directed by {director}. Starring {cast}."
    
    return text

def generate_sbert_embeddings():
    """Gera embeddings SBERT para todos os filmes"""
    global sbert_embeddings
    
    # Verificar cache
    if os.path.exists(EMBEDDINGS_CACHE_PATH):
        logger.info("Carregando embeddings do cache...")
        try:
            with open(EMBEDDINGS_CACHE_PATH, 'rb') as f:
                cached_data = pickle.load(f)
                if cached_data.get('num_movies') == len(df_movies):
                    sbert_embeddings = cached_data['embeddings']
                    logger.info(f"Embeddings carregados do cache: {sbert_embeddings.shape}")
                    return
        except Exception as e:
            logger.warning(f"Erro ao carregar cache: {e}")
    
    # Gerar novos embeddings
    logger.info("Gerando embeddings SBERT para todos os filmes...")
    
    movie_texts = df_movies.apply(create_movie_text_for_sbert, axis=1).tolist()
    
    # Gera embeddings em batch para eficiência
    sbert_embeddings = sbert_model.encode(
        movie_texts,
        show_progress_bar=True,
        convert_to_numpy=True,
        batch_size=32
    )
    
    logger.info(f"Embeddings gerados: {sbert_embeddings.shape}")
    
    # Salvar cache
    try:
        Path(EMBEDDINGS_CACHE_PATH).parent.mkdir(parents=True, exist_ok=True)
        with open(EMBEDDINGS_CACHE_PATH, 'wb') as f:
            pickle.dump({
                'embeddings': sbert_embeddings,
                'num_movies': len(df_movies)
            }, f)
        logger.info("Embeddings salvos no cache!")
    except Exception as e:
        logger.warning(f"Erro ao salvar cache: {e}")

def load_data():
    """Carrega e processa os dados dos filmes"""
    global df_movies, tfidf, tfidf_matrix, bm25, tokenized_corpus
    
    if not os.path.exists(DATA_PATH):
        logger.info(f"Dados não encontrados em {DATA_PATH}. Executando processador...")
        try:
            subprocess.run(["python", PROCESSOR_SCRIPT], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao executar processador: {e}")

    try:
        df_movies = pd.read_csv(DATA_PATH)
        df_movies = df_movies.fillna('')
        logger.info(f"Carregados {len(df_movies)} filmes")
    except FileNotFoundError:
        logger.error("Arquivo de dados não encontrado")
        df_movies = pd.DataFrame()
        return

    # Criar features para TF-IDF/BM25
    df_movies['processed_features'] = df_movies.apply(create_combined_features, axis=1)
    
    # Inicializar TF-IDF
    tfidf = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=50000,
        min_df=2,
        max_df=0.95
    )
    tfidf_matrix = tfidf.fit_transform(df_movies['processed_features'])
    logger.info(f"TF-IDF matrix: {tfidf_matrix.shape}")
    
    # Inicializar BM25
    tokenized_corpus = [doc.split() for doc in df_movies['processed_features']]
    bm25 = BM25Okapi(tokenized_corpus)
    logger.info("BM25 inicializado")
    
    # Carregar SBERT e gerar embeddings
    load_sbert_model()
    generate_sbert_embeddings()

def create_combined_features(row) -> str:
    """Combina features para TF-IDF/BM25"""
    def get_str(val):
        if isinstance(val, list):
            return " ".join(val)
        if isinstance(val, str) and val.startswith('['):
            try:
                return " ".join(ast.literal_eval(val))
            except:
                return val
        return str(val) if val else ""

    genre_str = get_str(row.get('genre', ''))
    cast_str = get_str(row.get('cast', ''))
    keyword_str = get_str(row.get('keywords', ''))
    director_str = str(row.get('director', ''))
    title_str = str(row.get('title', ''))
    description_str = str(row.get('description', ''))
    
    features = [
        keyword_str * 6,
        title_str * 3,
        director_str * 3,
        cast_str * 2,
        genre_str * 2,
        description_str
    ]
    
    combined_text = " ".join(features)
    return preprocess_text(combined_text)

# =============================================================================
# ALGORITMOS DE SIMILARIDADE
# =============================================================================

def tfidf_similarity(query: str, top_n: int = 10) -> tuple:
    """Calcula similaridade usando TF-IDF + Cosine Similarity"""
    query_processed = preprocess_text(query)
    query_vec = tfidf.transform([query_processed])
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    return similarities

def bm25_similarity(query: str) -> np.ndarray:
    """Calcula similaridade usando BM25"""
    query_processed = preprocess_text(query)
    query_tokens = query_processed.split()
    scores = bm25.get_scores(query_tokens)
    return scores

def sbert_similarity(query: str) -> np.ndarray:
    """Calcula similaridade semântica usando Sentence-BERT"""
    # Gera embedding da query
    query_embedding = sbert_model.encode([query], convert_to_numpy=True)
    
    # Calcula similaridade cosseno com todos os filmes
    similarities = cosine_similarity(query_embedding, sbert_embeddings).flatten()
    
    return similarities

def normalize_scores(scores: np.ndarray) -> np.ndarray:
    """Normaliza scores para o intervalo [0, 1]"""
    min_s, max_s = scores.min(), scores.max()
    if max_s - min_s > 0:
        return (scores - min_s) / (max_s - min_s)
    return np.zeros_like(scores)

def hybrid_similarity(query: str, query_type: str, top_n: int = 10) -> tuple:
    """Combina TF-IDF, BM25 e SBERT com pesos dinâmicos"""
    weights = HYBRID_WEIGHTS.get(query_type, HYBRID_WEIGHTS['general'])
    
    # Obter scores de todos os algoritmos
    tfidf_scores = tfidf_similarity(query)
    bm25_scores = bm25_similarity(query)
    sbert_scores = sbert_similarity(query)
    
    # Normalizar
    tfidf_norm = normalize_scores(tfidf_scores)
    bm25_norm = normalize_scores(bm25_scores)
    sbert_norm = normalize_scores(sbert_scores)
    
    # Combinar com pesos
    combined_scores = (
        weights['tfidf'] * tfidf_norm +
        weights['bm25'] * bm25_norm +
        weights['sbert'] * sbert_norm
    )
    
    top_indices = combined_scores.argsort()[-top_n:][::-1]
    top_scores = combined_scores[top_indices]
    
    return top_indices, top_scores

# =============================================================================
# RE-RANKING
# =============================================================================

def calculate_popularity_boost(popularity: float) -> float:
    if popularity <= 0:
        return 0
    return min(np.log1p(popularity) / 10, 1.0)

def calculate_rating_boost(vote_average: float) -> float:
    if vote_average <= 0:
        return 0
    return vote_average / 10

def calculate_confidence(vote_count: int) -> float:
    return min(vote_count / 1000, 1.0)

def rerank_results(recommendations: List[Dict]) -> List[Dict]:
    """Re-ordena resultados considerando múltiplos fatores"""
    for rec in recommendations:
        base_score = rec.get('similarity_score', 0)
        
        popularity_boost = calculate_popularity_boost(rec.get('popularity', 0))
        rating_boost = calculate_rating_boost(rec.get('vote_average', 0))
        confidence = calculate_confidence(rec.get('vote_count', 0))
        
        final_score = (
            RERANK_WEIGHTS['similarity'] * base_score +
            RERANK_WEIGHTS['popularity'] * popularity_boost +
            RERANK_WEIGHTS['rating'] * rating_boost +
            RERANK_WEIGHTS['confidence'] * confidence
        )
        
        rec['final_score'] = float(final_score)
        rec['score'] = float(final_score)  # Para compatibilidade com frontend
        rec['score_breakdown'] = {
            'similarity': round(base_score, 4),
            'popularity_boost': round(popularity_boost, 4),
            'rating_boost': round(rating_boost, 4),
            'confidence': round(confidence, 4)
        }
    
    return sorted(recommendations, key=lambda x: x['final_score'], reverse=True)

# =============================================================================
# ENDPOINTS DA API
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Carrega dados na inicialização"""
    load_data()

@app.get("/")
def root():
    return {
        "message": "Wagner Approves API v3.0 (Semantic)",
        "features": [
            "Sentence-BERT para busca semântica",
            "Sistema híbrido TF-IDF + BM25 + SBERT",
            "Compreensão de queries complexas"
        ],
        "endpoints": {
            "/movies": "Lista filmes populares",
            "/genres": "Lista gêneros disponíveis",
            "/movies/by-genre/{genre}": "Filmes por gênero",
            "/recommend": "Recomendações semânticas (POST)",
            "/health": "Status da API"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "movies_loaded": len(df_movies) if not df_movies.empty else 0,
        "tfidf_ready": tfidf_matrix is not None,
        "bm25_ready": bm25 is not None,
        "sbert_ready": sbert_model is not None,
        "sbert_model": SBERT_MODEL_NAME,
        "embeddings_shape": sbert_embeddings.shape if sbert_embeddings is not None else None
    }

@app.get("/movies")
def get_movies():
    if df_movies.empty:
        return []
    return df_movies.nlargest(200, 'popularity').to_dict(orient="records")

@app.get("/genres")
def get_genres():
    if df_movies.empty:
        return []
    
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
    if df_movies.empty:
        return []
    
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
    
    filtered_df = pd.DataFrame(filtered_movies)
    if not filtered_df.empty:
        filtered_df = filtered_df.nlargest(limit, 'popularity')
        return filtered_df.to_dict(orient="records")
    
    return []

@app.post("/recommend")
def recommend(request: RecommendationRequest):
    """Endpoint principal de recomendação com busca semântica"""
    if df_movies.empty:
        raise HTTPException(status_code=500, detail="Dados não carregados")
    
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query não pode ser vazia")
    
    algorithm = request.algorithm
    top_n = min(request.top_n, 50)  # Limita a 50 resultados
    
    # Detectar tipo de query
    query_type = detect_query_type(query)
    
    logger.info(f"Query: '{query}' | Tipo: {query_type} | Algoritmo: {algorithm}")
    
    try:
        if algorithm == "tfidf":
            scores = tfidf_similarity(query)
            scores_norm = normalize_scores(scores)
            top_indices = scores_norm.argsort()[-top_n:][::-1]
            top_scores = scores_norm[top_indices]
            algorithm_used = "TF-IDF"
            
        elif algorithm == "bm25":
            scores = bm25_similarity(query)
            scores_norm = normalize_scores(scores)
            top_indices = scores_norm.argsort()[-top_n:][::-1]
            top_scores = scores_norm[top_indices]
            algorithm_used = "BM25"
            
        elif algorithm == "sbert":
            scores = sbert_similarity(query)
            top_indices = scores.argsort()[-top_n:][::-1]
            top_scores = scores[top_indices]
            algorithm_used = "Sentence-BERT"
            
        else:  # hybrid (default)
            top_indices, top_scores = hybrid_similarity(query, query_type, top_n)
            algorithm_used = f"Hybrid (TF-IDF + BM25 + SBERT) - {query_type}"
        
        # Construir resultados
        recommendations = []
        for idx, score in zip(top_indices, top_scores):
            movie = df_movies.iloc[idx].to_dict()
            movie['similarity_score'] = float(score)
            recommendations.append(movie)
        
        # Re-ranking
        recommendations = rerank_results(recommendations)
        
        # Pesos usados
        weights_used = HYBRID_WEIGHTS.get(query_type, HYBRID_WEIGHTS['general'])
        
        return {
            "movies": recommendations,
            "query_info": {
                "original_query": query,
                "query_type": query_type,
                "weights": weights_used
            },
            "algorithm_used": algorithm_used
        }
        
    except Exception as e:
        logger.error(f"Erro na recomendação: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# INICIALIZAÇÃO
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
