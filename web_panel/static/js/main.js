/**
 * Main JavaScript file for YouTube Bot Developer Panel
 * Contains common functions and utilities used across all pages
 */

// Global variables
let notificationToast = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializePanel();
});

/**
 * Initialize the developer panel
 */
function initializePanel() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Set up auto-refresh for dashboard
    if (window.location.pathname === '/' || window.location.pathname.includes('dashboard')) {
        setInterval(refreshDashboardData, 30000); // Refresh every 30 seconds
    }

    // Set up form validation
    setupFormValidation();
    
    // Set up keyboard shortcuts
    setupKeyboardShortcuts();
    
    console.log('YouTube Bot Developer Panel initialized');
}

/**
 * Test YouTube service functionality
 */
function testYouTubeService() {
    showNotification('Тестування YouTube сервісу...', 'info');
    
    fetch('/api/test-youtube')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showNotification('YouTube сервіс працює правильно!', 'success');
            } else {
                showNotification('Помилка YouTube сервісу: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error testing YouTube service:', error);
            showNotification('Помилка тестування YouTube сервісу', 'error');
        });
}

/**
 * Restart bot functionality
 */
function restartBot() {
    if (!confirm('Ви впевнені, що хочете перезапустити бота? Це може зайняти кілька хвилин.')) {
        return;
    }
    
    showNotification('Надсилання сигналу перезапуску...', 'info');
    
    fetch('/api/restart-bot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification('Сигнал перезапуску надіслано!', 'success');
        } else {
            showNotification('Помилка перезапуску: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error restarting bot:', error);
        showNotification('Помилка перезапуску бота', 'error');
    });
}

/**
 * Show notification toast
 * @param {string} message - The message to display
 * @param {string} type - The type of notification (success, error, info, warning)
 */
function showNotification(message, type = 'info') {
    // Remove existing notification
    if (notificationToast) {
        notificationToast.dispose();
    }

    // Create notification element
    const toastContainer = getOrCreateToastContainer();
    const toastId = 'toast-' + Date.now();
    
    let iconClass = 'fas fa-info-circle';
    let bgClass = 'bg-primary';
    
    switch (type) {
        case 'success':
            iconClass = 'fas fa-check-circle';
            bgClass = 'bg-success';
            break;
        case 'error':
            iconClass = 'fas fa-exclamation-circle';
            bgClass = 'bg-danger';
            break;
        case 'warning':
            iconClass = 'fas fa-exclamation-triangle';
            bgClass = 'bg-warning';
            break;
        case 'info':
        default:
            iconClass = 'fas fa-info-circle';
            bgClass = 'bg-info';
            break;
    }
    
    const toastHTML = `
        <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="${iconClass} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    const toastElement = document.getElementById(toastId);
    notificationToast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: type === 'error' ? 8000 : 5000
    });
    
    notificationToast.show();
    
    // Clean up after toast is hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

/**
 * Get or create toast container
 */
function getOrCreateToastContainer() {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    return container;
}

/**
 * Refresh dashboard data
 */
function refreshDashboardData() {
    if (typeof loadDashboardData === 'function') {
        loadDashboardData();
    }
}

/**
 * Setup form validation
 */
function setupFormValidation() {
    // Add validation to all forms with .needs-validation class
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                showNotification('Будь ласка, заповніть всі обов\'язкові поля', 'warning');
            }
            form.classList.add('was-validated');
        });
    });
}

/**
 * Setup keyboard shortcuts
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(event) {
        // Ctrl/Cmd + S - Save configuration
        if ((event.ctrlKey || event.metaKey) && event.key === 's') {
            event.preventDefault();
            if (typeof saveConfiguration === 'function') {
                saveConfiguration();
            }
        }
        
        // Ctrl/Cmd + R - Refresh data
        if ((event.ctrlKey || event.metaKey) && event.key === 'r') {
            event.preventDefault();
            if (typeof refreshUsers === 'function') {
                refreshUsers();
            } else if (typeof loadDashboardData === 'function') {
                loadDashboardData();
            }
        }
        
        // F5 - Refresh page data (not browser refresh)
        if (event.key === 'F5') {
            event.preventDefault();
            location.reload();
        }
        
        // Escape - Close modals
        if (event.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            });
        }
    });
}

/**
 * Format file size in human readable format
 * @param {number} bytes - Size in bytes
 * @returns {string} Formatted size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Format duration in human readable format
 * @param {number} seconds - Duration in seconds
 * @returns {string} Formatted duration
 */
function formatDuration(seconds) {
    if (!seconds) return '0:00';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;
    
    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    } else {
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
}

/**
 * Format date in localized format
 * @param {string|Date} date - Date to format
 * @returns {string} Formatted date
 */
function formatDate(date) {
    if (!date) return 'Невідомо';
    
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    
    if (isNaN(dateObj.getTime())) return 'Невідомо';
    
    return dateObj.toLocaleDateString('uk-UA', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Format number with thousands separators
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
function formatNumber(num) {
    return new Intl.NumberFormat('uk-UA').format(num);
}

/**
 * Debounce function to limit API calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
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

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise} Promise that resolves when text is copied
 */
function copyToClipboard(text) {
    return navigator.clipboard.writeText(text).then(() => {
        showNotification('Скопійовано в буфер обміну!', 'success');
    }).catch(err => {
        console.error('Failed to copy text: ', err);
        showNotification('Помилка копіювання', 'error');
    });
}

/**
 * Download data as file
 * @param {string} data - Data to download
 * @param {string} filename - Name of the file
 * @param {string} type - MIME type of the file
 */
function downloadFile(data, filename, type = 'text/plain') {
    const blob = new Blob([data], { type: type });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

/**
 * Validate URL format
 * @param {string} url - URL to validate
 * @returns {boolean} True if URL is valid
 */
function isValidUrl(url) {
    try {
        new URL(url);
        return true;
    } catch (e) {
        return false;
    }
}

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} True if email is valid
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Get relative time string
 * @param {string|Date} date - Date to compare
 * @returns {string} Relative time string
 */
function getRelativeTime(date) {
    const now = new Date();
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    const diffInSeconds = Math.floor((now - dateObj) / 1000);
    
    if (diffInSeconds < 60) return 'щойно';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} хв тому`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} год тому`;
    if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)} дн тому`;
    
    return formatDate(dateObj);
}

/**
 * Handle API errors consistently
 * @param {Response} response - Fetch response object
 * @returns {Promise} Promise that resolves with JSON data or rejects with error
 */
function handleApiResponse(response) {
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
}

/**
 * Make API call with error handling
 * @param {string} url - API endpoint URL
 * @param {Object} options - Fetch options
 * @returns {Promise} Promise that resolves with API data
 */
function apiCall(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    return fetch(url, mergedOptions)
        .then(handleApiResponse)
        .catch(error => {
            console.error('API call failed:', error);
            showNotification('Помилка з\'єднання з сервером', 'error');
            throw error;
        });
}

// Export functions for use in other scripts
window.YouTubeBotPanel = {
    showNotification,
    testYouTubeService,
    restartBot,
    formatFileSize,
    formatDuration,
    formatDate,
    formatNumber,
    debounce,
    copyToClipboard,
    downloadFile,
    isValidUrl,
    isValidEmail,
    getRelativeTime,
    apiCall
};