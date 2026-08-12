"""**Name:** Israel Adetubo
**Contact:** israetubo@gmail.com"""

from app.extensions import db


class Skill(db.Model):
    __tablename__ = "skills"
    # the primary key is the id column which is the same in allot of other models
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)

    lsa_profiles = db.relationship(
        "LSAProfile", secondary="lsa_skills", back_populates="skills"
    )
