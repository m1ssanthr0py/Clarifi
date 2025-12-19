from flask import Flask, render_template, jsonify, request
import os
import glob
from datetime import datetime
import re

app = Flask(__name__)

LOG_DIR = '/var/log/remote'

def parse_syslog_line(line):
    """Parse a syslog line and extract components"""
    # RFC 3164 format: <priority>timestamp hostname tag: message
    # or simplified: timestamp hostname tag: message
    try:
        # Match timestamp, hostname, tag, and message
        pattern = r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+(\S+?):\s*(.*)'
        match = re.match(pattern, line.strip())
        
        if match:
            timestamp, hostname, tag, message = match.groups()
            return {
                'timestamp': timestamp,
                'hostname': hostname,
                'tag': tag,
                'message': message,
                'raw': line.strip()
            }
        else:
            # If parsing fails, return raw line
            return {
                'timestamp': '',
                'hostname': '',
                'tag': '',
                'message': line.strip(),
                'raw': line.strip()
            }
    except Exception:
        return {
            'timestamp': '',
            'hostname': '',
            'tag': '',
            'message': line.strip(),
            'raw': line.strip()
        }

def get_log_files():
    """Get list of all log files"""
    log_files = []
    
    # Get all log files recursively
    for filepath in glob.glob(os.path.join(LOG_DIR, '**/*.log'), recursive=True):
        relative_path = os.path.relpath(filepath, LOG_DIR)
        size = os.path.getsize(filepath)
        modified = os.path.getmtime(filepath)
        
        log_files.append({
            'path': relative_path,
            'full_path': filepath,
            'size': size,
            'modified': datetime.fromtimestamp(modified).strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # Sort by modification time (newest first)
    log_files.sort(key=lambda x: x['modified'], reverse=True)
    return log_files

def read_log_file(filepath, lines=100, search='', level=''):
    """Read log file and return parsed entries"""
    if not os.path.exists(filepath):
        return []
    
    try:
        with open(filepath, 'r') as f:
            all_lines = f.readlines()
        
        # Get last N lines
        recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        # Parse lines
        parsed_lines = []
        for line in recent_lines:
            if line.strip():
                parsed = parse_syslog_line(line)
                
                # Apply filters
                if search and search.lower() not in parsed['raw'].lower():
                    continue
                    
                if level and level.lower() not in parsed['raw'].lower():
                    continue
                
                parsed_lines.append(parsed)
        
        return parsed_lines
    except Exception as e:
        return [{'timestamp': '', 'hostname': '', 'tag': '', 'message': f'Error reading file: {str(e)}', 'raw': ''}]

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/files')
def api_files():
    """Get list of log files"""
    files = get_log_files()
    return jsonify({'files': files})

@app.route('/api/logs')
def api_logs():
    """Get log entries from a specific file"""
    file_path = request.args.get('file', 'all-remote.log')
    lines = int(request.args.get('lines', 100))
    search = request.args.get('search', '')
    level = request.args.get('level', '')
    
    # Build full path
    if file_path.startswith('/'):
        full_path = file_path
    else:
        full_path = os.path.join(LOG_DIR, file_path)
    
    # Security check - ensure path is within LOG_DIR
    if not os.path.abspath(full_path).startswith(os.path.abspath(LOG_DIR)):
        return jsonify({'error': 'Invalid file path'}), 403
    
    logs = read_log_file(full_path, lines, search, level)
    
    return jsonify({
        'file': file_path,
        'count': len(logs),
        'logs': logs
    })

@app.route('/api/stats')
def api_stats():
    """Get statistics about logs"""
    files = get_log_files()
    total_size = sum(f['size'] for f in files)
    
    return jsonify({
        'total_files': len(files),
        'total_size': total_size,
        'total_size_mb': round(total_size / 1024 / 1024, 2)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
