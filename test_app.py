import unittest
import json
import os
import sqlite3
from app import app, init_db, DB_FILE

class NeonViperTestCase(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        app.config['TESTING'] = True
        app.secret_key = os.urandom(24)
        self.client = app.test_client()
        
        # Test DB Initialization
        init_db()
        
        # Insert a mock user
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('INSERT OR REPLACE INTO users (username, high_score, gems, unlocked_skins, active_skin) VALUES (?, ?, ?, ?, ?)',
                      ('tester1', 100, 50, '["classic"]', 'classic'))
            conn.commit()

    def tearDown(self):
        # Cleanup
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('DELETE FROM users WHERE username="tester1"')
            c.execute('DELETE FROM users WHERE username="newuser"')
            c.execute('DELETE FROM users WHERE username="<script>bad"')
            conn.commit()

    def test_get_users(self):
        rv = self.client.get('/api/users')
        self.assertEqual(rv.status_code, 200)
        data = json.loads(rv.data)
        self.assertIn('users', data)

    def test_login_valid(self):
        rv = self.client.post('/api/login', json={'username': 'newuser'})
        self.assertEqual(rv.status_code, 200)
        
    def test_login_invalid_xss(self):
        # Should be rejected due to validation
        rv = self.client.post('/api/login', json={'username': '<script>bad'})
        self.assertEqual(rv.status_code, 400)

    def test_save_score(self):
        # Must login first
        with self.client.session_transaction() as sess:
            sess['username'] = 'tester1'
            
        rv = self.client.post('/api/save', json={'high_score': 500, 'gems': 60})
        self.assertEqual(rv.status_code, 200)

        # Verify in DB
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('SELECT high_score, gems FROM users WHERE username="tester1"')
            row = c.fetchone()
            self.assertEqual(row[0], 500)
            self.assertEqual(row[1], 60)

    def test_buy_skin_success(self):
        with self.client.session_transaction() as sess:
            sess['username'] = 'tester1'
            
        rv = self.client.post('/api/buy', json={'skin_id': 'neon'})
        self.assertEqual(rv.status_code, 200)
        data = json.loads(rv.data)
        self.assertEqual(data['gems'], 0)
        self.assertIn('neon', data['unlocked_skins'])

    def test_buy_skin_fail_insufficient_gems(self):
        with self.client.session_transaction() as sess:
            sess['username'] = 'tester1'
            
        rv = self.client.post('/api/buy', json={'skin_id': 'lava'})
        self.assertEqual(rv.status_code, 400)
        
    def test_gemini_comment(self):
        # Tests the fallback behavior when API key is not present or mocked
        rv = self.client.post('/api/comment', json={'event': 'game_over', 'score': 100, 'level': 2})
        self.assertEqual(rv.status_code, 200)
        data = json.loads(rv.data)
        self.assertIn('comment', data)
        self.assertTrue(isinstance(data['comment'], str))
        self.assertTrue(len(data['comment']) > 0)

if __name__ == '__main__':
    unittest.main()
