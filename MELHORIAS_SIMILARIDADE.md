# 🚀 Melhorias no Sistema de Similaridade - Guia Completo

## Índice

1. [Diagnóstico do Sistema Atual](#1-diagnóstico-do-sistema-atual)
2. [Melhorias no Pré-processamento de Texto](#2-melhorias-no-pré-processamento-de-texto)
3. [Algoritmos Avançados de Similaridade](#3-algoritmos-avançados-de-similaridade)
4. [Word Embeddings (Semântica Profunda)](#4-word-embeddings-semântica-profunda)
5. [Sistema Híbrido Multi-Algoritmo](#5-sistema-híbrido-multi-algoritmo)
6. [Otimização de Performance](#6-otimização-de-performance)
7. [Métricas de Qualidade](#7-métricas-de-qualidade)
8. [Implementação Recomendada](#8-implementação-recomendada)

---

## 1. Diagnóstico do Sistema Atual

### ✅ Pontos Fortes
- TF-IDF com bigramas (captura frases)
- Sistema de pesos por feature
- Pré-processamento básico (stopwords, lowercase)

### ❌ Limitações
| Problema | Impacto |
|----------|---------|
| TF-IDF não captura semântica | "carro" e "automóvel" são tratados como diferentes |
| Sem stemming/lemmatization | "running" e "run" são palavras diferentes |
| Pesos fixos | Não se adaptam ao contexto da busca |
| Sem expansão de query | Busca limitada aos termos exatos |
| Sem considerar popularidade no ranking | Filmes obscuros podem ter alta similaridade |

---

## 2. Melhorias no Pré-processamento de Texto

### 2.1 Lemmatization (Radical Semântico)

```python
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag

nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

lemmatizer = WordNetLemmatizer()

def get_wordnet_pos(tag):
    """Converte POS tag para formato WordNet"""
    if tag.startswith('J'):
        return 'a'  # Adjetivo
    elif tag.startswith('V'):
        return 'v'  # Verbo
    elif tag.startswith('N'):
        return 'n'  # Substantivo
    elif tag.startswith('R'):
        return 'r'  # Advérbio
    return 'n'

def lemmatize_text(tokens):
    """Aplica lemmatização considerando POS tags"""
    pos_tags = pos_tag(tokens)
    return [lemmatizer.lemmatize(word, get_wordnet_pos(tag)) 
            for word, tag in pos_tags]
```

**Exemplo:**
| Original | Stemming | Lemmatization |
|----------|----------|---------------|
| running | runn | run |
| better | better | good |
| movies | movi | movie |

### 2.2 Spell Correction (Correção Ortográfica)

```python
from spellchecker import SpellChecker

spell = SpellChecker()

def correct_spelling(text):
    """Corrige erros de digitação na query"""
    words = text.split()
    corrected = []
    for word in words:
        correction = spell.correction(word)
        corrected.append(correction if correction else word)
    return " ".join(corrected)
```

### 2.3 Synonym Expansion (Expansão por Sinônimos)

```python
from nltk.corpus import wordnet

def get_synonyms(word, max_synonyms=3):
    """Retorna sinônimos de uma palavra"""
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            if lemma.name() != word:
                synonyms.add(lemma.name().replace('_', ' '))
            if len(synonyms) >= max_synonyms:
                break
    return list(synonyms)

def expand_query(query):
    """Expande a query com sinônimos"""
    words = query.split()
    expanded = words.copy()
    for word in words:
        synonyms = get_synonyms(word)
        expanded.extend(synonyms)
    return " ".join(expanded)
```

**Exemplo:**
```
Query: "scary movie"
Expandida: "scary movie frightening film horror picture"
```

---

## 3. Algoritmos Avançados de Similaridade

### 3.1 BM25 (Best Matching 25)

BM25 é uma evolução do TF-IDF que considera:
- **Saturação de frequência**: Limita o impacto de termos muito frequentes
- **Normalização por tamanho**: Documentos longos não são penalizados

```python
from rank_bm25 import BM25Okapi

# Tokenizar documentos
tokenized_corpus = [doc.split() for doc in df_movies['processed_features']]

# Criar índice BM25
bm25 = BM25Okapi(tokenized_corpus)

def bm25_search(query, top_n=10):
    tokenized_query = query.split()
    scores = bm25.get_scores(tokenized_query)
    top_indices = scores.argsort()[-top_n:][::-1]
    return top_indices, scores[top_indices]
```

**Fórmula BM25:**

$$BM25(D, Q) = \sum_{i=1}^{n} IDF(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot (1 - b + b \cdot \frac{|D|}{avgdl})}$$

Onde:
- $k_1 = 1.5$ (saturação de frequência)
- $b = 0.75$ (normalização por tamanho)
- $avgdl$ = tamanho médio dos documentos

### 3.2 Jaccard Similarity (Para Conjuntos)

Útil para comparar gêneros, keywords e tags:

```python
def jaccard_similarity(set1, set2):
    """Similaridade de Jaccard entre dois conjuntos"""
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0
```

### 3.3 Soft Cosine Similarity

Considera similaridade entre palavras (não apenas igualdade):

```python
from gensim.similarities import SoftCosineSimilarity
from gensim.models import Word2Vec

# Treinar modelo Word2Vec ou usar pré-treinado
model = Word2Vec(sentences, vector_size=100, window=5, min_count=1)

# Criar matriz de similaridade entre termos
similarity_matrix = model.wv.similarity_matrix(dictionary)

# Calcular Soft Cosine
soft_cosine_sim = SoftCosineSimilarity(tfidf_corpus, similarity_matrix)
```

---

## 4. Word Embeddings (Semântica Profunda)

### 4.1 Word2Vec / FastText

Representação vetorial que captura relações semânticas:

```python
import gensim.downloader as api

# Carregar modelo pré-treinado (300 dimensões)
word2vec_model = api.load('word2vec-google-news-300')

def get_document_embedding(text, model):
    """Calcula embedding médio de um documento"""
    words = text.split()
    embeddings = []
    for word in words:
        if word in model:
            embeddings.append(model[word])
    if embeddings:
        return np.mean(embeddings, axis=0)
    return np.zeros(model.vector_size)
```

### 4.2 Sentence Transformers (Estado da Arte)

Embeddings de frases completas com modelos transformer:

```python
from sentence_transformers import SentenceTransformer

# Modelo multilíngue de alta qualidade
model = SentenceTransformer('all-MiniLM-L6-v2')

# Gerar embeddings para todos os filmes
movie_descriptions = df_movies['description'].tolist()
movie_embeddings = model.encode(movie_descriptions)

def semantic_search(query, top_n=10):
    query_embedding = model.encode([query])
    similarities = cosine_similarity(query_embedding, movie_embeddings)[0]
    top_indices = similarities.argsort()[-top_n:][::-1]
    return top_indices, similarities[top_indices]
```

**Vantagens:**
- Captura contexto e significado
- "Filme de terror espacial" encontra "Alien" mesmo sem palavras em comum
- Modelos pré-treinados em bilhões de textos

### 4.3 Comparação de Abordagens

| Método | Semântica | Velocidade | Recursos |
|--------|-----------|------------|----------|
| TF-IDF | ❌ Lexical | ⚡ Muito rápido | 💾 Baixo |
| BM25 | ❌ Lexical | ⚡ Muito rápido | 💾 Baixo |
| Word2Vec | ✅ Palavras | ⚡ Rápido | 💾 Médio |
| Sentence-BERT | ✅✅ Frases | 🐢 Moderado | 💾 Alto |

---

## 5. Sistema Híbrido Multi-Algoritmo

### 5.1 Ensemble de Similaridades

Combinar múltiplos algoritmos para resultado mais robusto:

```python
class HybridRecommender:
    def __init__(self, df_movies):
        self.df = df_movies
        
        # Inicializar múltiplos modelos
        self.tfidf = TfidfVectorizer(ngram_range=(1, 2))
        self.tfidf_matrix = self.tfidf.fit_transform(df_movies['processed_features'])
        
        self.bm25 = BM25Okapi([doc.split() for doc in df_movies['processed_features']])
        
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.semantic_embeddings = self.sentence_model.encode(
            df_movies['description'].tolist()
        )
    
    def recommend(self, query, weights=None):
        if weights is None:
            weights = {
                'tfidf': 0.3,
                'bm25': 0.3,
                'semantic': 0.4
            }
        
        # TF-IDF Score
        query_vec = self.tfidf.transform([preprocess_text(query)])
        tfidf_scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # BM25 Score
        bm25_scores = self.bm25.get_scores(query.split())
        
        # Semantic Score
        query_emb = self.sentence_model.encode([query])
        semantic_scores = cosine_similarity(query_emb, self.semantic_embeddings)[0]
        
        # Normalizar scores (0-1)
        tfidf_norm = self._normalize(tfidf_scores)
        bm25_norm = self._normalize(bm25_scores)
        semantic_norm = self._normalize(semantic_scores)
        
        # Combinar com pesos
        final_scores = (
            weights['tfidf'] * tfidf_norm +
            weights['bm25'] * bm25_norm +
            weights['semantic'] * semantic_norm
        )
        
        return final_scores
    
    def _normalize(self, scores):
        min_s, max_s = scores.min(), scores.max()
        if max_s - min_s > 0:
            return (scores - min_s) / (max_s - min_s)
        return scores
```

### 5.2 Pesos Dinâmicos por Tipo de Query

```python
def detect_query_type(query):
    """Detecta o tipo de busca para ajustar pesos"""
    query_lower = query.lower()
    
    # Busca por pessoa (diretor/ator)
    if any(word in query_lower for word in ['directed by', 'starring', 'actor', 'director']):
        return 'person'
    
    # Busca por gênero
    genres = ['action', 'comedy', 'drama', 'horror', 'romance', 'thriller']
    if any(genre in query_lower for genre in genres):
        return 'genre'
    
    # Busca descritiva/temática
    if len(query.split()) > 5:
        return 'descriptive'
    
    return 'general'

def get_dynamic_weights(query_type):
    weights = {
        'person': {'tfidf': 0.6, 'bm25': 0.3, 'semantic': 0.1},
        'genre': {'tfidf': 0.4, 'bm25': 0.4, 'semantic': 0.2},
        'descriptive': {'tfidf': 0.2, 'bm25': 0.2, 'semantic': 0.6},
        'general': {'tfidf': 0.33, 'bm25': 0.33, 'semantic': 0.34}
    }
    return weights.get(query_type, weights['general'])
```

### 5.3 Re-ranking com Fatores Adicionais

```python
def rerank_results(recommendations, df_movies):
    """Reordena resultados considerando fatores adicionais"""
    for rec in recommendations:
        base_score = rec['score']
        
        # Boost por popularidade (log scale para não dominar)
        popularity_boost = np.log1p(rec['popularity']) / 10
        
        # Boost por avaliação
        rating_boost = rec['vote_average'] / 20  # 0 a 0.5
        
        # Penalidade por poucos votos (baixa confiança)
        vote_confidence = min(rec['vote_count'] / 1000, 1)
        
        # Score final
        rec['final_score'] = (
            base_score * 0.6 +
            popularity_boost * 0.15 +
            rating_boost * 0.15 +
            vote_confidence * 0.1
        )
    
    return sorted(recommendations, key=lambda x: x['final_score'], reverse=True)
```

---

## 6. Otimização de Performance

### 6.1 Indexação com FAISS (Facebook AI)

Para busca ultrarrápida em milhões de vetores:

```python
import faiss

# Criar índice FAISS
dimension = movie_embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)  # Inner Product (para cosine sim com vetores normalizados)

# Normalizar e adicionar vetores
faiss.normalize_L2(movie_embeddings)
index.add(movie_embeddings)

# Busca (retorna top-k em milissegundos)
def fast_search(query_embedding, k=10):
    faiss.normalize_L2(query_embedding)
    distances, indices = index.search(query_embedding, k)
    return indices[0], distances[0]
```

### 6.2 Cache de Resultados

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def cached_recommend(query_hash):
    # Busca em cache
    return recommendations

def recommend_with_cache(query):
    query_hash = hashlib.md5(query.lower().encode()).hexdigest()
    return cached_recommend(query_hash)
```

### 6.3 Pré-computação de Embeddings

```python
# Na inicialização do servidor
print("Pré-computando embeddings...")
movie_embeddings = model.encode(
    df_movies['description'].tolist(),
    show_progress_bar=True,
    batch_size=64
)
np.save('embeddings_cache.npy', movie_embeddings)

# No reload
if os.path.exists('embeddings_cache.npy'):
    movie_embeddings = np.load('embeddings_cache.npy')
```

---

## 7. Métricas de Qualidade

### 7.1 Métricas de Avaliação

```python
def precision_at_k(relevant, recommended, k):
    """Precisão nos top-k resultados"""
    recommended_k = recommended[:k]
    relevant_recommended = len(set(relevant) & set(recommended_k))
    return relevant_recommended / k

def recall_at_k(relevant, recommended, k):
    """Recall nos top-k resultados"""
    recommended_k = recommended[:k]
    relevant_recommended = len(set(relevant) & set(recommended_k))
    return relevant_recommended / len(relevant) if relevant else 0

def ndcg_at_k(relevant, recommended, k):
    """Normalized Discounted Cumulative Gain"""
    dcg = sum([1 / np.log2(i + 2) for i, r in enumerate(recommended[:k]) if r in relevant])
    idcg = sum([1 / np.log2(i + 2) for i in range(min(len(relevant), k))])
    return dcg / idcg if idcg > 0 else 0

def mean_reciprocal_rank(relevant, recommended):
    """Posição média do primeiro resultado relevante"""
    for i, r in enumerate(recommended):
        if r in relevant:
            return 1 / (i + 1)
    return 0
```

### 7.2 A/B Testing Framework

```python
import random

class ABTest:
    def __init__(self, algorithms):
        self.algorithms = algorithms
        self.results = {name: [] for name in algorithms}
    
    def get_algorithm(self, user_id):
        """Atribui algoritmo consistente por usuário"""
        random.seed(user_id)
        return random.choice(list(self.algorithms.keys()))
    
    def log_interaction(self, algorithm, user_clicked):
        self.results[algorithm].append(user_clicked)
    
    def get_ctr(self, algorithm):
        """Click-Through Rate"""
        results = self.results[algorithm]
        return sum(results) / len(results) if results else 0
```

---

## 8. Implementação Recomendada

### Fase 1: Melhorias Imediatas (Baixo Esforço, Alto Impacto)

1. ✅ **Adicionar Lemmatization**
2. ✅ **Implementar BM25 como alternativa**
3. ✅ **Re-ranking com popularidade e rating**
4. ✅ **Cache de queries frequentes**

### Fase 2: Melhorias Intermediárias

5. 🔄 **Sentence Transformers para busca semântica**
6. 🔄 **Sistema híbrido com pesos dinâmicos**
7. 🔄 **Expansão de query com sinônimos**

### Fase 3: Melhorias Avançadas

8. 🔜 **FAISS para indexação rápida**
9. 🔜 **A/B testing para otimização contínua**
10. 🔜 **Personalização por histórico do usuário**

---

## Código de Implementação Completa

Veja o arquivo `backend/main_enhanced.py` para a implementação completa das melhorias da Fase 1.

---

## Referências

1. Robertson, S., & Zaragoza, H. (2009). The Probabilistic Relevance Framework: BM25 and Beyond.
2. Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks.
3. Johnson, J., Douze, M., & Jégou, H. (2019). Billion-scale similarity search with GPUs (FAISS).
4. Mikolov, T., et al. (2013). Distributed Representations of Words and Phrases (Word2Vec).
