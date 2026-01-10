// Loading Animations & UI Enhancements

// Auto-hide flash messages with toast animation
document.addEventListener('DOMContentLoaded', function () {
    // Add toast class to flash messages
    const flashes = document.querySelectorAll('.alert, .flash-message');
    flashes.forEach(flash => {
        flash.classList.add('toast');

        // Auto remove after 3 seconds
        setTimeout(() => {
            flash.remove();
        }, 3000);
    });

    // Fade in on scroll observer
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    // Observe all elements with fade-in-scroll class
    document.querySelectorAll('.fade-in-scroll').forEach(el => {
        observer.observe(el);
    });

    // Add smooth hover to all cards
    document.querySelectorAll('.card, .member-card-3d').forEach(card => {
        if (!card.classList.contains('smooth-hover')) {
            card.classList.add('smooth-hover');
        }
    });
});

// Button loading state
function setButtonLoading(button, loading = true) {
    if (loading) {
        button.classList.add('btn-loading');
        button.disabled = true;
    } else {
        button.classList.remove('btn-loading');
        button.disabled = false;
    }
}

// Show loading overlay
function showLoadingOverlay(message = 'Loading...') {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.id = 'loadingOverlay';
    overlay.innerHTML = `
        <div style="text-align: center;">
            <div class="spinner" style="margin: 0 auto 1rem"></div>
            <p style="color: white; font-size: 1.1rem;">${message}</p>
        </div>
    `;
    document.body.appendChild(overlay);
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.animation = 'fadeOut 0.2s ease-out';
        setTimeout(() => overlay.remove(), 200);
    }
}

// Show toast notification
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div style="font-size: 1.5rem;">
                ${type === 'success' ? '✅' : type === 'error' ? '❌' : '⚠️'}
            </div>
            <div style="flex: 1;">
                <p style="margin: 0; font-weight: 600;">${message}</p>
            </div>
        </div>
    `;
    document.body.appendChild(toast);

    setTimeout(() => toast.remove(), 3000);
}

// Confetti on success
function triggerConfetti() {
    const colors = ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ec4899'];

    for (let i = 0; i < 50; i++) {
        setTimeout(() => {
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            confetti.style.left = Math.random() * 100 + 'vw';
            confetti.style.background = colors[Math.floor(Math.random() * colors.length)];
            confetti.style.animationDelay = Math.random() * 0.5 + 's';
            confetti.style.animationDuration = (Math.random() * 2 + 2) + 's';
            document.body.appendChild(confetti);

            setTimeout(() => confetti.remove(), 3000);
        }, i * 50);
    }
}

// Form submission with loading state
document.addEventListener('submit', function (e) {
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');

    if (submitBtn && !submitBtn.classList.contains('no-loading')) {
        setButtonLoading(submitBtn, true);

        // Re-enable after 5 seconds as fallback
        setTimeout(() => {
            setButtonLoading(submitBtn, false);
        }, 5000);
    }
});

// Image lazy loading with placeholder
document.querySelectorAll('img[data-src]').forEach(img => {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const image = entry.target;
                image.src = image.dataset.src;
                image.classList.add('fade-in-scroll');
                observer.unobserve(image);
            }
        });
    });

    observer.observe(img);
});

// Page transition on load
window.addEventListener('load', function () {
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.3s ease-out';
        document.body.style.opacity = '1';
    }, 10);
});

// Smooth scroll for anchor links
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

console.log('✨ Loading animations initialized');
