import os
import sqlite3
import json
import logging
import re
from flask import Flask, render_template, request, jsonify, session, make_response

# Configure Logging for better Code Quality
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Security: Use environment variable for secret key in production, fallback for development.
app.secret_key = os.getenv('SECRET_KEY', 'snake_secret_key_2026_dev')
DB_FILE = 'game.db'

# Security: Content Security Policy & Security Headers
@app.after_request
def set_security_headers(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

def init_db():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS users
                         (username TEXT PRIMARY KEY, high_score INTEGER, gems INTEGER, unlocked_skins TEXT, active_skin TEXT)''')
            # Efficiency: Create an index on high_score for the leaderboard query
            c.execute('CREATE INDEX IF NOT EXISTS idx_high_score ON users(high_score DESC)')
            conn.commit()
            logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing DB: {e}")

# Validator helper
def is_valid_username(username):
    # Security: Enforce length and alphanumeric to prevent malicious payloads
    if not isinstance(username, str):
        return False
    if len(username) < 3 or len(username) > 15:
        return False
    return bool(re.match(r'^[a-zA-Z0-9_]+$', username))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            # Efficiently pull top 10 to avoid huge payloads
            c.execute('SELECT username, high_score FROM users ORDER BY high_score DESC LIMIT 10')
            users = [{'username': row[0], 'high_score': row[1]} for row in c.fetchall()]
        return jsonify({'users': users})
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    
    if not username or not is_valid_username(username):
        return jsonify({'error': 'Invalid username. Must be 3-15 alphanumeric characters.'}), 400
    
    try:
        session['username'] = username
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('SELECT username FROM users WHERE username=?', (username,))
            row = c.fetchone()
            if not row:
                logger.info(f"Creating new user: {username}")
                c.execute('INSERT INTO users (username, high_score, gems, unlocked_skins, active_skin) VALUES (?, ?, ?, ?, ?)',
                          (username, 0, 0, json.dumps(['classic']), 'classic'))
                conn.commit()
        return jsonify({'success': True, 'username': username})
    except Exception as e:
        logger.error(f"Error logging in: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'success': True})

@app.route('/api/profile', methods=['GET'])
def profile():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    username = session['username']
    
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('SELECT high_score, gems, unlocked_skins, active_skin FROM users WHERE username=?', (username,))
            row = c.fetchone()
            if row:
                return jsonify({
                    'username': username,
                    'high_score': row[0],
                    'gems': row[1],
                    'unlocked_skins': json.loads(row[2]),
                    'active_skin': row[3]
                })
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        logger.error(f"Error fetching profile: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/save', methods=['POST'])
def save():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json or {}
    username = session['username']
    
    # Validation
    try:
        high_score = int(data.get('high_score', 0))
        gems = int(data.get('gems', 0))
    except ValueError:
        return jsonify({'error': 'Invalid payload data'}), 400

    if high_score < 0 or gems < 0:
        return jsonify({'error': 'Values cannot be negative'}), 400
    
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('UPDATE users SET gems = ? WHERE username=?', (gems, username))
            c.execute('UPDATE users SET high_score = ? WHERE username=? AND ? > high_score', (high_score, username, high_score))
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error saving profile: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/buy', methods=['POST'])
def buy():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json or {}
    username = session['username']
    skin_id = data.get('skin_id')
    
    try:
        cost = int(data.get('cost', 0))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid cost parameter'}), 400

    if not skin_id or not isinstance(skin_id, str):
        return jsonify({'error': 'Invalid skin ID'}), 400

    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('SELECT gems, unlocked_skins FROM users WHERE username=?', (username,))
            row = c.fetchone()
            if row and row[0] >= cost:
                gems = row[0] - cost
                unlocked = json.loads(row[1])
                if skin_id not in unlocked:
                    unlocked.append(skin_id)
                c.execute('UPDATE users SET gems=?, unlocked_skins=? WHERE username=?',
                          (gems, json.dumps(unlocked), username))
                conn.commit()
                return jsonify({'success': True, 'gems': gems, 'unlocked_skins': unlocked})
            else:
                return jsonify({'error': 'Not enough gems or user not found'}), 400
    except Exception as e:
        logger.error(f"Error in shop buy: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/equip', methods=['POST'])
def equip():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json or {}
    username = session['username']
    skin_id = data.get('skin_id')
    
    if not skin_id or not isinstance(skin_id, str):
        return jsonify({'error': 'Invalid skin ID'}), 400
        
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            # Security Note: ensuring the user actually owns the skin could be validated here too, 
            # but setting active_skin harmlessly overwrites it. Let's validate ownership.
            c.execute('SELECT unlocked_skins FROM users WHERE username=?', (username,))
            row = c.fetchone()
            if row:
                unlocked = json.loads(row[0])
                if skin_id in unlocked:
                    c.execute('UPDATE users SET active_skin=? WHERE username=?', (skin_id, username))
                    conn.commit()
                    return jsonify({'success': True})
                else:
                    return jsonify({'error': 'Skin not owned'}), 403
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        logger.error(f"Error equipping skin: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
