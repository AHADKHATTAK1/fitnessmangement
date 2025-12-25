// Mobile Navigation Toggle
document.addEventListener('DOMContentLoaded', function () {
    // Create mobile nav toggle button if it doesn't exist
    const existingToggle = document.querySelector('.mobile-nav-toggle');
    if (!existingToggle) {
        const toggle = document.createElement('button');
        toggle.className = 'mobile-nav-toggle';
        toggle.setAttribute('aria-label', 'Toggle navigation');
        toggle.innerHTML = `
            <span></span>
            <span></span>
            <span></span>
        `;
        document.body.prepend(toggle);
    }

    // Create overlay if it doesn't exist
    let overlay = document.querySelector('.sidebar-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        document.body.append(overlay);
    }

    // Get sidebar
    const sidebar = document.querySelector('.sidebar') || document.querySelector('nav');
    const toggleBtn = document.querySelector('.mobile-nav-toggle');

    if (!sidebar) {
        console.warn('No sidebar found for mobile navigation');
        return;
    }

    // Add sidebar class if not present
    if (!sidebar.classList.contains('sidebar')) {
        sidebar.classList.add('sidebar');
    }

    // Toggle menu function
    function toggleMenu() {
        sidebar.classList.toggle('active');
        overlay.classList.toggle('active');
        document.body.style.overflow = sidebar.classList.contains('active') ? 'hidden' : '';
    }

    // Event listeners
    if (toggleBtn) {
        toggleBtn.addEventListener('click', toggleMenu);
    }

    overlay.addEventListener('click', toggleMenu);

    // Close menu when clicking nav link on mobile
    const navLinks = sidebar.querySelectorAll('a');
    navLinks.forEach(link => {
        link.addEventListener('click', function () {
            if (window.innerWidth < 768) {
                toggleMenu();
            }
        });
    });

    // Close menu on window resize to desktop
    window.addEventListener('resize', function () {
        if (window.innerWidth >= 768) {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
});

// Prevent zoom on input focus (iOS)
document.addEventListener('touchstart', function () { }, { passive: true });
