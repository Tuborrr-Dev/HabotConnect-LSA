"""**Name:** Israel Adetubo
**Contact:** israetubo@gmail.com"""

from app.extensions import db


# this is a many-to-many relationship table between LSAProfile and Skill
class LSASkill(db.Model):
    __tablename__ = "lsa_skills"
    # the primary key is a composite key of lsa_id and skill_id
    lsa_id = db.Column(
        db.Integer,
        db.ForeignKey("lsa_profiles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    skill_id = db.Column(
        db.Integer, db.ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True
    )
