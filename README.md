# Sistema de Recomendação de Filmes 🎬

Um sistema inteligente de recomendação de filmes baseado em similaridade de conteúdo, utilizando técnicas de processamento de linguagem natural (NLP) e aprendizado de máquina.

![NetRecs](https://img.shields.io/badge/NetRecs-Movie%20Recommendations-red?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=for-the-badge&logo=fastapi)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Instalação](#instalação)
- [Uso](#uso)
- [API Endpoints](#api-endpoints)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Como Funciona](#como-funciona)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

## 🎯 Sobre o Projeto

O **NetRecs** é um sistema de recomendação de filmes que utiliza técnicas avançadas de NLP para encontrar filmes similares baseados em múltiplos fatores como título, gênero, descrição, diretor, elenco e palavras-chave. O sistema processa dados de filmes do TMDB (The Movie Database) e oferece uma interface web moderna e intuitiva.

### Destaques

- ✨ **Recomendações Inteligentes**: Algoritmo baseado em TF-IDF e similaridade de cosseno
- 🎨 **Interface Moderna**: Design inspirado em plataformas de streaming populares
- 🔍 **Busca Avançada**: Pesquisa por título, gênero, diretor, atores ou palavras-chave
- 📊 **Múltiplos Filtros**: Navegação por gêneros com filmes populares
- ⚡ **API RESTful**: Backend FastAPI de alto desempenho

## ✨ Funcionalidades

- **Recomendações Personalizadas**: Sistema de recomendação baseado em conteúdo com pesos otimizados
- **Busca Inteligente**: Processamento de texto com remoção de stopwords e normalização
- **Navegação por Gêneros**: Explore filmes por categorias específicas
- **Scores de Similaridade**: Visualize o percentual de correspondência com sua busca
- **Interface Responsiva**: Design adaptável para diferentes dispositivos
- **Dados Reais**: Integração com dataset do TMDB

## 🚀 Tecnologias

### Backend
- **Python 3.8+**
- **FastAPI**: Framework web moderno e rápido
- **Pandas**: Manipulação e análise de dados
- **Scikit-learn**: TF-IDF Vectorizer e Cosine Similarity
- **NLTK**: Processamento de linguagem natural
- **Uvicorn**: Servidor ASGI

### Frontend
- **HTML5/CSS3**: Estrutura e estilização
- **JavaScript (Vanilla)**: Interatividade
- **Google Fonts (Inter)**: Tipografia moderna

### Dados
- **TMDB Dataset**: Movies Metadata, Credits, Keywords

## 📦 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git

### Passo a Passo

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/sistema-de-recomendacao-de-filme.git
cd sistema-de-recomendacao-de-filme
```

2. **Crie um ambiente virtual (recomendado)**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instale as dependências do backend**
```bash
pip install -r backend/requirements.txt
```

4. **Baixe os recursos do NLTK**
```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"
```

5. **Configure as variáveis de ambiente (opcional)**
```bash
# Crie um arquivo .env na raiz do projeto
# Adicione suas configurações se necessário
```

6. **Prepare os dados**

Se você tiver os datasets do TMDB:
```bash
# Coloque os arquivos CSV na pasta data/extracted/
# Execute o processador de dados
python backend/data_processor.py
```

Ou use os dados de exemplo:
```bash
python generate_data.py
```

## 🎮 Uso

### Iniciando o Backend

```bash
cd backend
python main.py
```

O servidor estará disponível em: `http://localhost:8000`

### Acessando o Frontend

1. Abra o arquivo `frontend/index.html` em um navegador web, ou
2. Use um servidor HTTP local:

```bash
# Python
cd frontend
python -m http.server 8080

# Acesse: http://localhost:8080
```

### Usando a API

Você pode testar a API diretamente em: `http://localhost:8000/docs` (Swagger UI)

## 🔌 API Endpoints

### GET `/movies`
Retorna os 200 filmes mais populares.

**Resposta:**
```json
[
  {
    "id": 1,
    "title": "The Avengers",
    "description": "Earth's mightiest heroes...",
    "genre": ["Action", "Sci-Fi"],
    "image_url": "https://image.tmdb.org/t/p/w500/...",
    "director": "Joss Whedon",
    "cast": ["Robert Downey Jr.", "Chris Evans", ...],
    "keywords": ["superhero", "marvel", ...],
    "vote_average": 7.7,
    "vote_count": 28000,
    "popularity": 150.5
  },
  ...
]
```

### GET `/genres`
Retorna todos os gêneros únicos disponíveis.

**Resposta:**
```json
["Action", "Adventure", "Animation", "Comedy", "Crime", "Drama", ...]
```

### GET `/movies/by-genre/{genre}`
Retorna filmes filtrados por gênero.

**Parâmetros:**
- `genre` (path): Nome do gênero
- `limit` (query, opcional): Número máximo de filmes (padrão: 20)

**Exemplo:**
```
GET /movies/by-genre/Action?limit=10
```

### POST `/recommend`
Retorna recomendações baseadas em uma consulta.

**Request Body:**
```json
{
  "query": "superhero movies with action"
}
```

**Resposta:**
```json
[
  {
    "id": 1,
    "title": "The Avengers",
    "score": 0.95,
    ...
  },
  ...
]
```

## 📁 Estrutura do Projeto

```
sistema-de-recomendacao-de-filme/
├── backend/
│   ├── main.py                 # API FastAPI principal
│   ├── data_processor.py       # Processamento de dados TMDB
│   └── requirements.txt        # Dependências Python
├── frontend/
│   ├── index.html             # Página principal
│   ├── style.css              # Estilos CSS
│   └── app.js                 # Lógica JavaScript
├── data/
│   ├── extracted/             # Dados brutos do TMDB
│   ├── processed_movies.csv   # Dados processados
│   └── movies.csv             # Dados de exemplo
├── docs/                      # Documentação MkDocs
├── .env                       # Variáveis de ambiente
├── .gitignore                # Arquivos ignorados pelo Git
├── generate_data.py          # Gerador de dados de exemplo
├── update_images.py          # Script para atualizar imagens
├── mkdocs.yml                # Configuração MkDocs
├── README.md                 # Este arquivo
└── LICENSE                   # Licença do projeto
```

## 🧠 Como Funciona

### 1. Processamento de Dados

O sistema processa dados do TMDB extraindo:
- Metadados dos filmes
- Informações de créditos (elenco e equipe)
- Palavras-chave e empresas de produção

### 2. Criação de Features

Combina múltiplos atributos com pesos otimizados:
- **Keywords**: 6x (maior peso para buscas por palavras-chave)
- **Título**: 3x
- **Diretor**: 3x
- **Elenco**: 2x
- **Gênero**: 2x
- **Descrição**: 1x

### 3. Vetorização TF-IDF

Utiliza TF-IDF (Term Frequency-Inverse Document Frequency) com n-gramas (1,2) para capturar:
- Palavras individuais
- Frases de duas palavras

### 4. Cálculo de Similaridade

Aplica similaridade de cosseno entre:
- Vetor da consulta do usuário
- Vetores de todos os filmes

### 5. Normalização de Scores

Normaliza os scores para uma escala de 0-95% para melhor interpretação.

## 🤝 Contribuindo

Contribuições são bem-vindas! Siga estas etapas:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👥 Autores

- Seu Nome - [GitHub](https://github.com/seu-usuario)

## 🙏 Agradecimentos

- [TMDB](https://www.themoviedb.org/) pelos dados de filmes
- [FastAPI](https://fastapi.tiangolo.com/) pelo excelente framework
- Comunidade open source

---

⭐ Se este projeto foi útil para você, considere dar uma estrela!
