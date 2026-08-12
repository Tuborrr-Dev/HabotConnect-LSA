"""**Name:** Israel Adetubo
**Contact:** israetubo@gmail.com"""

import logging
from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from app.schemas.webhook_schema import WebhookSchema
from app.services.webhook_service import (
    WebhookService,
    InvalidSignatureError,
    UnknownPaymentError,
)
from app.extensions import db

logger = logging.getLogger(__name__)


class PaymentWebhookResource(Resource):
    def post(self):
        raw_payload = request.get_data()
        signature = request.headers.get("X-Razorpay-Signature")
        event_id = request.headers.get("x-razorpay-event-id")

        try:
            WebhookService.verify_signature(raw_payload, signature)
        except InvalidSignatureError as exc:
            return {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(exc),
                    "details": {},
                }
            }, 400

        if not event_id:
            return {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Missing x-razorpay-event-id header",
                    "details": {},
                }
            }, 400

        schema = WebhookSchema()
        try:
            data = schema.load(request.get_json() or {})
        except ValidationError as err:
            return {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid webhook payload",
                    "details": err.messages,
                }
            }, 400

        try:
            result = WebhookService.process_webhook(
                data, signature, raw_payload, event_id
            )
        except UnknownPaymentError as exc:
            return {
                "error": {"code": "NOT_FOUND", "message": str(exc), "details": {}}
            }, 404
        except Exception:
            db.session.rollback()
            logger.exception("Unexpected error processing webhook")
            return {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {},
                }
            }, 500

        return result, 200
