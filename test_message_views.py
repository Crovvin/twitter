"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()
        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuserID = 10423
        self.testuser.id = self.testuserID
        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_show_message(self):

        message = Message(id=28323, text="test", user_id=self.testuser_id)
        db.session.add(message)
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            message = Message.query.get(28323)
            response = c.get(f'/messages/{message.id}')
            self.assertEqual(response.status_code, 200)
            self.assertIn(message.text, str(response.data))

    def test_show_wrong_message(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            response = c.get('/messages/2373272321')
            self.assertEqual(response.status_code, 404)

    def test_message_delete(self):

        message = Message(id=32412, text="test",user_id=self.testuser_id)
        db.session.add(message)
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            response = c.post("/messages/32412/delete", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            message = Message.query.get(32412)
            self.assertIsNone(message)

    def test_new_wrong_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 9818401230

            response = c.post("/messages/new", data={"text": "Test"}, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Unauthorized Access", str(response.data))

    def test_delete_authentication(self):

        message = Message(id=325235, text="test", user_id=self.testuser_id)
        db.session.add(message)
        db.session.commit()

        with self.client as c:
            respnse = c.post("/messages/325235/delete", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Access unauthorized", str(response.data))
            message = Message.query.get(325235)
            self.assertIsNotNone(message)
