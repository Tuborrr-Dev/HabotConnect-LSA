"""**Name:** Israel Adetubo
**Contact:** israetubo@gmail.com"""

import unittest
from datetime import datetime, date, time
from flask_jwt_extended import create_access_token
from app import create_app
from app.extensions import db
from app.models.parent import Parent
from app.models.lsa_profile import LSAProfile
from app.models.skill import Skill
from app.models.booking import Booking
from app.models.payment import Payment


# this is a base test case class that sets up the Flask application context and database for testing. It provides utility methods to create test data such as parents, LSAs, skills, bookings, and payments. The `setUp` method initializes the app and database, while the `tearDown` method cleans up after each test. The `auth_header` method generates an authorization header for authenticated requests.
class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def auth_header(self, user_id, user_type):
        token = create_access_token(
            identity=str(user_id), additional_claims={"type": user_type}
        )
        return {"Authorization": f"Bearer {token}"}

    def create_parent(self, **kwargs):
        defaults = {
            "full_name": "Test Parent",
            "email": "parent@test.com",
            "password_hash": "hash",
        }
        defaults.update(kwargs)
        p = Parent(**defaults)
        db.session.add(p)
        db.session.commit()
        return p

    def create_lsa(self, **kwargs):
        defaults = {
            "full_name": "Test LSA",
            "email": "lsa@test.com",
            "password_hash": "hash",
            "hourly_rate": 25.00,
            "years_experience": 3,
            "is_available": True,
        }
        defaults.update(kwargs)
        l = LSAProfile(**defaults)
        db.session.add(l)
        db.session.commit()
        return l

    def create_skill(self, name="Test Skill"):
        s = Skill(name=name)
        db.session.add(s)
        db.session.commit()
        return s

    def create_booking(self, **kwargs):
        defaults = {
            "child_name": "Test Child",
            "session_date": date(2026, 8, 20),
            "start_time": time(14, 0),
            "end_time": time(15, 0),
            "status": "pending_payment",
        }
        defaults.update(kwargs)
        if isinstance(defaults["session_date"], str):
            defaults["session_date"] = datetime.strptime(
                defaults["session_date"], "%Y-%m-%d"
            ).date()
        if isinstance(defaults["start_time"], str):
            defaults["start_time"] = datetime.strptime(
                defaults["start_time"], "%H:%M"
            ).time()
        if isinstance(defaults["end_time"], str):
            defaults["end_time"] = datetime.strptime(
                defaults["end_time"], "%H:%M"
            ).time()
        b = Booking(**defaults)
        db.session.add(b)
        db.session.commit()
        return b

    def create_payment(self, **kwargs):
        defaults = {
            "amount": 25.00,
            "status": "pending",
            "provider_reference": "pay_ref_test",
        }
        defaults.update(kwargs)
        p = Payment(**defaults)
        db.session.add(p)
        db.session.commit()
        return p
