/**
 * VolleyScore - Shared JavaScript Utilities
 * Common functions used across all pages
 */

// ============================================
// SOCKET CONNECTION
// ============================================

let socketInstance = null;
let connectionCallbacks = [];
let updateCallbacks = [];

function connectSocket(onUpdate, onConnect) {
    if (socketInstance) {
        socketInstance.off('score_update');
        socketInstance.off('connect');
    }

    socketInstance = io();

    socketInstance.on('connect', () => {
        console.log('Connected to WebSocket');
        if (onConnect) onConnect();
        connectionCallbacks.forEach(cb => cb(true));
    });

    socketInstance.on('score_update', function(data) {
        updateCallbacks.forEach(cb => cb(data));
        if (onUpdate) onUpdate(data);
    });

    socketInstance.on('disconnect', () => {
        console.log('Disconnected from WebSocket');
        connectionCallbacks.forEach(cb => cb(false));
    });
}

function getSocket() {
    return socketInstance;
}

function onConnectionChange(callback) {
    connectionCallbacks.push(callback);
}

function onScoreUpdate(callback) {
    updateCallbacks.push(callback);
}

// ============================================
// TIMER FUNCTIONS
// ============================================

function formatTime(seconds) {
    const mins = Math.floor(Math.max(0, seconds) / 60);
    const secs = Math.max(0, seconds) % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function calculateElapsedTime(timerState) {
    if (!timerState) return 0;

    if (!timerState.timerStarted) {
        return 0;
    }

    if (timerState.timerPaused && timerState.timerPausedTimestamp) {
        return timerState.accumulatedTime + Math.floor(timerState.timerPausedTimestamp - timerState.timerStartTimestamp);
    }

    if (timerState.timerStartTimestamp) {
        return timerState.accumulatedTime + Math.floor(Date.now() / 1000 - timerState.timerStartTimestamp);
    }

    return timerState.accumulatedTime;
}

function updateTimerDisplay(displayElement, timerState) {
    if (!displayElement) return;

    const elapsed = calculateElapsedTime(timerState);
    displayElement.textContent = formatTime(elapsed);
}

function startTimerInterval(displayElement, timerState, getTimerState) {
    if (displayElement.timerInterval) {
        clearInterval(displayElement.timerInterval);
    }

    function update() {
        const state = getTimerState ? getTimerState() : timerState;
        updateTimerDisplay(displayElement, state);
    }

    update();
    displayElement.timerInterval = setInterval(update, 1000);
}

function stopTimerInterval(displayElement) {
    if (displayElement && displayElement.timerInterval) {
        clearInterval(displayElement.timerInterval);
        displayElement.timerInterval = null;
    }
}

// ============================================
// SCORE ANIMATION
// ============================================

function animateScoreChange(elementId, newValue, animate = true) {
    const element = document.getElementById(elementId);
    if (!element) return;

    let currentSpan = element.querySelector('.score-anim-number.is-current');

    // If no currentSpan (initial load), create one
    if (!currentSpan) {
        currentSpan = document.createElement('span');
        currentSpan.className = 'score-anim-number is-current';
        currentSpan.textContent = newValue;
        element.appendChild(currentSpan);
        return;
    }

    const oldValue = parseInt(currentSpan.textContent);
    if (oldValue === newValue) return;

    // Remove any old, non-current spans
    element.querySelectorAll('.score-anim-number:not(.is-current)').forEach(span => span.remove());

    // Create the new span
    const newSpan = document.createElement('span');
    newSpan.className = 'score-anim-number';
    newSpan.textContent = newValue;

    // Determine direction and initial positions
    const direction = newValue > oldValue ? 'up' : 'down';
    newSpan.style.transform = direction === 'up' ? 'translateY(100%)' : 'translateY(-100%)';

    // Append new span
    element.appendChild(newSpan);

    // Force reflow
    void newSpan.offsetWidth;

    // Start the animation
    if (animate) {
        currentSpan.style.transform = direction === 'up' ? 'translateY(-100%)' : 'translateY(100%)';
        newSpan.style.transform = 'translateY(0)';
    }

    // Update classes
    currentSpan.classList.remove('is-current');
    newSpan.classList.add('is-current');

    // Clean up after transition
    currentSpan.addEventListener('transitionend', () => {
        currentSpan.remove();
    }, { once: true });
}

// ============================================
// TIMEOUT DOTS
// ============================================

function getTimeoutDotsHTML(remaining) {
    const used = 2 - remaining;
    return "●".repeat(Math.max(0, used)) + "○".repeat(Math.max(0, remaining));
}

function updateTimeoutDotsDisplay(dotsElement, countElement, count) {
    if (dotsElement) {
        dotsElement.textContent = getTimeoutDotsHTML(count);
    }
    if (countElement) {
        countElement.textContent = `(${count}/2)`;
    }
}

// ============================================
// FORMATTING UTILITIES
// ============================================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================
// TOAST NOTIFICATIONS
// ============================================

const toastContainer = createToastContainer();

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 10px;
        pointer-events: none;
    `;
    document.body.appendChild(container);
    return container;
}

function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.style.cssText = `
        background: #2a2a2a;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        font-family: system-ui, -apple-system, sans-serif;
        font-size: 14px;
        display: flex;
        align-items: center;
        gap: 10px;
        animation: slideIn 0.3s ease-out;
        pointer-events: auto;
        max-width: 300px;
    `;

    // Icon based on type
    let icon = '';
    if (type === 'success') {
        icon = '✓';
        toast.style.borderLeft = '4px solid #22c55e';
    } else if (type === 'error') {
        icon = '✕';
        toast.style.borderLeft = '4px solid #ef4444';
    } else if (type === 'warning') {
        icon = '!';
        toast.style.borderLeft = '4px solid #f97316';
    } else {
        icon = 'i';
        toast.style.borderLeft = '4px solid #3b82f6';
    }

    toast.innerHTML = `<span style="font-weight: bold;">${icon}</span> ${escapeHtml(message)}`;

    toastContainer.appendChild(toast);

    // Add animation keyframes if not exists
    if (!document.getElementById('toast-animation')) {
        const style = document.createElement('style');
        style.id = 'toast-animation';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out forwards';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ============================================
// CONNECTION STATUS
// ============================================

function createConnectionIndicator(container) {
    const indicator = document.createElement('div');
    indicator.id = 'connection-indicator';
    indicator.style.cssText = `
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #ef4444;
        transition: background 0.3s;
        box-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
    `;

    indicator.setConnected = function(connected) {
        if (connected) {
            this.style.background = '#22c55e';
            this.style.boxShadow = '0 0 8px rgba(34, 197, 94, 0.5)';
        } else {
            this.style.background = '#ef4444';
            this.style.boxShadow = '0 0 8px rgba(239, 68, 68, 0.5)';
        }
    };

    onConnectionChange((connected) => {
        indicator.setConnected(connected);
    });

    // Check initial connection
    if (socketInstance && socketInstance.connected) {
        indicator.setConnected(true);
    }

    return indicator;
}

// ============================================
// MODAL HELPERS
// ============================================

function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

function setupModalCloseOnOverlay(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    }
}

// ============================================
// FORM UTILITIES
// ============================================

function createFormData(fields) {
    const formData = new FormData();
    Object.entries(fields).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
            formData.append(key, value);
        }
    });
    return formData;
}

async function apiRequest(url, method = 'POST', data = {}) {
    const options = {
        method,
        headers: {}
    };

    if (method === 'POST') {
        options.body = createFormData(data);
    }

    try {
        const response = await fetch(url, options);
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// ============================================
// EXPORT FUNCTIONS
// ============================================

function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// ============================================
// INITIALIZATION HELPERS
// ============================================

async function fetchCurrentState() {
    try {
        const response = await fetch('/current');
        return await response.json();
    } catch (error) {
        console.error('Failed to fetch current state:', error);
        return null;
    }
}

// Initialize socket connection on page load
document.addEventListener('DOMContentLoaded', () => {
    if (!socketInstance) {
        connectSocket();
    }
});