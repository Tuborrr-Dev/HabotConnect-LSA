"""**Name:** Israel Adetubo
**Contact:** israetubo@gmail.com"""

from datetime import datetime, timezone
from app.extensions import db


# this is the parent model, which represents a parent user in the system
class Parent(db.Model):
    __tablename__ = "parents"
    # the primary key is the id column which is the same in allot of other models
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone_number = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    bookings = db.relationship("Booking", back_populates="parent", lazy="dynamic")
