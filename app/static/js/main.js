/* Gap2Growth - Main JavaScript */

document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert:not(.persistent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    const cards = document.querySelectorAll('.card, .stat-card, .activity-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.05}s`;
        card.classList.add('fade-in');
    });

    document.querySelectorAll('.form-select').forEach(select => {
        select.addEventListener('change', function () {
            if (this.value) {
                this.classList.add('has-value');
            } else {
                this.classList.remove('has-value');
            }
        });
    });
});


const api = {
    async get(url) {
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.json();
        } catch (error) {
            console.error('API GET Error:', error);
            throw error;
        }
    },

    async post(url, data = {}) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.json();
        } catch (error) {
            console.error('API POST Error:', error);
            throw error;
        }
    }
};


// Mark a notification as read
function markNotificationRead(notificationId) {
    api.post(`/student/notifications/${notificationId}/read`)
        .then(() => {
            const item = document.querySelector(`[data-notification-id="${notificationId}"]`);
            if (item) item.classList.remove('unread');
        })
        .catch(err => console.error('Failed to mark notification as read:', err));
}

function markAllNotificationsRead() {
    api.post('/api/notifications/read-all')
        .then(() => {
            document.querySelectorAll('.notification-item.unread')
                .forEach(item => item.classList.remove('unread'));
            showToast('All notifications marked as read', 'success');
        })
        .catch(err => console.error('Failed to mark all notifications as read:', err));
}


// Start an activity
function startActivity(activityId) {
    api.post(`/student/activity/${activityId}/start`)
        .then(data => {
            if (data.success) {
                showToast('Activity started! Good luck!', 'success');
                sessionStorage.setItem('currentActivityLog', data.log_id);
                // Refresh the page to show updated status
                setTimeout(() => location.reload(), 1500);
            }
        })
        .catch(err => {
            console.error('Failed to start activity:', err);
            showToast('Failed to start activity. Please try again.', 'danger');
        });
}

function completeActivity(logId) {
    api.post(`/student/activity/${logId}/complete`)
        .then(data => {
            if (data.success) {
                showToast('Activity completed! Great job! 🎉', 'success');
                sessionStorage.removeItem('currentActivityLog');
                setTimeout(() => location.reload(), 1500);
            }
        })
        .catch(err => {
            console.error('Failed to complete activity:', err);
            showToast('Failed to complete activity. Please try again.', 'danger');
        });
}


// Show toast notification
function showToast(message, type = 'info') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; display: flex; flex-direction: column; gap: 10px;';
        document.body.appendChild(container);
    }


    const toast = document.createElement('div');
    toast.className = `toast-message toast-${type}`;


    const icons = {
        success: '✅',
        danger: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };

    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-text">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;

    toast.style.cssText = `
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 14px 18px;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        font-size: 14px;
        animation: slideIn 0.3s ease;
        border-left: 4px solid ${type === 'success' ? '#10b981' : type === 'danger' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#3b82f6'};
    `;

    container.appendChild(toast);


    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}


// Initialize toast styles
if (!document.querySelector('#toast-styles')) {
    const style = document.createElement('style');
    style.id = 'toast-styles';
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
        .toast-close {
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            color: #9ca3af;
            padding: 0;
            line-height: 1;
        }
        .toast-close:hover { color: #374151; }
    `;
    document.head.appendChild(style);
}


// Format time string
function formatTime(timeString) {
    if (!timeString) return '';
    const [hours, minutes] = timeString.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const hour12 = hour % 12 || 12;
    return `${hour12}:${minutes} ${ampm}`;
}


// Format duration in minutes
function formatDuration(minutes) {
    if (!minutes || minutes <= 0) return '0 mins';
    if (minutes < 60) return `${minutes} mins`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
}


// Show confirmation dialog
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}


// Delete item with confirmation
function deleteItem(url, itemName) {
    confirmAction(`Are you sure you want to delete ${itemName}?`, () => {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = url;
        document.body.appendChild(form);
        form.submit();
    });
}


// Debounce function
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


// Initialize table search
function initializeTableSearch(searchInputId, tableId) {
    const searchInput = document.getElementById(searchInputId);
    const table = document.getElementById(tableId);

    if (!searchInput || !table) return;

    searchInput.addEventListener('input', debounce(function (e) {
        const query = e.target.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(query) ? '' : 'none';
        });
    }, 200));
}


// Format relative time
function formatRelativeTime(dateString) {
    if (!dateString) return 'Just now';

    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

    return date.toLocaleDateString();
}


window.gap2growth = {
    api,
    showToast,
    formatTime,
    formatDuration,
    formatRelativeTime,
    confirmAction,
    debounce,
    startActivity,
    completeActivity,
    markNotificationRead,
    markAllNotificationsRead
};
