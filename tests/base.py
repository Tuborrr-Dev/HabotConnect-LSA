# Name: Israel Adetubo
# contact: israeltubo@gmail.com
import unittest
from datetime import datetime
from app import create_app
from app.extensions import db
from app.models.parent import Parent
from app.models.lsa_profile import LSAProfile
from app.models.skill import Skill
from app.models.booking import Booking
from app.models.payment import Payment


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
            "session_date": datetime.strptime("2026-08-20", "%Y-%m-%d").date(),
            "start_time": datetime.strptime("14:00", "%H:%M").time(),
            "end_time": datetime.strptime("15:00", "%H:%M").time(),
            "status": "pending_payment",
        }
        defaults.update(kwargs)
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
