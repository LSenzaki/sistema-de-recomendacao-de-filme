# 🎬 NetRecs - Sistema de Recomendação de Filmes

## Guia Completo para Apresentação

---

## 📋 Índice

1. [Visão Geral do Projeto](#1-visão-geral-do-projeto)
2. [Arquitetura do Sistema](#2-arquitetura-do-sistema)
3. [Fluxo de Dados](#3-fluxo-de-dados)
4. [Algoritmos e Cálculos Matemáticos](#4-algoritmos-e-cálculos-matemáticos)
5. [Processamento de Linguagem Natural (NLP)](#5-processamento-de-linguagem-natural-nlp)
6. [API RESTful](#6-api-restful)
7. [Frontend](#7-frontend)
8. [Tecnologias Utilizadas](#8-tecnologias-utilizadas)
9. [Como Executar](#9-como-executar)
10. [Demonstração Prática](#10-demonstração-prática)

---

## 1. Visão Geral do Projeto

### O que é o NetRecs?

O **NetRecs** é um sistema de recomendação de filmes baseado em **conteúdo** (Content-Based Filtering). Diferente de sistemas colaborativos que usam preferências de outros usuários, nosso sistema analisa as **características intrínsecas** dos filmes para encontrar similaridades.

### Problema que Resolve

- Usuários têm dificuldade em encontrar filmes similares aos que gostam
- Catálogos de streaming são muito extensos para navegação manual
- Necessidade de recomendações personalizadas baseadas em preferências específicas

### Solução Proposta

Sistema que permite:
- Busca por palavras-chave (gênero, diretor, ator, tema)
- Navegação por categorias/gêneros
- Recomendações baseadas em similaridade de conteúdo
- Score de correspondência (% de match)

---

## 2. Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        ARQUITETURA                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    HTTP/REST    ┌──────────────────────────┐  │
│  │   FRONTEND   │ ◄─────────────► │        BACKEND           │  │
│  │  (HTML/CSS/  │                 │       (FastAPI)          │  │
│  │  JavaScript) │                 │                          │  │
│  └──────────────┘                 │  ┌────────────────────┐  │  │
│                                   │  │   TF-IDF Engine    │  │  │
│                                   │  │  + Cosine Simil.   │  │  │
│                                   │  └────────────────────┘  │  │
│                                   │           │              │  │
│                                   │           ▼              │  │
│                                   │  ┌────────────────────┐  │  │
│                                   │  │   Pandas + NLTK    │  │  │
│                                   │  │  (Processamento)   │  │  │
│                                   │  └────────────────────┘  │  │
│                                   └──────────────────────────┘  │
│                                              │                   │
│                                              ▼                   │
│                                   ┌──────────────────────────┐  │
│                                   │     DATA LAYER           │  │
│                                   │  processed_movies.csv    │  │
│                                   │  (TMDB Dataset)          │  │
│                                   └──────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Componentes Principais

| Componente | Tecnologia | Responsabilidade |
|------------|------------|------------------|
| Frontend | HTML/CSS/JS | Interface do usuário |
| Backend | FastAPI (Python) | API REST, lógica de negócio |
| Motor de Recomendação | Scikit-learn | TF-IDF + Similaridade |
| Processamento de Texto | NLTK | Tokenização, stopwords |
| Dados | Pandas/CSV | Armazenamento e manipulação |

---

## 3. Fluxo de Dados

### 3.1 Pipeline de Processamento de Dados

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ movies_metadata │     │    credits      │     │    keywords     │
│     .csv        │     │     .csv        │     │     .csv        │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   data_processor.py    │
                    │                        │
                    │  • Merge por ID        │
                    │  • Parse JSON          │
                    │  • Extrai features     │
                    │  • Filtra qualidade    │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  processed_movies.csv  │
                    │                        │
                    │  Campos:               │
                    │  - id, title           │
                    │  - description         │
                    │  - genre, cast         │
                    │  - director, keywords  │
                    │  - image_url           │
                    │  - vote_average        │
                    │  - popularity          │
                    └────────────────────────┘
```

### 3.2 Fluxo de Recomendação

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Query do   │────►│ Pré-process. │────►│ Vetorização     │
│  Usuário    │     │ do Texto     │     │ TF-IDF          │
└─────────────┘     └──────────────┘     └────────┬────────┘
                                                  │
                                                  ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│ Top 10      │◄────│ Ordenação    │◄────│ Similaridade    │
│ Filmes      │     │ por Score    │     │ do Cosseno      │
└─────────────┘     └──────────────┘     └─────────────────┘
```

---

## 4. Algoritmos e Cálculos Matemáticos

### 4.1 TF-IDF (Term Frequency - Inverse Document Frequency)

O TF-IDF é uma técnica estatística que avalia a **importância de uma palavra** em um documento dentro de uma coleção.

#### Fórmula Matemática

$$TF\text{-}IDF(t, d, D) = TF(t, d) \times IDF(t, D)$$

Onde:

**Term Frequency (TF)** - Frequência do termo no documento:
$$TF(t, d) = \frac{\text{Número de vezes que } t \text{ aparece em } d}{\text{Total de termos em } d}$$

**Inverse Document Frequency (IDF)** - Raridade do termo na coleção:
$$IDF(t, D) = \log\left(\frac{N}{1 + |\{d \in D : t \in d\}|}\right)$$

Onde:
- $t$ = termo (palavra)
- $d$ = documento (filme)
- $D$ = coleção de documentos (todos os filmes)
- $N$ = número total de documentos

#### Exemplo Prático

| Termo | TF (Filme A) | IDF | TF-IDF |
|-------|--------------|-----|--------|
| "ação" | 0.05 | 0.3 | 0.015 |
| "vingadores" | 0.02 | 2.5 | 0.050 |
| "marvel" | 0.03 | 1.8 | 0.054 |

**Interpretação**: Palavras comuns (como "ação") têm baixo IDF, enquanto palavras específicas (como "vingadores") têm alto IDF, tornando-as mais importantes na busca.

### 4.2 Similaridade do Cosseno (Cosine Similarity)

Mede o ângulo entre dois vetores no espaço n-dimensional. Quanto menor o ângulo, mais similares os vetores.

#### Fórmula Matemática

$$\text{similarity}(\vec{A}, \vec{B}) = \cos(\theta) = \frac{\vec{A} \cdot \vec{B}}{||\vec{A}|| \times ||\vec{B}||}$$

Expandindo:

$$\cos(\theta) = \frac{\sum_{i=1}^{n} A_i \times B_i}{\sqrt{\sum_{i=1}^{n} A_i^2} \times \sqrt{\sum_{i=1}^{n} B_i^2}}$$

#### Visualização Geométrica

```
                    │ 
           B ──────►│     A (vetor do filme)
              θ     │    /
               \    │   /
                \   │  /
                 \  │ /
                  \ │/
    ───────────────┼───────────────
                   │
                   │  Q (vetor da query)
                   │ /
                   │/
                   ▼
```

#### Interpretação dos Valores

| Valor | Significado |
|-------|-------------|
| 1.0 | Vetores idênticos (100% similar) |
| 0.0 | Vetores ortogonais (sem relação) |
| -1.0 | Vetores opostos (não ocorre em TF-IDF pois valores são ≥ 0) |

#### Exemplo Numérico

```
Query: "filme de ação com super-heróis"
Vetor Query:  [0.5, 0.8, 0.0, 0.3, 0.6]  (após TF-IDF)

Filme A (Vingadores):  [0.6, 0.9, 0.1, 0.4, 0.7]
Filme B (Titanic):     [0.1, 0.0, 0.8, 0.2, 0.1]

Similaridade(Query, A) = 0.98  →  98% match
Similaridade(Query, B) = 0.21  →  21% match
```

### 4.3 Sistema de Pesos (Feature Weighting)

O sistema aplica **pesos diferentes** para cada característica do filme:

```python
features = [
    keyword_str * 6,   # Keywords: peso 6x (MAIOR PRIORIDADE)
    title * 3,         # Título: peso 3x
    director * 3,      # Diretor: peso 3x
    cast * 2,          # Elenco: peso 2x
    genre * 2,         # Gênero: peso 2x
    description * 1    # Descrição: peso 1x
]
```

#### Por que esses pesos?

| Feature | Peso | Justificativa |
|---------|------|---------------|
| Keywords | 6x | Tags específicas são altamente relevantes |
| Título | 3x | Identifica diretamente o filme |
| Diretor | 3x | Estilo autoral influencia fortemente |
| Elenco | 2x | Atores indicam tipo de filme |
| Gênero | 2x | Categorização básica importante |
| Descrição | 1x | Texto longo, muitas palavras genéricas |

### 4.4 N-grams

O sistema usa **bigramas** (n=2) além de unigramas para capturar frases:

```python
tfidf = TfidfVectorizer(ngram_range=(1, 2))
```

**Exemplo**:
- Texto: "Star Wars"
- Unigramas: ["star", "wars"]
- Bigramas: ["star wars"]

Isso permite buscas mais precisas como "star wars" em vez de encontrar qualquer filme com "star" ou "wars" separadamente.

---

## 5. Processamento de Linguagem Natural (NLP)

### 5.1 Pipeline de Pré-processamento

```python
def preprocess_text(text):
    # 1. Lowercase
    text = text.lower()
    
    # 2. Normalização Unicode (remove acentos)
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    
    # 3. Remove pontuação
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # 4. Tokenização
    tokens = word_tokenize(text)
    
    # 5. Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [t for t in tokens if t not in stop_words]
    
    return " ".join(tokens)
```

### 5.2 Exemplo de Transformação

**Entrada**:
```
"The Avengers: Earth's Mightiest Heroes assemble to fight evil!"
```

**Processo**:
| Etapa | Resultado |
|-------|-----------|
| Lowercase | "the avengers: earth's mightiest heroes assemble to fight evil!" |
| Remove acentos | "the avengers: earth's mightiest heroes assemble to fight evil!" |
| Remove pontuação | "the avengers earths mightiest heroes assemble to fight evil" |
| Tokenização | ["the", "avengers", "earths", "mightiest", "heroes", "assemble", "to", "fight", "evil"] |
| Remove stopwords | ["avengers", "earths", "mightiest", "heroes", "assemble", "fight", "evil"] |

**Saída**:
```
"avengers earths mightiest heroes assemble fight evil"
```

### 5.3 Stopwords

Palavras removidas por não agregarem significado semântico:

```
the, a, an, is, are, was, were, be, been, being,
have, has, had, do, does, did, will, would, could,
should, may, might, must, shall, can, to, of, in,
for, on, with, at, by, from, as, into, through...
```

---

## 6. API RESTful

### 6.1 Endpoints Disponíveis

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/movies` | Lista top 200 filmes por popularidade |
| GET | `/genres` | Lista todos os gêneros disponíveis |
| GET | `/movies/by-genre/{genre}` | Filmes de um gênero específico |
| POST | `/recommend` | Retorna recomendações baseadas na query |

### 6.2 Exemplo de Requisição - Recomendação

**Request**:
```http
POST /recommend
Content-Type: application/json

{
    "query": "super hero action marvel"
}
```

**Response**:
```json
[
    {
        "id": 24428,
        "title": "The Avengers",
        "description": "When an unexpected enemy emerges...",
        "genre": "['Action', 'Adventure', 'Science Fiction']",
        "director": "Joss Whedon",
        "cast": "['Robert Downey Jr.', 'Chris Evans', ...]",
        "image_url": "https://image.tmdb.org/t/p/w500/...",
        "vote_average": 7.7,
        "popularity": 89.887,
        "score": 0.95
    },
    // ... mais 9 filmes
]
```

### 6.3 CORS (Cross-Origin Resource Sharing)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Permite qualquer origem
    allow_credentials=True,
    allow_methods=["*"],      # Permite todos os métodos HTTP
    allow_headers=["*"],      # Permite todos os headers
)
```

---

## 7. Frontend

### 7.1 Estrutura de Arquivos

```
frontend/
├── index.html    # Estrutura da página
├── style.css     # Estilos (design Netflix-like)
└── app.js        # Lógica de interação
```

### 7.2 Funcionalidades

1. **Navegação por Gêneros**: Carrossel horizontal com scroll
2. **Busca por Texto**: Input com autocomplete implícito
3. **Cards de Filmes**: Poster, título, rating, score de match
4. **Click para Similaridade**: Ao clicar em um filme, busca similares

### 7.3 Fluxo de Interação

```
┌────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Página Carrega                                          │
│     │                                                       │
│     ▼                                                       │
│  2. loadGenreSections()                                     │
│     │                                                       │
│     ├──► GET /genres                                        │
│     │                                                       │
│     └──► Para cada gênero:                                  │
│          GET /movies/by-genre/{genre}                       │
│                                                             │
│  3. Usuário digita busca                                    │
│     │                                                       │
│     ▼                                                       │
│  4. getRecommendations(query)                               │
│     │                                                       │
│     └──► POST /recommend { query }                          │
│                                                             │
│  5. Exibe resultados com % de match                         │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

---

## 8. Tecnologias Utilizadas

### Backend

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| Python | 3.8+ | Linguagem principal |
| FastAPI | 0.100+ | Framework web assíncrono |
| Uvicorn | 0.23+ | Servidor ASGI |
| Pandas | 2.0+ | Manipulação de dados |
| Scikit-learn | 1.3+ | TF-IDF e Cosine Similarity |
| NLTK | 3.8+ | Processamento de texto |

### Frontend

| Tecnologia | Uso |
|------------|-----|
| HTML5 | Estrutura |
| CSS3 | Estilização (Flexbox, Grid) |
| JavaScript (ES6+) | Interatividade, Fetch API |
| Google Fonts (Inter) | Tipografia |

### Dados

| Fonte | Descrição |
|-------|-----------|
| TMDB Dataset | Movies Metadata, Credits, Keywords |
| ~45.000 filmes | Dataset original |
| ~8.000 filmes | Após filtro de qualidade (vote_count ≥ 50) |

---

## 9. Como Executar

### Pré-requisitos

- Python 3.8+
- pip
- Git

### Passo a Passo

```bash
# 1. Clone o repositório
git clone https://github.com/LSenzaki/sistema-de-recomendacao-de-filme.git
cd sistema-de-recomendacao-de-filme

# 2. Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instale dependências
pip install -r backend/requirements.txt

# 4. Baixe recursos NLTK
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"

# 5. Inicie o backend (porta 8000)
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 6. Em outro terminal, inicie o frontend (porta 3000)
cd frontend
python -m http.server 3000

# 7. Acesse http://localhost:3000
```

---

## 10. Demonstração Prática

### 10.1 Casos de Uso para Demonstrar

| Busca | Resultado Esperado |
|-------|-------------------|
| "super hero marvel" | Vingadores, Homem de Ferro, etc. |
| "romantic comedy" | Filmes de comédia romântica |
| "Christopher Nolan" | Inception, Interstellar, Batman |
| "space adventure" | Star Wars, Guardians of the Galaxy |
| "Tom Hanks drama" | Forrest Gump, Cast Away, etc. |

### 10.2 Pontos para Destacar na Apresentação

1. **Eficiência do TF-IDF**: Vetorização pré-computada permite buscas em milissegundos
2. **Sistema de Pesos**: Keywords têm 6x mais importância que descrição
3. **Score Normalizado**: Porcentagem intuitiva para o usuário
4. **Arquitetura Desacoplada**: Frontend e Backend independentes
5. **Escalabilidade**: Fácil adicionar mais filmes ou features

### 10.3 Limitações e Melhorias Futuras

| Limitação Atual | Melhoria Possível |
|-----------------|-------------------|
| Dados estáticos (CSV) | Integrar API TMDB em tempo real |
| Sem perfil de usuário | Adicionar sistema de login/preferências |
| Apenas inglês | Suporte multilíngue |
| Sem avaliações do usuário | Implementar ratings e feedback |
| Content-based apenas | Híbrido com Collaborative Filtering |

---

## 📚 Referências

1. **TF-IDF**: Salton, G., & Buckley, C. (1988). Term-weighting approaches in automatic text retrieval.
2. **Cosine Similarity**: Singhal, A. (2001). Modern information retrieval: A brief overview.
3. **TMDB Dataset**: https://www.themoviedb.org/
4. **FastAPI Documentation**: https://fastapi.tiangolo.com/
5. **Scikit-learn TfidfVectorizer**: https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html

---

## 🎓 Resumo Executivo para Apresentação

> **NetRecs** é um sistema de recomendação de filmes que utiliza **TF-IDF** para vetorizar características textuais dos filmes e **Similaridade do Cosseno** para encontrar os mais relevantes à busca do usuário. O sistema processa ~8.000 filmes do TMDB, aplicando técnicas de **NLP** (tokenização, remoção de stopwords) e um **sistema de pesos** que prioriza keywords e título. A arquitetura **cliente-servidor** separa o frontend (HTML/CSS/JS) do backend (**FastAPI**), comunicando-se via **API REST**. O resultado é uma experiência similar ao Netflix, com recomendações instantâneas e scores de correspondência em porcentagem.

---

*Documento gerado para apresentação do projeto NetRecs - Sistema de Recomendação de Filmes*
