# API Reference

Documentação completa da API RESTful do Sistema de Recomendação de Filmes.

## Base URL

```
http://localhost:8000
```

## Documentação Interativa

A API oferece documentação interativa através do Swagger UI:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Endpoints

### GET `/movies`

Retorna os 200 filmes mais populares do dataset.

#### Request

```http
GET /movies HTTP/1.1
Host: localhost:8000
```

#### Response

**Status Code**: `200 OK`

```json
[
  {
    "id": 299536,
    "title": "Avengers: Infinity War",
    "description": "The Avengers and their allies must be willing to sacrifice all...",
    "genre": ["Action", "Adventure", "Science Fiction"],
    "image_url": "https://image.tmdb.org/t/p/w500/7WsyChQLEftFiDOVTGkv3hFpyyt.jpg",
    "director": "Anthony Russo",
    "cast": ["Robert Downey Jr.", "Chris Hemsworth", "Mark Ruffalo", "Chris Evans", "Scarlett Johansson"],
    "keywords": ["superhero", "marvel", "infinity stones", "thanos", "avengers"],
    "vote_average": 8.3,
    "vote_count": 28000,
    "popularity": 150.5
  },
  ...
]
```

#### Campos da Resposta

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | integer | ID único do filme (TMDB ID) |
| `title` | string | Título do filme |
| `description` | string | Sinopse/descrição do filme |
| `genre` | array[string] | Lista de gêneros |
| `image_url` | string | URL da imagem do poster |
| `director` | string | Nome do diretor |
| `cast` | array[string] | Lista dos 5 principais atores |
| `keywords` | array[string] | Palavras-chave e empresas de produção |
| `vote_average` | float | Média de votos (0-10) |
| `vote_count` | integer | Número de votos |
| `popularity` | float | Score de popularidade |

---

### GET `/genres`

Retorna todos os gêneros únicos disponíveis no dataset.

#### Request

```http
GET /genres HTTP/1.1
Host: localhost:8000
```

#### Response

**Status Code**: `200 OK`

```json
[
  "Action",
  "Adventure",
  "Animation",
  "Comedy",
  "Crime",
  "Documentary",
  "Drama",
  "Family",
  "Fantasy",
  "History",
  "Horror",
  "Music",
  "Mystery",
  "Romance",
  "Science Fiction",
  "Thriller",
  "War",
  "Western"
]
```

---

### GET `/movies/by-genre/{genre}`

Retorna filmes filtrados por um gênero específico, ordenados por popularidade.

#### Request

```http
GET /movies/by-genre/Action?limit=10 HTTP/1.1
Host: localhost:8000
```

#### Parâmetros

**Path Parameters**:

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `genre` | string | Sim | Nome do gênero (case-sensitive) |

**Query Parameters**:

| Parâmetro | Tipo | Obrigatório | Default | Descrição |
|-----------|------|-------------|---------|-----------|
| `limit` | integer | Não | 20 | Número máximo de filmes a retornar |

#### Response

**Status Code**: `200 OK`

```json
[
  {
    "id": 299536,
    "title": "Avengers: Infinity War",
    "description": "The Avengers and their allies...",
    "genre": ["Action", "Adventure", "Science Fiction"],
    ...
  },
  ...
]
```

#### Exemplos

```bash
# Obter 10 filmes de ação
curl "http://localhost:8000/movies/by-genre/Action?limit=10"

# Obter filmes de comédia (limite padrão: 20)
curl "http://localhost:8000/movies/by-genre/Comedy"
```

---

### POST `/recommend`

Retorna recomendações de filmes baseadas em uma consulta de texto.

#### Request

```http
POST /recommend HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "query": "superhero movies with action"
}
```

#### Request Body

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `query` | string | Sim | Texto de busca (título, gênero, diretor, ator, palavras-chave) |

#### Response

**Status Code**: `200 OK`

```json
[
  {
    "id": 299536,
    "title": "Avengers: Infinity War",
    "description": "The Avengers and their allies...",
    "genre": ["Action", "Adventure", "Science Fiction"],
    "image_url": "https://image.tmdb.org/t/p/w500/7WsyChQLEftFiDOVTGkv3hFpyyt.jpg",
    "director": "Anthony Russo",
    "cast": ["Robert Downey Jr.", "Chris Hemsworth", ...],
    "keywords": ["superhero", "marvel", ...],
    "vote_average": 8.3,
    "vote_count": 28000,
    "popularity": 150.5,
    "score": 0.95
  },
  ...
]
```

