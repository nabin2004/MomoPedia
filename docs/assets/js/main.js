// MomoPedia JavaScript - Enhanced Interactivity

document.addEventListener('DOMContentLoaded', function() {
    // Mobile Navigation Toggle
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
        });
    }
    
    // Smooth Scrolling for Internal Links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // AI Status Animation
    const aiPulse = document.querySelector('.ai-pulse');
    if (aiPulse) {
        // Random pulse timing for more organic feel
        setInterval(() => {
            aiPulse.style.animationDelay = Math.random() * 2 + 's';
        }, 3000);
    }
    
    // Article Card Hover Effects
    const articleCards = document.querySelectorAll('.article-card');
    articleCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(-4px)';
        });
    });
    
    // Feature Card Animation on Scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe feature cards
    document.querySelectorAll('.feature-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
    
    // Search Functionality (if search input exists)
    const searchInput = document.querySelector('#search-input');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function(e) {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(e.target.value);
            }, 300);
        });
    }
    
    // AI Content Generation Simulation
    function simulateAIGeneration(element) {
        if (!element) return;
        
        const originalText = element.textContent;
        let currentText = '';
        let currentIndex = 0;
        
        const typeInterval = setInterval(() => {
            if (currentIndex < originalText.length) {
                currentText += originalText[currentIndex];
                element.textContent = currentText + '|';
                currentIndex++;
            } else {
                clearInterval(typeInterval);
                element.textContent = originalText;
                // Add AI generated badge
                const badge = document.createElement('span');
                badge.className = 'ai-generated';
                badge.textContent = '✨ AI Generated';
                element.parentNode.appendChild(badge);
            }
        }, 50);
    }
    
    // Loading States for Dynamic Content
    function showLoadingState(element) {
        element.classList.add('loading');
        element.innerHTML = '<div class="loading-spinner"></div>';
    }
    
    function hideLoadingState(element, content) {
        element.classList.remove('loading');
        element.innerHTML = content;
    }
    
    // Theme Switching (for future dark mode)
    function initThemeToggle() {
        const themeToggle = document.querySelector('#theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', function() {
                document.body.classList.toggle('dark-theme');
                localStorage.setItem('theme', 
                    document.body.classList.contains('dark-theme') ? 'dark' : 'light'
                );
            });
        }
        
        // Load saved theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-theme');
        }
    }
    
    // Performance: Lazy load images
    const lazyImages = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    lazyImages.forEach(img => imageObserver.observe(img));
    
    // Analytics and User Interaction Tracking
    function trackUserInteraction(action, category, label) {
        if (typeof gtag !== 'undefined') {
            gtag('event', action, {
                'event_category': category,
                'event_label': label
            });
        }
        
        // Console log for development
        console.log(`User Interaction: ${action} - ${category} - ${label}`);
    }
    
    // Track button clicks
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function() {
            trackUserInteraction('click', 'button', this.textContent.trim());
        });
    });
    
    // Track article reads
    document.querySelectorAll('.read-more').forEach(link => {
        link.addEventListener('click', function() {
            trackUserInteraction('read', 'article', this.closest('.article-card').querySelector('.article-title').textContent);
        });
    });
    
    // Initialize all features
    initThemeToggle();
    
    console.log('MomoPedia JavaScript initialized successfully! 🥟');
});

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Search functionality (placeholder for future implementation)
function performSearch(query) {
    console.log('Searching for:', query);
    // This would integrate with the AI search system in the future
    
    if (query.length > 2) {
        // Show search results
        showSearchResults(query);
    } else {
        hideSearchResults();
    }
}

function showSearchResults(query) {
    // Placeholder for search results display
    console.log('Showing search results for:', query);
}

function hideSearchResults() {
    // Placeholder for hiding search results
    console.log('Hiding search results');
}

// Export functions for potential module usage
window.MomoPedia = {
    trackUserInteraction,
    performSearch,
    debounce,
    throttle
};