"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()
        user1 = User.signup("test", "test@email.com", "password", None)
        user1ID = 10000
        user1.id = user1ID
        user2 = User.signup("testagain", "testagain@email.com", "password2", None)
        user2ID = 20000
        user2.id = user2ID
        db.session.commit()
        user1 = User.query.get(user1ID)
        user2 = User.query.get(user2ID)
        self.user1 = user1
        self.user1ID = user1ID
        self.user2 = user2
        self.user2ID = user2ID
        self.client = app.test_client()

    def tearDown(self):
        td = super().tearDown()
        db.session.rollback()
        return td

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_signup(self):
        newUser = User.signup("YetAnotherTest", "testthings@someemail.com", "password", None)
        userID = 52342
        newUser.id = userID
        db.session.commit()
        newUser = User.query.get(userID)
        self.assertIsNotNone(newUser)
        self.assertEqual(newUser.username, "YetAnotherTest")
        self.assertEqual(newUser.email, "testthings@someemail.com")
        self.assertNotEqual(newUser.password, "password")
    
    def test_wrong_username(self):
        self.assertFalse(User.authenticate("wrongusername", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.user1.username, "wrongpassword"))
    
    def test_authentication(self):
        user = User.authenticate(self.user1.username, "password")
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.user1ID)

    def test_follows(self):
        self.user1.following.append(self.user2)
        db.session.commit()
        self.assertEqual(len(self.user1.followers), 0)
        self.assertEqual(len(self.user1.following), 1)
        self.assertEqual(len(self.user2.following), 0)
        self.assertEqual(len(self.user2.followers), 1)
        self.assertEqual(self.user1.following[0].id, self.user2.id)
        self.assertEqual(self.user2.followers[0].id, self.user1.id)

    def test_following(self):
        self.user1.following.append(self.user2)
        db.session.commit()
        self.assertTrue(self.user1.is_following(self.user2))
        self.assertFalse(self.user2.is_following(self.user1))

    def test_is_followed_by(self):
        self.user1.following.append(self.user2)
        db.session.commit()
        self.assertTrue(self.user2.is_followed_by(self.user1))
        self.assertFalse(self.user1.is_followed_by(self.user2))