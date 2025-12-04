const API_URL = 'http://localhost:8000';

// Current selected movie for modal
let currentMovie = null;

document.addEventListener('DOMContentLoaded', () => {
    loadGenreSections();
    setupModalEvents();

    const searchBtn = document.getElementById('searchBtn');
    const searchInput = document.getElementById('searchInput');

    searchBtn.addEventListener('click', () => {
        const query = searchInput.value;
        if (query) {
            getRecommendations(query);
        }
    });

    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const query = searchInput.value;
            if (query) {
                getRecommendations(query);
            }
        }
    });

    // Logo click to return home
    const logo = document.querySelector('.logo');
    logo.addEventListener('click', () => {
        window.location.reload();
    });
    logo.style.cursor = 'pointer';

    // Header scroll effect
    window.addEventListener('scroll', () => {
        const header = document.querySelector('header');
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
});

// ==========================================
// Modal Functions
// ==========================================

function setupModalEvents() {
    const modal = document.getElementById('movieModal');
    const closeBtn = modal.querySelector('.modal-close');
    const overlay = modal.querySelector('.modal-overlay');
    const findSimilarBtn = document.getElementById('btnFindSimilar');

    // Close modal
    closeBtn.addEventListener('click', closeModal);
    overlay.addEventListener('click', closeModal);

    // ESC key to close
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
            closeModal();
        }
    });

    // Find similar button
    findSimilarBtn.addEventListener('click', () => {
        if (currentMovie) {
            closeModal();
            const searchQuery = createSearchQuery(currentMovie);
            document.getElementById('searchInput').value = searchQuery;
            getRecommendations(searchQuery);
        }
    });
}

