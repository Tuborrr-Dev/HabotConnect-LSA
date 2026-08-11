from app.extensions import db


class LSASkill(db.Model):
    __tablename__ = "lsa_skills"

    lsa_id = db.Column(
        db.Integer,
        db.ForeignKey("lsa_profiles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    skill_id = db.Column(
        db.Integer, db.ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True
    )
