from app.extensions import db


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)

    lsa_profiles = db.relationship(
        "LSAProfile", secondary="lsa_skills", back_populates="skills"
    )