function openModal(movie, similarMovies = null) {
    console.log('openModal called with:', movie);
    currentMovie = movie;
    const modal = document.getElementById('movieModal');
    console.log('Modal element:', modal);

    // Set backdrop image
    const backdrop = document.getElementById('modalBackdrop');
    backdrop.style.backgroundImage = `url(${movie.image_url})`;

    // Set movie info
    document.getElementById('modalTitle').textContent = movie.title;
    document.getElementById('modalRating').textContent = `⭐ ${movie.vote_average ? movie.vote_average.toFixed(1) : 'N/A'} / 10`;
    
    // Show match score if available
    const matchEl = document.getElementById('modalMatch');
    if (movie.score) {
        matchEl.textContent = `${Math.round(movie.score * 100)}% Match`;
        matchEl.style.display = 'inline-block';
    } else {
        matchEl.style.display = 'none';
    }

    // Description
    document.getElementById('modalDescription').textContent = movie.description || 'No description available.';

    // Director
    document.getElementById('modalDirector').textContent = movie.director || 'Unknown';

    // Cast
    let castText = 'Unknown';
    if (movie.cast) {
        try {
            const cast = typeof movie.cast === 'string' ? 
                JSON.parse(movie.cast.replace(/'/g, '"')) : movie.cast;
            if (Array.isArray(cast)) {
                castText = cast.slice(0, 5).join(', ');
            }
        } catch (e) {
            castText = movie.cast;
        }
    }
    document.getElementById('modalCast').textContent = castText;

    // Genres
    let genreText = 'Unknown';
    if (movie.genre) {
        try {
            const genres = typeof movie.genre === 'string' ? 
                JSON.parse(movie.genre.replace(/'/g, '"')) : movie.genre;
            if (Array.isArray(genres)) {
                genreText = genres.join(', ');
            }
        } catch (e) {
            genreText = movie.genre;
        }
    }
    document.getElementById('modalGenres').textContent = genreText;

    // Show modal
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';

    // Load similar movies
    if (similarMovies) {
        displaySimilarMovies(similarMovies);
    } else {
        loadSimilarMovies(movie);
    }
}

function closeModal() {
    const modal = document.getElementById('movieModal');
    modal.classList.add('hidden');
    document.body.style.overflow = 'auto';
    currentMovie = null;
}

async function loadSimilarMovies(movie) {
    const container = document.getElementById('similarMoviesRow');
    container.innerHTML = '<div class="loading-similar"><div class="spinner"></div></div>';

    try {
        const searchQuery = createSearchQuery(movie);
        const response = await fetch(`${API_URL}/recommend`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: searchQuery }),
        });
        const data = await response.json();
        const recommendations = Array.isArray(data) ? data : (data.movies || []);
        
        // Filter out the current movie
        const filtered = recommendations.filter(m => m.id !== movie.id);
        displaySimilarMovies(filtered);
    } catch (error) {
        console.error('Error loading similar movies:', error);
        container.innerHTML = '<p style="color: #888;">Could not load similar movies.</p>';
    }
}

function displaySimilarMovies(movies) {
    const container = document.getElementById('similarMoviesRow');
    container.innerHTML = '';

    if (movies.length === 0) {
        container.innerHTML = '<p style="color: #888;">No similar movies found.</p>';
        return;
    }

    movies.forEach(movie => {
        const card = document.createElement('div');
        card.className = 'similar-card';

        const scoreHtml = movie.score ? 
            `<div class="similar-card-score">${Math.round(movie.score * 100)}% Match</div>` : '';

        card.innerHTML = `
            <img src="${movie.image_url}" alt="${movie.title}" 
                 onerror="this.onerror=null;this.src='https://via.placeholder.com/130x195?text=No+Image';">
            <div class="similar-card-info">
                <div class="similar-card-title">${movie.title}</div>
                ${scoreHtml}
            </div>
        `;

        card.addEventListener('click', () => {
            openModal(movie);
        });

        container.appendChild(card);
    });
}

async function loadGenreSections() {
    try {
        // Fetch all available genres
        const genresResponse = await fetch(`${API_URL}/genres`);
        const genres = await genresResponse.json();

        const genreSectionsContainer = document.getElementById('genreSections');

        // Load movies for each genre
        for (const genre of genres) {
            const section = createGenreSection(genre);
            genreSectionsContainer.appendChild(section);

            // Fetch movies for this genre
            const moviesResponse = await fetch(`${API_URL}/movies/by-genre/${encodeURIComponent(genre)}?limit=20`);
            const movies = await moviesResponse.json();

            // Display movies in the genre section
            displayMoviesInRow(movies, `genre-${genre.replace(/\s+/g, '-')}`);
        }
    } catch (error) {
        console.error('Error loading genre sections:', error);
    }
}

function createGenreSection(genre) {
    const section = document.createElement('section');
    section.className = 'genre-section';

    const genreId = `genre-${genre.replace(/\s+/g, '-')}`;

    section.innerHTML = `
        <h2 class="genre-title">${genre}</h2>
        <div class="movie-row-container">
            <button class="scroll-btn scroll-left" data-target="${genreId}">‹</button>
            <div class="movie-row" id="${genreId}">
                <!-- Movies will be loaded here -->
            </div>
            <button class="scroll-btn scroll-right" data-target="${genreId}">›</button>
        </div>
    `;

    // Add scroll button functionality
    const scrollLeft = section.querySelector('.scroll-left');
    const scrollRight = section.querySelector('.scroll-right');

    scrollLeft.addEventListener('click', () => {
        const row = document.getElementById(genreId);
        row.scrollBy({ left: -800, behavior: 'smooth' });
    });

    scrollRight.addEventListener('click', () => {
        const row = document.getElementById(genreId);
        row.scrollBy({ left: 800, behavior: 'smooth' });
    });

    return section;
}

function displayMoviesInRow(movies, rowId) {
    const row = document.getElementById(rowId);
    if (!row) return;

    row.innerHTML = '';

    movies.forEach(movie => {
        const card = document.createElement('div');
        card.className = 'movie-card-row';

        card.innerHTML = `
            <img src="${movie.image_url}" alt="${movie.title}" onerror="this.onerror=null;this.src='https://via.placeholder.com/300x450?text=No+Image';">
            <div class="movie-info-row">
                <div class="movie-title-row">${movie.title}</div>
                <div class="movie-rating">⭐ ${movie.vote_average ? movie.vote_average.toFixed(1) : 'N/A'}</div>
            </div>
        `;

        // Add click event to open modal
        card.addEventListener('click', () => {
            openModal(movie);
        });

        row.appendChild(card);
    });
}

function createSearchQuery(movie) {
    // Create an intelligent search query from movie data
    // Prioritize: title keywords, genre, and actual keywords
    let queryParts = [];

    // Extract key words from title (remove common words, numbers, years)
    const titleWords = movie.title
        .replace(/\d+/g, '') // Remove numbers
        .replace(/[:\-()]/g, ' ') // Remove punctuation
        .split(' ')
        .filter(word => word.length > 2) // Only words with 3+ chars
        .filter(word => !['the', 'and', 'for', 'with'].includes(word.toLowerCase()))
        .slice(0, 3); // Take first 3 meaningful words

    queryParts.push(...titleWords);

    // Add genres
    if (movie.genre) {
        try {
            const genres = typeof movie.genre === 'string' ?
                JSON.parse(movie.genre.replace(/'/g, '"')) : movie.genre;
            if (Array.isArray(genres)) {
                queryParts.push(...genres.slice(0, 2)); // Top 2 genres
            }
        } catch (e) {
            // If parsing fails, just use as string
            queryParts.push(movie.genre);
        }
    }

    // Add keywords
    if (movie.keywords) {
        try {
            const keywords = typeof movie.keywords === 'string' ?
                JSON.parse(movie.keywords.replace(/'/g, '"')) : movie.keywords;
            if (Array.isArray(keywords)) {
                queryParts.push(...keywords.slice(0, 5)); // Top 5 keywords
            }
        } catch (e) {
            // If parsing fails, skip
        }
    }

    // Join and return
    return queryParts.join(' ');
}

async function getRecommendations(query) {
    console.log('getRecommendations called with:', query);
    try {
        const response = await fetch(`${API_URL}/recommend`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query }),
        });
        const data = await response.json();
        console.log('API response:', data);
        
        // Handle both old format (array) and new enhanced format (object with movies property)
        const recommendations = Array.isArray(data) ? data : (data.movies || []);
        console.log('Recommendations count:', recommendations.length);

        const recommendationsSection = document.getElementById('recommendations');
        recommendationsSection.classList.remove('hidden');

        displayMovies(recommendations, 'recommendationsGrid', true);

        // Scroll to recommendations
        recommendationsSection.scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        console.error('Error getting recommendations:', error);
    }
}

function displayMovies(movies, gridId, showScore = false) {
    const grid = document.getElementById(gridId);
    grid.innerHTML = '';

    movies.forEach(movie => {
        const card = document.createElement('div');
        card.className = 'movie-card';

        let scoreHtml = '';
        if (showScore && movie.score) {
            const percentage = Math.round(movie.score * 100);
            scoreHtml = `<div class="similarity-score">${percentage}% Match</div>`;
        }

        card.innerHTML = `
            <img src="${movie.image_url}" alt="${movie.title}" onerror="this.onerror=null;this.src='https://via.placeholder.com/500x750?text=No+Image';">
            ${scoreHtml}
            <div class="movie-info">
                <div class="movie-title">${movie.title}</div>
                <div class="movie-genre">${formatGenre(movie.genre)}</div>
            </div>
        `;

        // Add click event to open modal
        card.addEventListener('click', () => {
            openModal(movie, movies.filter(m => m.id !== movie.id));
        });

        grid.appendChild(card);
    });
}

function formatGenre(genre) {
    if (!genre) return '';
    try {
        const genres = typeof genre === 'string' ? 
            JSON.parse(genre.replace(/'/g, '"')) : genre;
        if (Array.isArray(genres)) {
            return genres.slice(0, 3).join(', ');
        }
    } catch (e) {
        return genre;
    }
    return genre;
}
