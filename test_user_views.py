"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, connect_db, User, Message, Follows, Likes

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

class UserViewsTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        db.drop_all()
        db.create_all()
        self.client = app.test_client()
        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 32147
        self.testuser.id = self.testuser_id
        self.u1 = User.signup("u1test", "u1test@email.com", "password", None)
        self.u1_id = 43453
        self.u1.id = self.u1_id
        self.u2 = User.signup("u2test", "u2test@email.com", "password", None)
        self.u2_id = 34755
        self.u2.id = self.u2_id
        self.u3 = User.signup("u3test", "u3test@email.com", "password", None)
        self.u4 = User.signup("u4test", "u4test@email.com", "password", None)
        db.session.commit()

    def tearDown(self):
        td = super().tearDown()
        db.session.rollback()
        return td

    def setUp2(self):
        message1 = Message(text="I am a message", user_id=self.testuser_id)
        message2 = Message(text="I am a second message", user_id=self.testuser_id)
        message3 = Message(id=12433, text ="like me", user_id=self.u1_id)
        db.session.add_all([message1, message2, message3])
        db.session.commit()
        likesTest = Likes(user_id=self.testuser_id, message_id = 12433)
        db.session.add(likesTest)
        db.session.commit()

    def test_like(self):
        message = Message(id=28320, text="I like this message", user_id=self.u1_id)
        db.session.add(message)
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            response = c.post("/messages/28320/like", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            likes = Likes.query.filter(Likes.message_id==28320).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.testuser_id)

    def test_unlike(self):
        self.setUp2()
        message = Message.query.filter(Message.text=="like me").one()
        self.assertIsNotNone(message)
        self.assertNotEqual(message.user_id, self.testuser_id)
        likes = Likes.query.filter(Likes.user_id==self.testuser_id and Likes.message_id==m.id).one()
        self.assertIsNotNone(likes)
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            response = c.post(f"/messages/{message.id}/like", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            likes = Likes.query.filter(Likes.message_id==message.id).all()
            self.assertEqual(len(likes), 0)