"""**Name:** Israel Adetubo
**Contact:** israetubo@gmail.com"""

import hmac
import hashlib
import os
from decimal import Decimal
from app.extensions import db
from app.models.payment import Payment


class WebhookServiceError(Exception):
    pass


class InvalidSignatureError(WebhookServiceError):
    pass


class UnknownPaymentError(WebhookServiceError):
    pass


class WebhookService:
    WEBHOOK_SECRET = os.environ["RAZORPAY_WEBHOOK_SECRET"]

    @classmethod
    def verify_signature(cls, raw_payload, signature):
        if not signature:
            raise InvalidSignatureError("Missing X-Razorpay-Signature header")
        expected = hmac.new(
            cls.WEBHOOK_SECRET.encode(), raw_payload, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise InvalidSignatureError("Invalid HMAC signature")

    @staticmethod
    def paise_to_rupees(amount_in_paise):
        return Decimal(amount_in_paise) / 100

    @staticmethod
    def process_webhook(data, signature, raw_payload, event_id):
        WebhookService.verify_signature(raw_payload, signature)

        entity = data["payload"]["payment"]["entity"]
        event_type = data["event"]
        provider_reference = entity["order_id"]

        # Idempotency guard: already processed this event_id?
        existing = Payment.query.filter_by(processed_event_id=event_id).first()
        if existing:
            return {
                "received": True,
                "booking_id": existing.booking_id,
                "booking_status": existing.booking.status,
            }

        payment = Payment.query.filter_by(provider_reference=provider_reference).first()
        if not payment:
            raise UnknownPaymentError(
                f"Payment with reference {provider_reference} not found"
            )

        booking = payment.booking

        # If booking is not pending, this is out-of-order / duplicate → no-op
        if booking.status != "pending_payment":
            return {
                "received": True,
                "booking_id": booking.id,
                "booking_status": booking.status,
            }

        if event_type == "payment.captured":
            payment.status = "success"
            payment.processed_event_id = event_id
            booking.status = "confirmed"
        elif event_type == "payment.failed":
            payment.status = "failed"
            payment.processed_event_id = event_id
            booking.status = "payment_failed"

        db.session.commit()
        return {
            "received": True,
            "booking_id": booking.id,
            "booking_status": booking.status,
        }
