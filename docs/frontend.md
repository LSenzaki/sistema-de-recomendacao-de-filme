# Documentação do Frontend

Guia completo sobre a interface web do NetRecs.

## Visão Geral

O frontend do NetRecs é uma aplicação web moderna e responsiva, construída com HTML5, CSS3 e JavaScript vanilla. A interface foi inspirada em plataformas de streaming populares como Netflix, oferecendo uma experiência familiar e intuitiva.

## Estrutura de Arquivos

```
frontend/
├── index.html      # Estrutura HTML principal
├── style.css       # Estilos e design
└── app.js          # Lógica e interatividade
```

## Componentes Principais

### 1. Header (Cabeçalho)

O cabeçalho contém o logo e a barra de pesquisa.

```html
<header>
    <div class="logo">NETRECS</div>
    <div class="search-container">
        <input type="text" id="searchInput" placeholder="What are you looking for?">
        <button id="searchBtn">Search</button>
    </div>
</header>
```

**Funcionalidades**:
- Logo clicável que recarrega a página
- Campo de busca com placeholder
- Botão de pesquisa
- Suporte para busca ao pressionar Enter

### 2. Hero Section

Seção de boas-vindas exibida quando não há busca ativa.

```html
<section id="hero" class="hero">
    <div class="hero-content">
        <h1>Unlimited Movies, TV Shows, and More.</h1>
        <p>Discover your next favorite story.</p>
    </div>
</section>
```

**Características**:
- Gradiente de fundo vibrante
- Texto centralizado
- Animação de fade-in

### 3. Recommendations Section

Exibe os resultados da busca com scores de similaridade.

```html
<section id="recommendations" class="movie-section hidden">
    <h2>Recommended for You</h2>
    <div class="movie-grid" id="recommendationsGrid">
        <!-- Filmes aparecem aqui -->
    </div>
</section>
```

**Funcionalidades**:
- Grid responsivo de filmes
- Scores de similaridade em porcentagem
- Animações de hover
- Informações detalhadas ao passar o mouse

### 4. Genre Sections

Seções dinâmicas organizadas por gênero.

```html
<section id="genreSections" class="genre-sections">
    <!-- Seções de gênero carregadas dinamicamente -->
</section>
```

**Características**:
- Carregamento automático ao iniciar
- Scroll horizontal para cada gênero
- Filmes ordenados por popularidade

## Design System

### Paleta de Cores

```css
:root {
    --primary-bg: #141414;        /* Fundo principal */
    --secondary-bg: #1a1a1a;      /* Fundo secundário */
    --accent-color: #e50914;      /* Vermelho Netflix */
    --accent-hover: #f40612;      /* Vermelho hover */
    --text-primary: #ffffff;      /* Texto principal */
    --text-secondary: #b3b3b3;    /* Texto secundário */
}
```

### Tipografia

- **Fonte**: Inter (Google Fonts)
- **Pesos**: 400 (regular), 600 (semi-bold), 700 (bold)

```css
body {
    font-family: 'Inter', sans-serif;
    font-size: 16px;
    line-height: 1.6;
}
```

### Espaçamento

```css
/* Sistema de espaçamento consistente */
--spacing-xs: 0.5rem;   /* 8px */
--spacing-sm: 1rem;     /* 16px */
--spacing-md: 1.5rem;   /* 24px */
--spacing-lg: 2rem;     /* 32px */
--spacing-xl: 3rem;     /* 48px */
```

## Componentes de UI

### Movie Card

Cartão de filme com imagem, título e informações.

```html
<div class="movie-card">
    <img src="..." alt="Movie Title">
    <div class="movie-info">
        <h3>Movie Title</h3>
        <p class="movie-genre">Action, Sci-Fi</p>
        <p class="movie-description">Description...</p>
        <span class="match-score">95% Match</span>
    </div>
</div>
```

**Efeitos**:
- Hover: Escala 1.05 e sombra
- Transição suave (0.3s)
- Overlay com informações adicionais

### Search Bar

Barra de pesquisa estilizada.

```css
.search-container input {
    background: rgba(255, 255, 255, 0.1);
    border: 2px solid transparent;
    border-radius: 4px;
    padding: 0.75rem 1rem;
    color: white;
    transition: all 0.3s ease;
}

.search-container input:focus {
    background: rgba(255, 255, 255, 0.15);
    border-color: var(--accent-color);
    outline: none;
}
```

### Buttons

Botões com estados interativos.

```css
button {
    background: var(--accent-color);
    color: white;
    border: none;
    padding: 0.75rem 2rem;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.3s ease;
}

button:hover {
    background: var(--accent-hover);
}
```

## JavaScript - Funcionalidades

### 1. Inicialização

```javascript
document.addEventListener('DOMContentLoaded', () => {
    loadGenres();
    setupEventListeners();
});
```

### 2. Busca de Filmes

