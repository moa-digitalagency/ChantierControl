import unittest
import os
import sys
import time
from flask import session

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, User, Entreprise
from security import hash_pin

class TestSecurity(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing if it was enabled (it's not but good practice)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create Entreprise
        self.entreprise = Entreprise(
            nom="Security Corp",
            telephone="0500000000"
        )
        db.session.add(self.entreprise)
        db.session.commit()

        # Create Test User
        self.user = User(
            telephone="0611111111",
            pin_hash=hash_pin("1234"),
            nom="Security",
            prenom="Tester",
            role="admin",
            entreprise_id=self.entreprise.id,
            actif=True
        )
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

        # Reset rate limiter storage if it exists (for isolation)
        from routes import auth
        if hasattr(auth, 'login_attempts'):
            auth.login_attempts.clear()

    def test_login_rate_limiting(self):
        """Test that login is rate limited after 5 failed attempts"""

        # 1. 5 Failed attempts
        for i in range(5):
            response = self.client.post('/login', data={
                'telephone': '0611111111',
                'pin': '0000' # Wrong PIN
            }, follow_redirects=True, environ_base={'REMOTE_ADDR': '192.168.1.100'})

            # Should show incorrect credentials message
            self.assertIn(b'Num\xc3\xa9ro de t\xc3\xa9l\xc3\xa9phone ou PIN incorrect', response.data)

        # 2. 6th attempt - Should be blocked
        response = self.client.post('/login', data={
            'telephone': '0611111111',
            'pin': '0000'
        }, follow_redirects=True, environ_base={'REMOTE_ADDR': '192.168.1.100'})

        # Check for rate limit message (which we will add)
        # Using a partial match for the message we intend to add
        self.assertIn(b'Trop de tentatives', response.data)

    def test_login_success_resets_limit(self):
        """Test that a successful login resets the failed attempt counter"""

        # 1. 3 Failed attempts
        for i in range(3):
            self.client.post('/login', data={
                'telephone': '0611111111',
                'pin': '0000'
            }, follow_redirects=True, environ_base={'REMOTE_ADDR': '192.168.1.101'})

        # 2. Successful login
        response = self.client.post('/login', data={
            'telephone': '0611111111',
            'pin': '1234' # Correct PIN
        }, follow_redirects=True, environ_base={'REMOTE_ADDR': '192.168.1.101'})

        self.assertIn(b'Bienvenue Tester!', response.data)
        self.client.get('/logout', follow_redirects=True)

        # 3. Fail again - count should start from 0 (or at least not be 4)
        # We can try 5 more times and they should all be "allowed" (as in, not blocked by rate limit yet)
        for i in range(4):
            response = self.client.post('/login', data={
                'telephone': '0611111111',
                'pin': '0000'
            }, follow_redirects=True, environ_base={'REMOTE_ADDR': '192.168.1.101'})
            self.assertIn(b'Num\xc3\xa9ro de t\xc3\xa9l\xc3\xa9phone ou PIN incorrect', response.data)
            self.assertNotIn(b'Trop de tentatives', response.data)

if __name__ == '__main__':
    unittest.main()
