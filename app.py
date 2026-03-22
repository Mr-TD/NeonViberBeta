from flask import Flask, render_template, request, jsonify, session
import sqlite3
import json
import os

app = Flask(__name__)
app.secret_key = 'snake_secret_key_2026'
DB_FILE = 'game.db'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (username TEXT PRIMARY KEY, high_score INTEGER, gems INTEGER, unlocked_skins TEXT, active_skin TEXT)''')
        conn.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/users', methods=['GET'])
def get_users():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT username, high_score FROM users ORDER BY high_score DESC')
        users = [{'username': row[0], 'high_score': row[1]} for row in c.fetchall()]
    return jsonify({'users': users})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    if not username:
        return jsonify({'error': 'Username required'}), 400
    
    session['username'] = username
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username=?', (username,))
        row = c.fetchone()
        if not row:
            c.execute('INSERT INTO users (username, high_score, gems, unlocked_skins, active_skin) VALUES (?, ?, ?, ?, ?)',
                      (username, 0, 0, json.dumps(['classic']), 'classic'))
            conn.commit()
    return jsonify({'success': True, 'username': username})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'success': True})

@app.route('/api/profile', methods=['GET'])
def profile():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    username = session['username']
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

@app.route('/api/save', methods=['POST'])
def save():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    data = request.json
    username = session['username']
    high_score = data.get('high_score', 0)
    gems = data.get('gems', 0)
    
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('UPDATE users SET gems = ? WHERE username=?', (gems, username))
        c.execute('UPDATE users SET high_score = ? WHERE username=? AND ? > high_score', (high_score, username, high_score))
        conn.commit()
    return jsonify({'success': True})

@app.route('/api/buy', methods=['POST'])
def buy():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    data = request.json
    username = session['username']
    skin_id = data.get('skin_id')
    cost = data.get('cost', 0)
    
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
            return jsonify({'error': 'Not enough gems'}), 400

@app.route('/api/equip', methods=['POST'])
def equip():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    data = request.json
    username = session['username']
    skin_id = data.get('skin_id')
    
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('UPDATE users SET active_skin=? WHERE username=?', (skin_id, username))
        conn.commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
