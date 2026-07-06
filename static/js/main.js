document.addEventListener('DOMContentLoaded', () => {
    
    // --- Theme Toggling ---
    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {
        const darkIcon = themeBtn.querySelector('.dark-icon');
        const lightIcon = themeBtn.querySelector('.light-icon');
        
        // Setup initial icon state
        if (document.documentElement.getAttribute('data-theme') === 'light') {
            darkIcon.classList.add('d-none');
            lightIcon.classList.remove('d-none');
        }
        
        themeBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Toggle icons
            darkIcon.classList.toggle('d-none');
            lightIcon.classList.toggle('d-none');
        });
    }
    
    // --- Instant Playback Logic (Home Page) ---
    const instantContainer = document.getElementById('instant-songs-container');
    if (instantContainer) {
        fetch('/instant_songs')
            .then(res => res.json())
            .then(data => {
                document.getElementById('instant-loading').classList.add('d-none');
                data.songs.forEach((song, index) => {
                    const delay = index * 0.05;
                    const cardHTML = `
                        <div class="col fade-in-up" style="animation-delay: ${delay}s;">
                            <a href="${song.url}" target="_blank" class="text-decoration-none text-reset h-100 d-block">
                            <div class="glass-card song-card p-3 h-100">
                                <div class="song-cover-container">
                                    <img src="${song.cover}" alt="${song.title} Cover" class="song-cover">
                                    <div class="play-overlay">
                                        <div class="play-btn"><i class="bi bi-play-fill"></i></div>
                                    </div>
                                </div>
                                <h6 class="fw-bold mb-1 text-truncate" title="${song.title}">${song.title}</h6>
                                <p class="small text-muted mb-2 text-truncate" title="${song.artist}">${song.artist}</p>
                            </div>
                            </a>
                        </div>
                    `;
                    instantContainer.insertAdjacentHTML('beforeend', cardHTML);
                });
            })
            .catch(err => {
                console.error(err);
                document.getElementById('instant-loading').innerHTML = '<p class="text-danger">Failed to load tracks. Please refresh.</p>';
            });
    }
    
    // --- Prediction Logic ---
    const predictForm = document.getElementById('predict-form');
    
    if (predictForm) {
        predictForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const textInput = document.getElementById('mood-text').value.trim();
            if (!textInput) return;
            
            // Show loading
            const loadingOverlay = document.getElementById('loading-overlay');
            loadingOverlay.classList.remove('d-none');
            
            try {
                // In a real app, this points to your Flask /predict endpoint
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text: textInput })
                });
                
                if (!response.ok) throw new Error('Network response was not ok');
                
                const data = await response.json();
                
                // Hide loading
                loadingOverlay.classList.add('d-none');
                
                // Process and show results
                displayResults(data);
                
            } catch (error) {
                console.error('Error during prediction:', error);
                loadingOverlay.classList.add('d-none');
                alert('An error occurred while analyzing your mood. Please try again.');
            }
        });
        
        // Reset button
        document.getElementById('reset-btn')?.addEventListener('click', () => {
            document.getElementById('results-section').classList.add('d-none');
            document.getElementById('input-section').classList.remove('d-none');
            document.getElementById('mood-text').value = '';
            
            // Reset theme to base
            document.documentElement.className = '';
        });
    }
});

function displayResults(data) {
    // Hide input, show results
    document.getElementById('input-section').classList.add('d-none');
    
    const resultsSection = document.getElementById('results-section');
    resultsSection.classList.remove('d-none');
    
    // Populate header info
    document.getElementById('res-emoji').textContent = data.emoji;
    document.getElementById('res-mood').textContent = data.mood;
    document.getElementById('res-confidence').textContent = `${data.confidence_score}%`;
    document.getElementById('res-description').textContent = `"${data.description}"`;
    document.getElementById('res-wellness').textContent = data.wellness_suggestion;
    
    // Apply theme
    const themeClass = `theme-${data.mood.toLowerCase()}`;
    document.body.className = `d-flex flex-column min-vh-100 transition-body ${themeClass}`; // applies to body
    
    // Populate songs
    const container = document.getElementById('songs-container');
    container.innerHTML = '';
    
    data.songs.forEach((song, index) => {
        // Staggered animation delay based on index
        const delay = index * 0.1;
        
        const cardHTML = `
            <div class="col fade-in-up" style="animation-delay: ${delay}s;">
                <a href="${song.url}" target="_blank" class="text-decoration-none text-reset h-100 d-block">
                <div class="glass-card song-card p-3 h-100">
                    <div class="song-cover-container">
                        <img src="${song.cover}" alt="${song.title} Cover" class="song-cover">
                        <div class="play-overlay">
                            <div class="play-btn"><i class="bi bi-play-fill"></i></div>
                        </div>
                    </div>
                    <h6 class="fw-bold mb-1 text-truncate" title="${song.title}">${song.title}</h6>
                    <p class="small text-muted mb-2 text-truncate" title="${song.artist}">${song.artist}</p>
                    <div class="d-flex justify-content-between align-items-center mt-auto">
                        <span class="badge bg-secondary bg-opacity-25 text-body text-truncate" style="max-width: 60px;" title="${song.genre}">${song.genre}</span>
                        <span class="small text-muted"><i class="bi bi-clock me-1"></i>${song.duration}</span>
                    </div>
                </div>
                </a>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', cardHTML);
    });
    
    // Scroll to results slightly
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
