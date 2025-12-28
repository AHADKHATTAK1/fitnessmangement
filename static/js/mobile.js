// Mobile UI JavaScript - Bottom Navigation
document.addEventListener('DOMContentLoaded', function () {
    // Only run on mobile
    if (window.innerWidth <= 768) {
        initMobileUI();
    }
});

function initMobileUI() {
    // Add mobile status bar
    if (!document.querySelector('.mobile-status-bar')) {
        const statusBar = createStatusBar();
        document.body.insertBefore(statusBar, document.body.firstChild);
    }

    // Add bottom navigation
    if (!document.querySelector('.mobile-bottom-nav')) {
        const bottomNav = createBottomNav();
        document.body.appendChild(bottomNav);
    }

    // Add gym selector at bottom
    if (!document.querySelector('.gym-selector-bottom')) {
        const gymSelect = createGymSelector();
        document.body.appendChild(gymSelect);
    }

    // Update active nav item based on current page
    updateActiveNav();
}

function createStatusBar() {
    const statusBar = document.createElement('div');
    statusBar.className = 'mobile-status-bar';

    const time = new Date().toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    });

    statusBar.innerHTML = `
        <div class="status-bar-time">${time}</div>
        <div class="status-bar-icons">
            <span>📶</span>
            <span>🔋</span>
        </div>
    `;

    // Update time every minute
    setInterval(() => {
        const newTime = new Date().toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        });
        statusBar.querySelector('.status-bar-time').textContent = newTime;
    }, 60000);

    return statusBar;
}

function createBottomNav() {
    const nav = document.createElement('nav');
    nav.className = 'mobile-bottom-nav';

    const navItems = [
        { icon: '🏠', label: 'Home', url: '/dashboard' },
        { icon: '➕', label: 'Add', url: '/add_member' },
        { icon: '💰', label: 'Fees', url: '/fees' },
        { icon: '📊', label: 'Stats', url: '/reports' },
        { icon: '💎', label: 'Plan', url: '/subscription_plans' },
        { icon: '⚙️', label: 'More', url: '/settings' }
    ];

    navItems.forEach(item => {
        const link = document.createElement('a');
        link.href = item.url;
        link.className = 'nav-item';
        link.innerHTML = `
            <div class="nav-icon">${item.icon}</div>
            <div class="nav-label">${item.label}</div>
        `;
        nav.appendChild(link);
    });

    return nav;
}

function createGymSelector() {
    const selector = document.createElement('div');
    selector.className = 'gym-selector-bottom';

    // Get gym name from context or default
    const gymName = document.querySelector('[data-gym-name]')?.dataset.gymName || 'Gym';

    selector.innerHTML = `
        <select onchange="location.href='/switch_gym?id=' + this.value">
            <option selected>${gymName} ▼</option>
        </select>
    `;

    return selector;
}

function updateActiveNav() {
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.mobile-bottom-nav .nav-item');

    navItems.forEach(item => {
        const href = item.getAttribute('href');
        if (currentPath === href || currentPath.startsWith(href)) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}

// Pull to refresh functionality
let startY = 0;
let isPulling = false;

document.addEventListener('touchstart', function (e) {
    startY = e.touches[0].clientY;
});

document.addEventListener('touchmove', function (e) {
    const currentY = e.touches[0].clientY;
    const diff = currentY - startY;

    if (diff > 0 && window.scrollY === 0) {
        isPulling = true;
    }
});

document.addEventListener('touchend', function () {
    if (isPulling) {
        location.reload();
    }
    isPulling = false;
});

// Haptic feedback for touch
document.querySelectorAll('.mobile-btn-primary, .nav-item').forEach(el => {
    el.addEventListener('touchstart', function () {
        if ('vibrate' in navigator) {
            navigator.vibrate(10);
        }
    });
});
