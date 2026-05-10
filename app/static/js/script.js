/**
 * Main application JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Job Match application loaded');
    
    // Initialize tooltips, modals, etc.
    initializeApp();
});

/**
 * Initialize application
 */
function initializeApp() {
    // Add your initialization code here
    console.log('App initialized');
}

/**
 * Fetch data from API
 */
async function fetchAPI(endpoint, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(endpoint, finalOptions);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    const container = document.querySelector('main');
    if (container) {
        container.insertBefore(alert, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }
}

/**
 * API helper functions
 */
const API = {
    /**
     * GET request
     */
    get: async (endpoint) => {
        return fetchAPI(endpoint, { method: 'GET' });
    },
    
    /**
     * POST request
     */
    post: async (endpoint, data) => {
        return fetchAPI(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    /**
     * PUT request
     */
    put: async (endpoint, data) => {
        return fetchAPI(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    /**
     * DELETE request
     */
    delete: async (endpoint) => {
        return fetchAPI(endpoint, { method: 'DELETE' });
    }
};
