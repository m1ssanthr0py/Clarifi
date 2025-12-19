// API base URL
const API_BASE = '';

// DOM elements
const logFileSelect = document.getElementById('log-file');
const linesSelect = document.getElementById('lines');
const searchInput = document.getElementById('search');
const levelSelect = document.getElementById('level');
const refreshBtn = document.getElementById('refresh-btn');
const autoRefreshCheckbox = document.getElementById('auto-refresh');
const logEntriesDiv = document.getElementById('log-entries');
const statsFiles = document.getElementById('stats-files');
const statsSize = document.getElementById('stats-size');
const statsLogs = document.getElementById('stats-logs');

// Auto-refresh interval
let autoRefreshInterval = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadLogFiles();
    loadStats();
    loadLogs();
    
    // Event listeners
    refreshBtn.addEventListener('click', () => loadLogs());
    logFileSelect.addEventListener('change', () => loadLogs());
    linesSelect.addEventListener('change', () => loadLogs());
    levelSelect.addEventListener('change', () => loadLogs());
    
    // Debounced search
    let searchTimeout;
    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => loadLogs(), 500);
    });
    
    // Auto-refresh toggle
    autoRefreshCheckbox.addEventListener('change', (e) => {
        if (e.target.checked) {
            startAutoRefresh();
        } else {
            stopAutoRefresh();
        }
    });
});

// Load available log files
async function loadLogFiles() {
    try {
        const response = await fetch(`${API_BASE}/api/files`);
        const data = await response.json();
        
        // Clear existing options (except the first one)
        while (logFileSelect.options.length > 1) {
            logFileSelect.remove(1);
        }
        
        // Add log files
        data.files.forEach(file => {
            if (file.path !== 'all-remote.log') {
                const option = document.createElement('option');
                option.value = file.path;
                option.textContent = `${file.path} (${formatBytes(file.size)})`;
                logFileSelect.appendChild(option);
            }
        });
    } catch (error) {
        console.error('Error loading log files:', error);
    }
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/api/stats`);
        const data = await response.json();
        
        statsFiles.textContent = `Files: ${data.total_files}`;
        statsSize.textContent = `Size: ${data.total_size_mb} MB`;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load logs
async function loadLogs() {
    const file = logFileSelect.value;
    const lines = linesSelect.value;
    const search = searchInput.value;
    const level = levelSelect.value;
    
    // Show loading
    logEntriesDiv.innerHTML = '<div class="loading">Loading logs</div>';
    
    try {
        const params = new URLSearchParams({
            file: file,
            lines: lines,
            search: search,
            level: level
        });
        
        const response = await fetch(`${API_BASE}/api/logs?${params}`);
        const data = await response.json();
        
        // Update stats
        statsLogs.textContent = `Logs: ${data.count}`;
        
        // Display logs
        if (data.logs.length === 0) {
            logEntriesDiv.innerHTML = '<div class="no-logs">No logs found</div>';
            return;
        }
        
        logEntriesDiv.innerHTML = '';
        data.logs.forEach(log => {
            const entry = createLogEntry(log);
            logEntriesDiv.appendChild(entry);
        });
        
        // Auto-scroll to bottom
        logEntriesDiv.scrollTop = logEntriesDiv.scrollHeight;
        
    } catch (error) {
        console.error('Error loading logs:', error);
        logEntriesDiv.innerHTML = '<div class="no-logs">Error loading logs</div>';
    }
}

// Create log entry element
function createLogEntry(log) {
    const div = document.createElement('div');
    div.className = 'log-entry';
    
    // Try to detect log level from message
    const logLevel = detectLogLevel(log.raw);
    if (logLevel) {
        div.classList.add(`level-${logLevel}`);
    }
    
    div.innerHTML = `
        <span class="col-time">${escapeHtml(log.timestamp)}</span>
        <span class="col-host">${escapeHtml(log.hostname)}</span>
        <span class="col-tag">${escapeHtml(log.tag)}</span>
        <span class="col-message">${escapeHtml(log.message)}</span>
    `;
    
    return div;
}

// Detect log level from message
function detectLogLevel(message) {
    const lower = message.toLowerCase();
    if (lower.includes('emerg')) return 'emerg';
    if (lower.includes('alert')) return 'alert';
    if (lower.includes('crit')) return 'crit';
    if (lower.includes('err') || lower.includes('error')) return 'err';
    if (lower.includes('warn')) return 'warning';
    if (lower.includes('notice')) return 'notice';
    if (lower.includes('info')) return 'info';
    if (lower.includes('debug')) return 'debug';
    return null;
}

// Start auto-refresh
function startAutoRefresh() {
    if (autoRefreshInterval) return;
    autoRefreshInterval = setInterval(() => {
        loadLogs();
        loadStats();
    }, 5000);
}

// Stop auto-refresh
function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

// Utility functions
function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
