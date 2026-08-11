from datetime import datetime, timezone
from app.extensions import db


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(
        db.Integer, db.ForeignKey("parents.id"), nullable=False, index=True
    )
    lsa_id = db.Column(
        db.Integer, db.ForeignKey("lsa_profiles.id"), nullable=False, index=True
    )
    child_name = db.Column(db.String(120), nullable=False)
    session_date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(
        db.String(20), nullable=False, default="pending_payment", index=True
    )
    notes = db.Column(db.String(500), nullable=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    parent = db.relationship("Parent", back_populates="bookings")
    lsa = db.relationship("LSAProfile", back_populates="bookings")
    payment = db.relationship("Payment", back_populates="booking", uselist=False)

    __table_args__ = (
        db.CheckConstraint("end_time > start_time", name="check_end_after_start"),
        db.Index("ix_bookings_lsa_date", "lsa_id", "session_date"),
    )
