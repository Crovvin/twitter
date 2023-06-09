"""Message model tests"""

import os
from unittest import TestCase
from models import db, User, Message, Follows, Likes

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

class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()
        userTest = User.signup("twittertesting", "twitterclone@test.com", "password", None)
        self.uid = 37284
        userTest.id = self.uid
        db.session.commit()
        self.userTest = User.query.get(self.uid)
        self.client = app.test_client()

    def tearDown(self):
        td = super().tearDown()
        db.session.rollback()
        return td

    def test_message_model(self):
        """Test if model works"""
        
        message = Message(text="message", user_id=self.uid)
        db.session.add(message)
        db.session.commit()
        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(self.u.messages[0].text, "message")
