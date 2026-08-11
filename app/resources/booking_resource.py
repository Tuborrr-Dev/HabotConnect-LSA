import logging
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError
from app.schemas.booking_schema import BookingCreateSchema, BookingResponseSchema
from app.services.booking_service import (
    BookingService,
    SlotUnavailableError,
    LSANotAvailableError,
    ResourceNotFoundError,
)
from app.extensions import db

logger = logging.getLogger(__name__)


class BookingResource(Resource):

    @jwt_required()
    def post(self):
        schema = BookingCreateSchema()
        try:
            data = schema.load(request.get_json() or {})
        except ValidationError as err:
            return {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request data",
                    "details": err.messages,
                }
            }, 400

        # Only a logged-in Parent can create a booking (not an LSA)
        claims = get_jwt()
        if claims.get("type") != "parent":
            return {
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Only parents can create bookings",
                    "details": {},
                }
            }, 403

        # Ignore any parent_id the client sent — always use the logged-in user's own id
        data["parent_id"] = int(get_jwt_identity())

        try:
            booking = BookingService.create_booking(data)
        except ResourceNotFoundError as exc:
            return {
                "error": {"code": "NOT_FOUND", "message": str(exc), "details": {}}
            }, 404
        except LSANotAvailableError as exc:
            return {
                "error": {
                    "code": "UNPROCESSABLE_ENTITY",
                    "message": str(exc),
                    "details": {},
                }
            }, 422
        except SlotUnavailableError as exc:
            details = {}
            if exc.conflicting_booking_id:
                details["conflicting_booking_id"] = exc.conflicting_booking_id
            return {
                "error": {
                    "code": "SLOT_UNAVAILABLE",
                    "message": str(exc),
                    "details": details,
                }
            }, 409
        except Exception:
            db.session.rollback()
            logger.exception("Unexpected error creating booking")
            return {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {},
                }
            }, 500

        return BookingResponseSchema().dump(booking), 201

    @jwt_required()
    def get(self):
        claims = get_jwt()
        user_id = int(get_jwt_identity())

        if claims.get("type") == "parent":
            bookings = BookingService.list_bookings_for_parent(user_id)
        elif claims.get("type") == "lsa":
            bookings = BookingService.list_bookings_for_lsa(user_id)
        else:
            return {
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Unrecognized user type",
                    "details": {},
                }
            }, 403

        return BookingResponseSchema(many=True).dump(bookings), 200


class BookingDetailResource(Resource):

    @jwt_required()
    def get(self, booking_id):
        try:
            booking = BookingService.get_booking(booking_id)
        except ResourceNotFoundError as exc:
            return {
                "error": {"code": "NOT_FOUND", "message": str(exc), "details": {}}
            }, 404

        # Only the parent or LSA on this specific booking can view it
        claims = get_jwt()
        user_id = int(get_jwt_identity())
        is_owner = (
            claims.get("type") == "parent" and booking.parent_id == user_id
        ) or (claims.get("type") == "lsa" and booking.lsa_id == user_id)
        if not is_owner:
            return {
                "error": {
                    "code": "FORBIDDEN",
                    "message": "You do not have access to this booking",
                    "details": {},
                }
            }, 403

        return BookingResponseSchema().dump(booking), 200
