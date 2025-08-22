from flask import Flask, request, jsonify, redirect, send_file
from flask_cors import CORS
import sqlite3
import uuid
import os
from urllib.parse import urlparse
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration
PORT = 3000

# Initialize database
def initialize_database():
    conn = sqlite3.connect('urls.db')
    cursor = conn.cursor()
    
    # Create URLs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE NOT NULL,
            original_url TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            clicks INTEGER DEFAULT 0,
            last_accessed DATETIME
        )
    ''')
    
    # Create analytics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url_id INTEGER,
            ip_address TEXT,
            user_agent TEXT,
            referrer TEXT,
            accessed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (url_id) REFERENCES urls (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")

# Generate a short code
def generate_short_code():
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(chars[i % len(chars)] for i in os.urandom(6))

# Validate URL format
def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('urls.db')
    conn.row_factory = sqlite3.Row
    return conn

# API Routes

@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    original_url = data.get('originalUrl')
    
    if not original_url:
        return jsonify({'error': 'URL is required'}), 400
    
    if not is_valid_url(original_url):
        return jsonify({'error': 'Invalid URL format'}), 400
    
    short_code = None
    attempts = 0
    max_attempts = 5
    
    # Generate unique short code
    conn = get_db_connection()
    while attempts < max_attempts:
        short_code = generate_short_code()
        
        # Check if code exists
        existing = conn.execute(
            'SELECT short_code FROM urls WHERE short_code = ?', 
            (short_code,)
        ).fetchone()
        
        if not existing:
            break
        attempts += 1
    
    if attempts == max_attempts:
        conn.close()
        return jsonify({'error': 'Failed to generate unique short code'}), 500
    
    # Insert new URL
    try:
        cursor = conn.execute(
            'INSERT INTO urls (short_code, original_url) VALUES (?, ?)',
            (short_code, original_url)
        )
        url_id = cursor.lastrowid
        
        short_url = f"{request.scheme}://{request.host}/{short_code}"
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'originalUrl': original_url,
            'shortCode': short_code,
            'shortUrl': short_url,
            'createdAt': datetime.now().isoformat()
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'error': 'Database error'}), 500

@app.route('/<short_code>')
def redirect_to_url(short_code):
    conn = get_db_connection()
    
    try:
        url = conn.execute(
            'SELECT * FROM urls WHERE short_code = ?', 
            (short_code,)
        ).fetchone()
        
        if not url:
            conn.close()
            return 'URL not found', 404
        
        # Update click count and last accessed
        conn.execute(
            'UPDATE urls SET clicks = clicks + 1, last_accessed = CURRENT_TIMESTAMP WHERE id = ?',
            (url['id'],)
        )
        
        # Log analytics
        conn.execute(
            'INSERT INTO analytics (url_id, ip_address, user_agent, referrer) VALUES (?, ?, ?, ?)',
            (url['id'], request.remote_addr, request.user_agent.string, request.referrer)
        )
        
        conn.commit()
        conn.close()
        
        return redirect(url['original_url'])
        
    except Exception as e:
        conn.close()
        return jsonify({'error': 'Database error'}), 500

@app.route('/api/stats')
def get_stats():
    conn = get_db_connection()
    
    try:
        base_url = f"{request.scheme}://{request.host}"
        stats = conn.execute('''
            SELECT 
                COUNT(*) as totalLinks,
                SUM(clicks) as totalClicks,
                SUM(LENGTH(original_url) - LENGTH(short_code) - LENGTH(?) - 1) as savedChars
            FROM urls
        ''', (base_url,)).fetchone()
        
        conn.close()
        
        return jsonify({
            'totalLinks': stats['totalLinks'] or 0,
            'totalClicks': stats['totalClicks'] or 0,
            'savedChars': max(stats['savedChars'] or 0, 0)
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'error': 'Database error'}), 500

@app.route('/api/recent')
def get_recent_urls():
    conn = get_db_connection()
    
    try:
        urls = conn.execute('''
            SELECT 
                short_code, 
                original_url, 
                created_at as createdAt, 
                clicks 
            FROM urls 
            ORDER BY created_at DESC 
            LIMIT 5
        ''').fetchall()
        
        conn.close()
        
        result = []
        base_url = f"{request.scheme}://{request.host}"
        for url in urls:
            result.append({
                'short_code': url['short_code'],
                'original_url': url['original_url'],
                'shortUrl': f"{base_url}/{url['short_code']}",
                'createdAt': url['createdAt'],
                'clicks': url['clicks']
            })
        
        return jsonify(result)
        
    except Exception as e:
        conn.close()
        return jsonify({'error': 'Database error'}), 500

@app.route('/api/url/<short_code>')
def get_url_details(short_code):
    conn = get_db_connection()
    
    try:
        url = conn.execute('''
            SELECT 
                short_code, 
                original_url, 
                created_at as createdAt, 
                clicks,
                last_accessed as lastAccessed
            FROM urls 
            WHERE short_code = ?
        ''', (short_code,)).fetchone()
        
        conn.close()
        
        if not url:
            return jsonify({'error': 'URL not found'}), 404
        
        base_url = f"{request.scheme}://{request.host}"
        return jsonify({
            'short_code': url['short_code'],
            'original_url': url['original_url'],
            'shortUrl': f"{base_url}/{url['short_code']}",
            'createdAt': url['createdAt'],
            'clicks': url['clicks'],
            'lastAccessed': url['lastAccessed']
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'error': 'Database error'}), 500

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'OK', 'timestamp': datetime.now().isoformat()})

@app.route('/')
def serve_frontend():
    return send_file('index.html')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Something went wrong!'}), 500

if __name__ == '__main__':
    # Initialize database
    initialize_database()
    print(f"Server running on http://localhost:{PORT}")
    app.run(debug=True, port=PORT)
