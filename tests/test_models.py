"""**Name:** Israel Adetubo
**Contact:** israetubo@gmail.com"""

from datetime import date, time
from tests.base import BaseTestCase
from app.models.booking import Booking
from app.extensions import db
from sqlalchemy.exc import IntegrityError


class TestModels(BaseTestCase):
    def test_tc19_check_constraint_end_before_start(self):
        parent = self.create_parent()
        lsa = self.create_lsa()
        booking = Booking(
            parent_id=parent.id,
            lsa_id=lsa.id,
            child_name="Test",
            session_date=date(2026, 8, 20),
            start_time=time(15, 0),
            end_time=time(14, 0),
            status="pending_payment",
        )
        db.session.add(booking)
        with self.assertRaises(IntegrityError):
            db.session.commit()