```javascript
async function searchMovies(query) {
    try {
        const response = await fetch(`${API_BASE_URL}/recommend`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query }),
        });
        
        const movies = await response.json();
        displayRecommendations(movies);
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to fetch recommendations');
    }
}
```

### 3. Renderização de Filmes

```javascript
function displayRecommendations(movies) {
    const grid = document.getElementById('recommendationsGrid');
    grid.innerHTML = '';
    
    movies.forEach(movie => {
        const card = createMovieCard(movie);
        grid.appendChild(card);
    });
    
    // Mostrar seção de recomendações
    document.getElementById('recommendations').classList.remove('hidden');
    document.getElementById('hero').classList.add('hidden');
}
```

### 4. Carregamento de Gêneros

```javascript
async function loadGenres() {
    try {
        const genres = await fetchGenres();
        
        for (const genre of genres) {
            const movies = await fetchMoviesByGenre(genre, 20);
            createGenreSection(genre, movies);
        }
    } catch (error) {
        console.error('Error loading genres:', error);
    }
}
```

### 5. Scroll Horizontal

```javascript
function setupHorizontalScroll(container) {
    let isDown = false;
    let startX;
    let scrollLeft;
    
    container.addEventListener('mousedown', (e) => {
        isDown = true;
        startX = e.pageX - container.offsetLeft;
        scrollLeft = container.scrollLeft;
    });
    
    container.addEventListener('mousemove', (e) => {
        if (!isDown) return;
        e.preventDefault();
        const x = e.pageX - container.offsetLeft;
        const walk = (x - startX) * 2;
        container.scrollLeft = scrollLeft - walk;
    });
    
    container.addEventListener('mouseup', () => {
        isDown = false;
    });
}
```

## Responsividade

### Breakpoints

```css
/* Mobile */
@media (max-width: 768px) {
    .movie-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .search-container {
        flex-direction: column;
    }
}

/* Tablet */
@media (min-width: 769px) and (max-width: 1024px) {
    .movie-grid {
        grid-template-columns: repeat(3, 1fr);
    }
}

/* Desktop */
@media (min-width: 1025px) {
    .movie-grid {
        grid-template-columns: repeat(5, 1fr);
    }
}
```

## Animações

### Fade In

```css
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.movie-card {
    animation: fadeIn 0.5s ease-out;
}
```

### Hover Effects

```css
.movie-card {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.movie-card:hover {
    transform: scale(1.05);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
}
```

## Otimizações

### 1. Lazy Loading de Imagens

```javascript
function createMovieCard(movie) {
    const img = document.createElement('img');
    img.loading = 'lazy';  // Lazy loading nativo
    img.src = movie.image_url;
    img.alt = movie.title;
    // ...
}
```

### 2. Debounce na Busca

```javascript
let searchTimeout;

searchInput.addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        if (e.target.value.length >= 3) {
            searchMovies(e.target.value);
        }
    }, 500);  // Aguarda 500ms após parar de digitar
});
```

### 3. Cache de Requisições

```javascript
const cache = new Map();

async function fetchWithCache(url) {
    if (cache.has(url)) {
        return cache.get(url);
    }
    
    const response = await fetch(url);
    const data = await response.json();
    cache.set(url, data);
    
    return data;
}
```

## Acessibilidade

### ARIA Labels

```html
<button aria-label="Search for movies">Search</button>
<img src="..." alt="Movie poster for Avengers">
```

### Navegação por Teclado

```javascript
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        searchMovies(searchInput.value);
    }
});
```

### Contraste de Cores

Todas as combinações de cores atendem ao padrão WCAG AA:
- Texto branco (#ffffff) sobre fundo escuro (#141414): 15.3:1
- Vermelho (#e50914) sobre fundo escuro: 5.2:1

## Personalização

### Alterar Cores

Edite as variáveis CSS em `style.css`:

```css
:root {
    --accent-color: #your-color;  /* Cor principal */
    --accent-hover: #your-hover-color;
}
```

### Adicionar Novos Gêneros

Não é necessário modificar o código - os gêneros são carregados dinamicamente da API.

### Customizar Layout

Ajuste o grid de filmes em `style.css`:

```css
.movie-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1.5rem;
}
```

## Troubleshooting

### Imagens não carregam

**Problema**: URLs de imagem inválidas ou CORS.

**Solução**: Verifique se o backend está retornando URLs válidas do TMDB.

### Busca não funciona

**Problema**: Backend não está rodando ou URL incorreta.

**Solução**: Verifique `API_BASE_URL` em `app.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

### Layout quebrado em mobile

**Problema**: Viewport não configurado.

**Solução**: Adicione em `index.html`:

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

## Próximos Passos

- 📖 [Documentação da API](api.md)
- 📊 [Processamento de Dados](data-processing.md)
- 🤝 [Como Contribuir](contributing.md)

---

!!! tip "Dica de Desenvolvimento"
    Use o DevTools do navegador (F12) para inspecionar elementos e testar mudanças em tempo real!
