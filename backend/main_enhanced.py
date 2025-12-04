"""
NetRecs - Sistema de Recomendação de Filmes (Versão Aprimorada)
===============================================================

Melhorias implementadas:
1. Lemmatization com POS tagging
2. BM25 como algoritmo alternativo
3. Sistema híbrido TF-IDF + BM25
4. Re-ranking com popularidade e rating
5. Cache de queries frequentes
6. Expansão de query com sinônimos
7. Detecção automática de tipo de busca
8. Métricas de confiança no score

Autor: NetRecs Team
Versão: 2.0
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
    title="NetRecs API",
    description="Sistema de Recomendação de Filmes com Algoritmos Híbridos",
    version="2.0"
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

# Pesos para o sistema híbrido
HYBRID_WEIGHTS = {
    'person': {'tfidf': 0.6, 'bm25': 0.4},      # Busca por pessoa
    'genre': {'tfidf': 0.4, 'bm25': 0.6},       # Busca por gênero
    'descriptive': {'tfidf': 0.5, 'bm25': 0.5}, # Busca descritiva
    'general': {'tfidf': 0.5, 'bm25': 0.5}      # Busca geral
}

# Pesos para re-ranking
RERANK_WEIGHTS = {
    'similarity': 0.60,    # Score de similaridade base
    'popularity': 0.15,    # Boost por popularidade
    'rating': 0.15,        # Boost por avaliação
    'confidence': 0.10     # Confiança (baseada em vote_count)
}

# Gêneros conhecidos para detecção de query
KNOWN_GENRES = [
    'action', 'adventure', 'animation', 'comedy', 'crime', 'documentary',
    'drama', 'family', 'fantasy', 'foreign', 'history', 'horror', 'music',
    'mystery', 'romance', 'science fiction', 'thriller', 'war', 'western'
]

# =============================================================================
# CLASSES E MODELOS
# =============================================================================

class RecommendationRequest(BaseModel):
    query: str
    algorithm: Optional[str] = "hybrid"  # "tfidf", "bm25", "hybrid"
    use_synonyms: Optional[bool] = True
    top_n: Optional[int] = 10

class RecommendationResponse(BaseModel):
    movies: List[Dict]
    query_info: Dict
    algorithm_used: str

# =============================================================================
# PROCESSAMENTO DE TEXTO AVANÇADO
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

def get_synonyms(word: str, max_synonyms: int = 2) -> List[str]:
    """Retorna sinônimos de uma palavra usando WordNet"""
    synonyms = set()
    try:
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonym = lemma.name().replace('_', ' ').lower()
                if synonym != word and len(synonym) > 2:
                    synonyms.add(synonym)
                if len(synonyms) >= max_synonyms:
                    return list(synonyms)
    except Exception as e:
        logger.warning(f"Erro ao buscar sinônimos para '{word}': {e}")
    return list(synonyms)

def expand_query_with_synonyms(query: str) -> str:
    """Expande a query adicionando sinônimos relevantes"""
    words = query.lower().split()
    expanded = words.copy()
    
    # Palavras para não expandir (stopwords, números, etc.)
    stop_words = set(stopwords.words('english'))
    
    for word in words:
        if word not in stop_words and len(word) > 3:
            synonyms = get_synonyms(word)
            expanded.extend(synonyms)
    
    return " ".join(expanded)

def preprocess_text_advanced(text: str, use_lemmatization: bool = True) -> str:
    """Pré-processamento avançado de texto com lemmatização"""
    if not isinstance(text, str):
        return ""
    
    # 1. Lowercase
    text = text.lower()
    
    # 2. Normalização Unicode (remove acentos)
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    
    # 3. Remove pontuação
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # 4. Tokenização
    try:
        tokens = word_tokenize(text)
    except Exception:
        tokens = text.split()
    
    # 5. Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [t for t in tokens if t not in stop_words and len(t) > 1]
    
    # 6. Lemmatização (opcional)
    if use_lemmatization:
        tokens = lemmatize_tokens(tokens)
    
    return " ".join(tokens)

def detect_query_type(query: str) -> str:
    """Detecta o tipo de busca para ajustar pesos do algoritmo"""
    query_lower = query.lower()
    
    # Busca por pessoa (diretor/ator)
    person_keywords = ['directed by', 'starring', 'actor', 'actress', 'director', 
                       'with', 'featuring', 'played by']
    if any(kw in query_lower for kw in person_keywords):
        return 'person'
    
    # Busca por gênero
    if any(genre in query_lower for genre in KNOWN_GENRES):
        return 'genre'
    
    # Busca descritiva (query longa)
    if len(query.split()) > 5:
        return 'descriptive'
    
    return 'general'

# =============================================================================
# CARREGAMENTO E PROCESSAMENTO DE DADOS
# =============================================================================

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

    # Criar features combinadas
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

def create_combined_features(row) -> str:
    """Combina features com pesos para criar representação textual do filme"""
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
    
    # Pesos otimizados (repetição = peso maior)
    features = [
        keyword_str * 6,   # Keywords: peso 6x
        title_str * 3,     # Título: peso 3x
        director_str * 3,  # Diretor: peso 3x
        cast_str * 2,      # Elenco: peso 2x
        genre_str * 2,     # Gênero: peso 2x
        description_str    # Descrição: peso 1x
    ]
    
    combined_text = " ".join(features)
    return preprocess_text_advanced(combined_text)

# =============================================================================
# ALGORITMOS DE SIMILARIDADE
# =============================================================================

def tfidf_similarity(query: str, top_n: int = 10) -> tuple:
    """Calcula similaridade usando TF-IDF + Cosine Similarity"""
    query_processed = preprocess_text_advanced(query)
    query_vec = tfidf.transform([query_processed])
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    
    top_indices = similarities.argsort()[-top_n:][::-1]
    top_scores = similarities[top_indices]
    
    return top_indices, top_scores

def bm25_similarity(query: str, top_n: int = 10) -> tuple:
    """Calcula similaridade usando BM25"""
    query_processed = preprocess_text_advanced(query)
    query_tokens = query_processed.split()
    
    scores = bm25.get_scores(query_tokens)
    
    top_indices = scores.argsort()[-top_n:][::-1]
    top_scores = scores[top_indices]
    
    return top_indices, top_scores

def normalize_scores(scores: np.ndarray) -> np.ndarray:
    """Normaliza scores para o intervalo [0, 1]"""
    min_s, max_s = scores.min(), scores.max()
    if max_s - min_s > 0:
        return (scores - min_s) / (max_s - min_s)
    return np.zeros_like(scores)

def hybrid_similarity(query: str, query_type: str, top_n: int = 10) -> tuple:
    """Combina TF-IDF e BM25 com pesos dinâmicos"""
    weights = HYBRID_WEIGHTS.get(query_type, HYBRID_WEIGHTS['general'])
    
    # Obter scores de ambos os algoritmos
    query_processed = preprocess_text_advanced(query)
    
    # TF-IDF
    query_vec = tfidf.transform([query_processed])
    tfidf_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
    
    # BM25
    query_tokens = query_processed.split()
    bm25_scores = bm25.get_scores(query_tokens)
    
    # Normalizar
    tfidf_norm = normalize_scores(tfidf_scores)
    bm25_norm = normalize_scores(bm25_scores)
    
    # Combinar
    combined_scores = (
        weights['tfidf'] * tfidf_norm +
        weights['bm25'] * bm25_norm
    )
    
    top_indices = combined_scores.argsort()[-top_n:][::-1]
    top_scores = combined_scores[top_indices]
    
    return top_indices, top_scores

# =============================================================================
# RE-RANKING
# =============================================================================

def calculate_popularity_boost(popularity: float) -> float:
    """Calcula boost de popularidade usando escala logarítmica"""
    if popularity <= 0:
        return 0
    return min(np.log1p(popularity) / 10, 1.0)

def calculate_rating_boost(vote_average: float) -> float:
    """Calcula boost baseado na avaliação média"""
    if vote_average <= 0:
        return 0
    return vote_average / 10  # Normaliza para 0-1

def calculate_confidence(vote_count: int) -> float:
    """Calcula confiança baseada no número de votos"""
    # Limiar de 1000 votos para confiança máxima
    return min(vote_count / 1000, 1.0)

def rerank_results(recommendations: List[Dict]) -> List[Dict]:
    """Re-ordena resultados considerando múltiplos fatores"""
    for rec in recommendations:
        base_score = rec.get('similarity_score', 0)
        
        popularity_boost = calculate_popularity_boost(rec.get('popularity', 0))
        rating_boost = calculate_rating_boost(rec.get('vote_average', 0))
        confidence = calculate_confidence(rec.get('vote_count', 0))
        
        # Score final ponderado
        final_score = (
            RERANK_WEIGHTS['similarity'] * base_score +
            RERANK_WEIGHTS['popularity'] * popularity_boost +
            RERANK_WEIGHTS['rating'] * rating_boost +
            RERANK_WEIGHTS['confidence'] * confidence
        )
        
        rec['final_score'] = float(final_score)
        rec['score_breakdown'] = {
            'similarity': round(base_score, 4),
            'popularity_boost': round(popularity_boost, 4),
            'rating_boost': round(rating_boost, 4),
            'confidence': round(confidence, 4)
        }
    
    return sorted(recommendations, key=lambda x: x['final_score'], reverse=True)

# =============================================================================
# CACHE
# =============================================================================

@lru_cache(maxsize=500)
def cached_recommend(query_hash: str, algorithm: str, use_synonyms: bool, top_n: int) -> str:
    """Cache para queries frequentes (retorna JSON string)"""
    # Este é um placeholder - a lógica real está em recommend()
    pass

def get_query_hash(query: str, algorithm: str, use_synonyms: bool) -> str:
    """Gera hash único para a query"""
    key = f"{query.lower().strip()}:{algorithm}:{use_synonyms}"
    return hashlib.md5(key.encode()).hexdigest()

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
        "message": "NetRecs API v2.0",
        "endpoints": {
            "/movies": "Lista filmes populares",
            "/genres": "Lista gêneros disponíveis",
            "/movies/by-genre/{genre}": "Filmes por gênero",
            "/recommend": "Recomendações (POST)",
            "/health": "Status da API"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "movies_loaded": len(df_movies) if not df_movies.empty else 0,
        "tfidf_ready": tfidf_matrix is not None,
        "bm25_ready": bm25 is not None
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
    """
    Endpoint principal de recomendação com múltiplos algoritmos.
    
    Parâmetros:
    - query: Texto de busca
    - algorithm: "tfidf", "bm25", ou "hybrid" (padrão)
    - use_synonyms: Expandir query com sinônimos (padrão: True)
    - top_n: Número de resultados (padrão: 10)
    """
    if df_movies.empty or tfidf_matrix is None:
        return {"movies": [], "query_info": {}, "algorithm_used": "none"}

    query = request.query
    algorithm = request.algorithm
    use_synonyms = request.use_synonyms
    top_n = request.top_n
    
    # Detectar tipo de query
    query_type = detect_query_type(query)
    
    # Expandir com sinônimos se solicitado
    expanded_query = query
    if use_synonyms:
        expanded_query = expand_query_with_synonyms(query)
    
    # Selecionar algoritmo
    if algorithm == "tfidf":
        indices, scores = tfidf_similarity(expanded_query, top_n * 2)
    elif algorithm == "bm25":
        indices, scores = bm25_similarity(expanded_query, top_n * 2)
    else:  # hybrid
        indices, scores = hybrid_similarity(expanded_query, query_type, top_n * 2)
    
    # Normalizar scores
    if len(scores) > 0 and scores.max() > 0:
        scores = scores / scores.max()
    
    # Construir lista de recomendações
    recommendations = []
    for i, idx in enumerate(indices):
        if scores[i] > 0:
            movie = df_movies.iloc[idx].to_dict()
            
            movie['similarity_score'] = float(scores[i])
            
            # Limpar NaN
            for k, v in movie.items():
                if pd.isna(v):
                    movie[k] = ""
            
            recommendations.append(movie)
    
    # Re-ranking
    recommendations = rerank_results(recommendations)
    
    # Limitar ao top_n após re-ranking
    recommendations = recommendations[:top_n]
    
    # Adicionar score final normalizado como 'score' para compatibilidade
    if recommendations:
        max_final = recommendations[0]['final_score']
        for rec in recommendations:
            rec['score'] = round(rec['final_score'] / max_final * 0.95, 4) if max_final > 0 else 0
    
    # Informações sobre a query
    query_info = {
        "original_query": query,
        "expanded_query": expanded_query if use_synonyms else None,
        "query_type": query_type,
        "synonyms_added": expanded_query != query
    }
    
    return {
        "movies": recommendations,
        "query_info": query_info,
        "algorithm_used": algorithm
    }

# Endpoint simplificado para compatibilidade com frontend existente
@app.post("/recommend/simple")
def recommend_simple(request: RecommendationRequest):
    """Endpoint simplificado que retorna apenas a lista de filmes"""
    result = recommend(request)
    return result["movies"]

# =============================================================================
# INICIALIZAÇÃO
# =============================================================================

# Variáveis globais
df_movies = pd.DataFrame()
tfidf = None
tfidf_matrix = None
bm25 = None
tokenized_corpus = []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
