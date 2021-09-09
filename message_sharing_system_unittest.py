import os
import sqlite3
import tempfile
import unittest

import message_sharing_system
import settings


class MessagesBaseTestCase(unittest.TestCase):

    def setUp(self):
        """Create a temporary database and create the needed table"""
        message_sharing_system.app.config.from_object(settings)
        self.db_fd, message_sharing_system.app.config['DATABASE'] = tempfile.mkstemp()
        message_sharing_system.app.config['TESTING'] = True
        self.app = message_sharing_system.app.test_client()
        with sqlite3.connect(message_sharing_system.app.config['DATABASE'], uri=True) as conn:
            c = conn.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS messages (id TEXT NOT NULL, dt TEXT NOT NULL, message TEXT NOT NULL, sender TEXT NOT NULL)')
            conn.commit()

    def close(self):
        os.close(self.db_fd)
        os.unlink(message_sharing_system.app.config['DATABASE'])

    # Helper functs to test login in MessagesMiscTestCase
    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

class MessagesEmptyTestCase(MessagesBaseTestCase):

    def test_get_empty_db(self):
        """GET on empty database should (return 404 Not found)"""
        rv = self.app.get('/message/hdsn68sbs')
        self.assertEqual(rv.status_code, 404)
        self.assertIn(b'"error": "Not found"', rv.data)

class MessagesSingleTestCase(MessagesBaseTestCase):

    def test_retrieve_message(self):
        """Tests to get a single message"""
        with sqlite3.connect(message_sharing_system.app.config['DATABASE']) as conn:
            c = conn.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS messages (id TEXT NOT NULL, dt TEXT NOT NULL, message TEXT NOT NULL, sender TEXT NOT NULL)')
            cmd = "INSERT INTO messages VALUES ('hdsn68sbs', datetime('now'), 'Test', 'Test')"
            c.execute(cmd)
            conn.commit()
            rv = self.app.get('/message/hdsn68sbs')
            self.assertEqual(rv.status_code, 200)
            resp = rv.get_json()
            self.assertEqual('hdsn68sbs', resp['messages'][0]['id'])
            self.assertEqual('Test', resp['messages'][0]['sender'])
            self.assertEqual('Test', resp['messages'][0]['message'])


class MessagesTestCases(MessagesBaseTestCase):

    def test_login(self):
        """Tests login functionality"""

        # Test successful login
        rv = self.login('admin', 'psw')
        self.assertIn(b'Logout', rv.data)
        self.assertEqual(rv.status_code, 200)

        # Test successful logout
        rv = self.logout()
        self.assertIn(b'Login', rv.data)
        self.assertEqual(rv.status_code, 200)

        # Test wrong username
        rv = self.login('ad', 'psw')
        self.assertIn(b'Invalid username and/or password', rv.data)
        self.assertEqual(rv.status_code, 401)

        # Test wrong password
        rv = self.login('admin', '123')
        self.assertIn(b'Invalid username and/or password', rv.data)
        self.assertEqual(rv.status_code, 401)

    def test_about_page(self):
        """Tests that about page show the intended details"""
        rv = self.app.get('/about')
        self.assertIn(b'Welcome to the Storytel Security Engineer Coding Challenge!', rv.data)
        self.assertEqual(rv.status_code, 200)

    def test_admin_page(self):
        """Tests that the admin page works as intended"""
        rv = self.app.get('/admin', follow_redirects=True)

        self.assertIn(b'Please login:', rv.data)
        self.assertEqual(rv.status_code, 200)

        with self.app as c:
            with c.session_transaction() as session:
                session['logged_in'] = True
            rv = c.get('/admin', follow_redirects=True)
        self.assertIn(b'No messages found.', rv.data)
        self.assertEqual(rv.status_code, 200)

if __name__ == '__main__':
    unittest.main()