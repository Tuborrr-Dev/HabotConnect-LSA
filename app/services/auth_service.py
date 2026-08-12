"""**Name:** Israel Adetubo
**Contact:** israetubo@gmail.com"""

from flask_jwt_extended import create_access_token
from app.extensions import db
from app.models.parent import Parent
from app.models.lsa_profile import LSAProfile
from app.utils.security import hash_password, check_password


# this is the AuthService class, which provides methods for signing up and logging in parents and LSAs (Learning Support Assistants). It handles password hashing, token generation, and raises custom exceptions for various error scenarios such as email already exists or invalid credentials.
class AuthServiceError(Exception):
    pass


class EmailAlreadyExistsError(AuthServiceError):
    pass


class InvalidCredentialsError(AuthServiceError):
    pass


class AuthService:

    @staticmethod
    def signup_parent(full_name, email, password, phone_number=None):
        if Parent.query.filter_by(email=email).first():
            raise EmailAlreadyExistsError(f"Email {email} is already registered")

        parent = Parent(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            password_hash=hash_password(password),
        )
        db.session.add(parent)
        db.session.commit()
        return parent

    @staticmethod
    def login_parent(email, password):
        parent = Parent.query.filter_by(email=email).first()
        if not parent or not check_password(password, parent.password_hash):
            raise InvalidCredentialsError("Invalid email or password")

        token = create_access_token(
            identity=str(parent.id), additional_claims={"type": "parent"}
        )
        return parent, token

    @staticmethod
    def signup_lsa(full_name, email, password, hourly_rate, years_experience=0):
        if LSAProfile.query.filter_by(email=email).first():
            raise EmailAlreadyExistsError(f"Email {email} is already registered")

        lsa = LSAProfile(
            full_name=full_name,
            email=email,
            hourly_rate=hourly_rate,
            years_experience=years_experience,
            password_hash=hash_password(password),
        )
        db.session.add(lsa)
        db.session.commit()
        return lsa

    @staticmethod
    def login_lsa(email, password):
        lsa = LSAProfile.query.filter_by(email=email).first()
        if not lsa or not check_password(password, lsa.password_hash):
            raise InvalidCredentialsError("Invalid email or password")

        token = create_access_token(
            identity=str(lsa.id), additional_claims={"type": "lsa"}
        )
        return lsa, token
