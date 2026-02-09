import unittest
from app import create_app
from flask import session, url_for

class I18nTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_default_language(self):
        # Default should be 'fr'
        with self.client:
            # Check direct access to login
            response = self.client.get('/login')
            # Check for French text
            self.assertIn(b'Gestion Chantiers', response.data)
            self.assertIn(b'Connectez-vous', response.data)

    def test_switch_language(self):
        # Switch to English
        with self.client:
            self.client.get('/set_language/en', follow_redirects=True)
            with self.client.session_transaction() as sess:
                self.assertEqual(sess['lang'], 'en')

            response = self.client.get('/login')
            # Check for English text
            self.assertIn(b'Construction Management', response.data)
            self.assertIn(b'Log in', response.data)

    def test_switch_back(self):
        # Switch to En then Fr
        with self.client:
            self.client.get('/set_language/en', follow_redirects=True)
            self.client.get('/set_language/fr', follow_redirects=True)
            response = self.client.get('/login')
            self.assertIn(b'Gestion Chantiers', response.data)

if __name__ == '__main__':
    unittest.main()