!!! note "Campo Adicional"
    A resposta inclui um campo `score` (0.0 - 0.95) que indica o percentual de similaridade com a consulta.

#### Exemplos de Consultas

```bash
# Buscar por gênero
curl -X POST "http://localhost:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{"query": "romantic comedy"}'

# Buscar por diretor
curl -X POST "http://localhost:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{"query": "Christopher Nolan"}'

# Buscar por ator
curl -X POST "http://localhost:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{"query": "Tom Hanks"}'

# Buscar por palavras-chave
curl -X POST "http://localhost:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{"query": "space exploration sci-fi"}'

# Buscar por título
curl -X POST "http://localhost:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{"query": "avengers"}'
```

---

## Algoritmo de Recomendação

### Como Funciona

O sistema usa um algoritmo baseado em **TF-IDF** (Term Frequency-Inverse Document Frequency) e **Similaridade de Cosseno**:

1. **Pré-processamento de Texto**:
   - Conversão para minúsculas
   - Remoção de acentos
   - Remoção de pontuação
   - Tokenização
   - Remoção de stopwords (inglês)

2. **Criação de Features Combinadas**:
   ```python
   features = [
       keywords * 6,      # Maior peso
       title * 3,
       director * 3,
       cast * 2,
       genre * 2,
       description * 1    # Menor peso
   ]
   ```

3. **Vetorização TF-IDF**:
   - N-gramas: (1, 2) - palavras individuais e pares
   - Vetorização de features combinadas

4. **Cálculo de Similaridade**:
   - Similaridade de cosseno entre query e todos os filmes
   - Ordenação por score decrescente

5. **Normalização**:
   - Scores normalizados para 0-95%
   - Top 10 resultados retornados

### Pesos das Features

| Feature | Peso | Razão |
|---------|------|-------|
| Keywords | 6x | Maior precisão em buscas específicas |
| Title | 3x | Importância do título |
| Director | 3x | Estilo do diretor é relevante |
| Cast | 2x | Atores influenciam preferências |
| Genre | 2x | Categoria importante |
| Description | 1x | Contexto geral |

---

## Códigos de Status HTTP

| Código | Descrição |
|--------|-----------|
| `200 OK` | Requisição bem-sucedida |
| `422 Unprocessable Entity` | Erro de validação nos dados enviados |
| `500 Internal Server Error` | Erro interno do servidor |

---

## Rate Limiting

Atualmente, a API **não possui** rate limiting. Em produção, considere implementar:

- Limite de requisições por IP
- Autenticação via API key
- Cache de respostas

---

## CORS

A API está configurada para aceitar requisições de qualquer origem (`allow_origins=["*"]`).

Para produção, configure origens específicas em `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://seu-dominio.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Exemplos de Integração

### JavaScript (Fetch API)

```javascript
// Obter filmes
async function getMovies() {
  const response = await fetch('http://localhost:8000/movies');
  const movies = await response.json();
  return movies;
}

// Obter recomendações
async function getRecommendations(query) {
  const response = await fetch('http://localhost:8000/recommend', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query }),
  });
  const recommendations = await response.json();
  return recommendations;
}

// Uso
getRecommendations('action superhero').then(movies => {
  console.log(movies);
});
```

### Python (requests)

```python
import requests

# Obter filmes
response = requests.get('http://localhost:8000/movies')
movies = response.json()

# Obter recomendações
response = requests.post(
    'http://localhost:8000/recommend',
    json={'query': 'romantic comedy'}
)
recommendations = response.json()

print(recommendations)
```

### cURL

```bash
# Obter todos os gêneros
curl http://localhost:8000/genres

# Obter filmes de ação
curl "http://localhost:8000/movies/by-genre/Action?limit=5"

# Obter recomendações
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "space adventure"}'
```

---

## Próximos Passos

- 🎨 [Explore o Frontend](frontend.md)
- 📊 [Entenda o Processamento de Dados](data-processing.md)
- 🤝 [Contribua para o projeto](contributing.md)
