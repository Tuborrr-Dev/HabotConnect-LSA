from datetime import datetime, timezone
from app.extensions import db


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(
        db.Integer, db.ForeignKey("bookings.id"), nullable=False, index=True
    )
    amount = db.Column(db.Numeric(8, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    provider_reference = db.Column(
        db.String(100), unique=True, nullable=False, index=True
    )
    processed_event_id = db.Column(
        db.String(100), unique=True, nullable=True, index=True
    )
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    booking = db.relationship("Booking", back_populates="payment")
