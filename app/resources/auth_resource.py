"""**Name:** Israel Adetubo
**Contact:** israetubo@gmail.com"""

from flask import request
from flask_restful import Resource
from marshmallow import Schema, fields, validate, ValidationError
from app.services.auth_service import (
    AuthService,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
)


class ParentSignupSchema(Schema):
    full_name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))
    phone_number = fields.String(load_default=None)


class LSASignupSchema(Schema):
    full_name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))
    hourly_rate = fields.Decimal(required=True, as_string=True)
    years_experience = fields.Integer(load_default=0, validate=validate.Range(min=0))


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class ParentSignupResource(Resource):
    def post(self):
        try:
            data = ParentSignupSchema().load(request.get_json() or {})
        except ValidationError as err:
            return {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid signup data",
                    "details": err.messages,
                }
            }, 400

        try:
            parent = AuthService.signup_parent(**data)
        except EmailAlreadyExistsError as exc:
            return {
                "error": {"code": "EMAIL_EXISTS", "message": str(exc), "details": {}}
            }, 409

        return {"id": parent.id, "email": parent.email}, 201


class ParentLoginResource(Resource):
    def post(self):
        try:
            data = LoginSchema().load(request.get_json() or {})
        except ValidationError as err:
            return {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid login data",
                    "details": err.messages,
                }
            }, 400

        try:
            parent, token = AuthService.login_parent(**data)
        except InvalidCredentialsError as exc:
            return {
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": str(exc),
                    "details": {},
                }
            }, 401

        return {"access_token": token, "id": parent.id}, 200


class LSASignupResource(Resource):
    def post(self):
        try:
            data = LSASignupSchema().load(request.get_json() or {})
        except ValidationError as err:
            return {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid signup data",
                    "details": err.messages,
                }
            }, 400

        try:
            lsa = AuthService.signup_lsa(**data)
        except EmailAlreadyExistsError as exc:
            return {
                "error": {"code": "EMAIL_EXISTS", "message": str(exc), "details": {}}
            }, 409

        return {"id": lsa.id, "email": lsa.email}, 201


class LSALoginResource(Resource):
    def post(self):
        try:
            data = LoginSchema().load(request.get_json() or {})
        except ValidationError as err:
            return {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid login data",
                    "details": err.messages,
                }
            }, 400

        try:
            lsa, token = AuthService.login_lsa(**data)
        except InvalidCredentialsError as exc:
            return {
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": str(exc),
                    "details": {},
                }
            }, 401

        return {"access_token": token, "id": lsa.id}, 200
