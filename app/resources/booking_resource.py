import logging
from flask import request
from flask_restful import Resource
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

    def get(self):
        # TEMPORARY: filters by query param until JWT auth is built.
        # Once auth exists, parent_id/lsa_id should come from the
        # authenticated user's token, not a client-supplied query param
        # (otherwise anyone could view anyone else's bookings).
        parent_id = request.args.get("parent_id", type=int)
        lsa_id = request.args.get("lsa_id", type=int)

        if parent_id:
            bookings = BookingService.list_bookings_for_parent(parent_id)
        elif lsa_id:
            bookings = BookingService.list_bookings_for_lsa(lsa_id)
        else:
            return {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "parent_id or lsa_id query param required",
                    "details": {},
                }
            }, 400

        return BookingResponseSchema(many=True).dump(bookings), 200


class BookingDetailResource(Resource):

    def get(self, booking_id):
        try:
            booking = BookingService.get_booking(booking_id)
        except ResourceNotFoundError as exc:
            return {
                "error": {"code": "NOT_FOUND", "message": str(exc), "details": {}}
            }, 404

        return BookingResponseSchema().dump(booking), 200
