// Store the currently selected user role
let selectedRole = 'student';

// ========== ROLE SELECTION ==========

/**
 * Select a user role and update the UI
 * @param {string} role - The role to select ('student', 'teacher', 'admin')
 */
function selectRole(role) {
    selectedRole = role;

    // Get all role buttons and remove 'active' class
    const roleButtons = document.querySelectorAll('.role-btn');
    roleButtons.forEach(btn => btn.classList.remove('active'));

    // Add 'active' class to the clicked button
    const activeBtn = document.querySelector(`[data-role="${role}"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
    }

    // Update form for the selected role
    updateFormForRole(role);
}

/**
 * Update form elements based on selected role
 * @param {string} role - The selected role
 */
function updateFormForRole(role) {
    const emailInput = document.getElementById('email');
    const loginBtn = document.querySelector('.btn-login');

    if (emailInput) {
        emailInput.placeholder = 'Enter your email';
    }

    if (loginBtn) {
        loginBtn.textContent = `Login as ${role.charAt(0).toUpperCase() + role.slice(1)}`;
    }
}

// ========== PASSWORD VISIBILITY TOGGLE ==========

/**
 * Toggle password visibility in the input field
 */
function togglePassword() {
    const passwordInput = document.getElementById('password');
    const toggleIcon = document.querySelector('.password-toggle i');

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.classList.remove('bi-eye');
        toggleIcon.classList.add('bi-eye-slash');
    } else {
        passwordInput.type = 'password';
        toggleIcon.classList.remove('bi-eye-slash');
        toggleIcon.classList.add('bi-eye');
    }
}

// ========== FORM VALIDATION ==========

/**
 * Validate the email field
 * @returns {boolean} True if email is valid
 */
function validateEmail() {
    const emailInput = document.getElementById('email');
    const email = emailInput.value.trim();

    clearFieldError(emailInput);

    if (!email) {
        showFieldError(emailInput, 'Email is required');
        return false;
    }

    if (!isValidEmail(email)) {
        showFieldError(emailInput, 'Please enter a valid email address');
        return false;
    }

    return true;
}

/**
 * Validate the password field
 * @returns {boolean} True if password is valid
 */
function validatePasswordField() {
    const passwordInput = document.getElementById('password');
    const password = passwordInput.value;

    clearFieldError(passwordInput);

    if (!password) {
        showFieldError(passwordInput, 'Password is required');
        return false;
    }

    if (password.length < 6) {
        showFieldError(passwordInput, 'Password must be at least 6 characters');
        return false;
    }

    return true;
}

/**
 * Validate the entire login form
 * @returns {boolean} True if form is valid
 */
function validateLoginForm() {
    const isEmailValid = validateEmail();
    const isPasswordValid = validatePasswordField();
    return isEmailValid && isPasswordValid;
}

// ========== FORM SUBMISSION ==========
// NOTE: This will call actual backend API in Phase 3

/**
 * Handle login form submission
 * @param {Event} event - The form submit event
 */
function handleLogin(event) {
    event.preventDefault();

    if (!validateLoginForm()) {
        showToast('Please fix the errors in the form', 'error');
        return;
    }

    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const rememberMe = document.getElementById('rememberMe')?.checked || false;

    const loginBtn = document.querySelector('.btn-login');
    showButtonLoading(loginBtn, 'Signing in...');

    // TODO: Replace with actual API call in Phase 3
    // For now, show a message that backend is not connected
    setTimeout(() => {
        hideButtonLoading(loginBtn);

        // Store basic session for frontend navigation
        const userSession = {
            email: email,
            role: selectedRole,
            loggedIn: true
        };
        saveToStorage('gap2growth_user', userSession);

        showToast('Login successful!', 'success');

        // Redirect to dashboard
        setTimeout(() => {
            const dashboards = {
                student: 'student_dashboard.html',
                teacher: 'teacher_dashboard.html',
                admin: 'admin_dashboard.html'
            };
            window.location.href = dashboards[selectedRole] || 'student_dashboard.html';
        }, 500);

    }, 1000);
}

// ========== GOOGLE LOGIN ==========
// NOTE: This will use Firebase Google Auth in Phase 3

/**
 * Handle Google login button click
 */
function handleGoogleLogin() {
    const googleBtn = document.querySelector('.btn-google');
    showButtonLoading(googleBtn, 'Connecting to Google...');

    // TODO: Replace with Firebase Google Auth in Phase 3
    setTimeout(() => {
        hideButtonLoading(googleBtn);
        showToast('Google login will be available after backend integration', 'info');
    }, 1000);
}

// ========== INPUT EVENT LISTENERS ==========

function setupInputListeners() {
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    if (emailInput) {
        emailInput.addEventListener('blur', validateEmail);
        emailInput.addEventListener('input', () => {
            clearFieldError(emailInput);
        });
    }

    if (passwordInput) {
        passwordInput.addEventListener('blur', validatePasswordField);
        passwordInput.addEventListener('input', () => {
            clearFieldError(passwordInput);
        });
    }
}

// ========== INITIALIZATION ==========

document.addEventListener('DOMContentLoaded', function () {
    setupInputListeners();

    // Role button click handlers
    const roleButtons = document.querySelectorAll('.role-btn');
    roleButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            selectRole(this.dataset.role);
        });
    });

    // Form submit handler
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    // Google login button
    const googleBtn = document.querySelector('.btn-google');
    if (googleBtn) {
        googleBtn.addEventListener('click', handleGoogleLogin);
    }

    // Password toggle
    const passwordToggle = document.querySelector('.password-toggle');
    if (passwordToggle) {
        passwordToggle.addEventListener('click', togglePassword);
    }
});
