from datetime import datetime, timezone
from app.extensions import db

lsa_skills = db.Table(
    "lsa_skills",
    db.Column(
        "lsa_profile_id", db.Integer, db.ForeignKey("lsa_profiles.id"), primary_key=True
    ),
    db.Column("skill_id", db.Integer, db.ForeignKey("skills.id"), primary_key=True),
)


class LSAProfile(db.Model):
    __tablename__ = "lsa_profiles"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    hourly_rate = db.Column(db.Numeric(8, 2), nullable=False)
    years_experience = db.Column(db.Integer, nullable=False, default=0)
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    skills = db.relationship(
        "Skill", secondary=lsa_skills, back_populates="lsa_profiles"
    )
    bookings = db.relationship("Booking", back_populates="lsa", lazy="dynamic")
