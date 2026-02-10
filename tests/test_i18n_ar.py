import unittest
from flask import session, g
from app import create_app

class ArabicI18nTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_switch_to_arabic_rtl(self):
        """Test switching to Arabic sets direction to RTL by default"""
        with self.client:
            response = self.client.get('/set_language/ar', follow_redirects=True)
            self.assertEqual(session.get('lang'), 'ar')
            # Check default direction logic in session
            # Note: app.py logic sets g.dir based on session or default
            # We need to check if the response contains dir="rtl"
            self.assertIn(b'dir="rtl"', response.data)
            self.assertIn(b'lang="ar"', response.data)

    def test_switch_to_arabic_ltr_toggle(self):
        """Test toggling direction to LTR while in Arabic"""
        with self.client:
            # First set to Arabic
            self.client.get('/set_language/ar', follow_redirects=True)

            # Now toggle to LTR
            response = self.client.get('/set_direction/ltr', follow_redirects=True)
            self.assertEqual(session.get('dir'), 'ltr')
            self.assertIn(b'dir="ltr"', response.data)
            self.assertIn(b'lang="ar"', response.data)

    def test_switch_back_to_rtl(self):
        """Test toggling back to RTL from LTR"""
        with self.client:
            self.client.get('/set_language/ar', follow_redirects=True)
            self.client.get('/set_direction/ltr', follow_redirects=True)

            response = self.client.get('/set_direction/rtl', follow_redirects=True)
            self.assertEqual(session.get('dir'), 'rtl')
            self.assertIn(b'dir="rtl"', response.data)

    def test_non_arabic_languages_are_ltr(self):
        """Test other languages remain LTR"""
        with self.client:
            response = self.client.get('/set_language/en', follow_redirects=True)
            self.assertEqual(session.get('lang'), 'en')
            # Should be LTR by default
            self.assertIn(b'dir="ltr"', response.data)
            self.assertIn(b'lang="en"', response.data)

if __name__ == '__main__':
    unittest.main()
