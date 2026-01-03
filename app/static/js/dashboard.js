
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');

    if (sidebar) {
        sidebar.classList.toggle('active');
    }
    if (overlay) {
        overlay.classList.toggle('active');
    }
}

// ========== NAVIGATION HIGHLIGHTING ==========

/**
 * Highlight the active navigation link based on current page
 */
function highlightActiveNav() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && href.includes(currentPage)) {
            link.classList.add('active');
        }
    });
}

// ========== LOGOUT FUNCTIONALITY ==========

/**
 * Handle user logout
 */
function handleLogout() {
    // Clear stored user data
    localStorage.removeItem('gap2growth_user');

    showToast('Logged out successfully', 'success');

    // Redirect to login page
    setTimeout(() => {
        window.location.href = 'login.html';
    }, 500);
}

// ========== USER SESSION ==========

/**
 * Load user information from session
 */
function loadUserInfo() {
    const user = JSON.parse(localStorage.getItem('gap2growth_user') || '{}');

    // Update profile elements if user data exists
    if (user.email) {
        const profileName = document.getElementById('profileName');
        const profileAvatar = document.getElementById('profileAvatar');
        const headerAvatar = document.getElementById('headerAvatar');

        // Extract initials from email
        const initials = user.email.charAt(0).toUpperCase();

        if (profileName) {
            profileName.textContent = user.email.split('@')[0];
        }

        if (profileAvatar) {
            profileAvatar.textContent = initials;
        }

        if (headerAvatar) {
            headerAvatar.textContent = initials;
        }
    }

    // Update greeting
    updateGreeting();
}

/**
 * Update greeting based on time of day
 */
function updateGreeting() {
    const greetingEl = document.getElementById('greetingText');
    if (!greetingEl) return;

    const hour = new Date().getHours();
    let greeting = 'Welcome!';

    if (hour < 12) {
        greeting = 'Good Morning!';
    } else if (hour < 17) {
        greeting = 'Good Afternoon!';
    } else {
        greeting = 'Good Evening!';
    }

    const user = JSON.parse(localStorage.getItem('gap2growth_user') || '{}');
    if (user.email) {
        const name = user.email.split('@')[0];
        greeting += ` ${name.charAt(0).toUpperCase() + name.slice(1)}`;
    }

    greetingEl.textContent = greeting;
}

/**
 * Update today's date display
 */
function updateTodayDate() {
    const dateEl = document.getElementById('todayDate');
    if (!dateEl) return;

    const options = { weekday: 'long', month: 'short', day: 'numeric', year: 'numeric' };
    dateEl.textContent = new Date().toLocaleDateString('en-US', options);
}

// ========== PROGRESS CIRCLE ==========

/**
 * Initialize progress circle animation
 */
function initProgressCircle() {
    const progressCircle = document.getElementById('progressCircle');
    if (!progressCircle) return;

    const percentage = parseInt(progressCircle.dataset.percentage) || 0;
    const valueEl = progressCircle.querySelector('.progress-value');

    // Animate the percentage
    let current = 0;
    const increment = percentage / 50;

    const timer = setInterval(() => {
        current += increment;
        if (current >= percentage) {
            current = percentage;
            clearInterval(timer);
        }

        if (valueEl) {
            valueEl.textContent = Math.round(current) + '%';
        }

        // Update circle gradient
        progressCircle.style.background = `conic-gradient(
            var(--primary-color) ${current * 3.6}deg,
            #e0e0e0 ${current * 3.6}deg
        )`;
    }, 30);
}

// ========== INITIALIZATION ==========

document.addEventListener('DOMContentLoaded', function () {
    // Sidebar toggle
    const menuToggle = document.querySelector('.menu-toggle');
    if (menuToggle) {
        menuToggle.addEventListener('click', toggleSidebar);
    }

    // Sidebar overlay click to close
    const overlay = document.querySelector('.sidebar-overlay');
    if (overlay) {
        overlay.addEventListener('click', toggleSidebar);
    }

    // Logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function (e) {
            e.preventDefault();
            handleLogout();
        });
    }

    // Highlight active nav
    highlightActiveNav();

    // Load user info
    loadUserInfo();

    // Update today's date
    updateTodayDate();

    // Initialize progress circle
    initProgressCircle();
});
