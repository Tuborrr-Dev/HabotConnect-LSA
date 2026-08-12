import json
import hmac
import hashlib
from datetime import date
from tests.base import BaseTestCase
from app.models.booking import Booking
from app.models.payment import Payment
from app.services.webhook_service import WebhookService


class TestPaymentWebhook(BaseTestCase):
    def _make_signature(self, payload):
        return hmac.new(
            WebhookService.WEBHOOK_SECRET.encode(), payload, hashlib.sha256
        ).hexdigest()

    def _webhook_payload(self, event, order_id, status="captured"):
        return {
            "event": event,
            "payload": {
                "payment": {
                    "entity": {
                        "id": f"pay_{order_id}",
                        "order_id": order_id,
                        "amount": 2500,
                        "currency": "INR",
                        "status": status,
                    }
                }
            },
        }

    def _headers(self, raw, event_id):
        return {
            "X-Razorpay-Signature": self._make_signature(raw),
            "x-razorpay-event-id": event_id,
        }

    def test_tc14_payment_success(self):
        parent = self.create_parent()
        lsa = self.create_lsa()
        booking = self.create_booking(
            parent_id=parent.id,
            lsa_id=lsa.id,
            session_date=date(2026, 8, 20),
            start_time="14:00",
            end_time="15:00",
            status="pending_payment",
        )
        self.create_payment(booking_id=booking.id, provider_reference="pay_ref_4471")

        payload = self._webhook_payload("payment.captured", "pay_ref_4471")
        raw = json.dumps(payload).encode()

        response = self.client.post(
            "/api/v1/payments/webhook/",
            data=raw,
            content_type="application/json",
            headers=self._headers(raw, "evt_9f8a3b2c"),
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["booking_status"], "confirmed")

        updated = Booking.query.get(booking.id)
        self.assertEqual(updated.status, "confirmed")

    def test_tc15_payment_failure(self):
        parent = self.create_parent()
        lsa = self.create_lsa()
        booking = self.create_booking(
            parent_id=parent.id,
            lsa_id=lsa.id,
            session_date=date(2026, 8, 20),
            start_time="14:00",
            end_time="15:00",
            status="pending_payment",
        )
        self.create_payment(booking_id=booking.id, provider_reference="pay_ref_4471")

        payload = self._webhook_payload(
            "payment.failed", "pay_ref_4471", status="failed"
        )
        raw = json.dumps(payload).encode()

        response = self.client.post(
            "/api/v1/payments/webhook/",
            data=raw,
            content_type="application/json",
            headers=self._headers(raw, "evt_failure_1"),
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["booking_status"], "payment_failed")

    def test_tc16_duplicate_event_id(self):
        parent = self.create_parent()
        lsa = self.create_lsa()
        booking = self.create_booking(
            parent_id=parent.id,
            lsa_id=lsa.id,
            session_date=date(2026, 8, 20),
            start_time="14:00",
            end_time="15:00",
            status="pending_payment",
        )
        payment = self.create_payment(
            booking_id=booking.id, provider_reference="pay_ref_4471"
        )

        payload = self._webhook_payload("payment.captured", "pay_ref_4471")
        raw = json.dumps(payload).encode()
        headers = self._headers(raw, "evt_duplicate")

        r1 = self.client.post(
            "/api/v1/payments/webhook/",
            data=raw,
            content_type="application/json",
            headers=headers,
        )
        self.assertEqual(r1.status_code, 200)

        r2 = self.client.post(
            "/api/v1/payments/webhook/",
            data=raw,
            content_type="application/json",
            headers=headers,
        )
        self.assertEqual(r2.status_code, 200)

        updated = Payment.query.get(payment.id)
        self.assertEqual(updated.processed_event_id, "evt_duplicate")

    def test_tc17_invalid_signature(self):
        payload = self._webhook_payload("payment.captured", "pay_ref_1")
        raw = json.dumps(payload).encode()

        response = self.client.post(
            "/api/v1/payments/webhook/",
            data=raw,
            content_type="application/json",
            headers={
                "X-Razorpay-Signature": "bad_signature",
                "x-razorpay-event-id": "evt_1",
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_tc18_unknown_provider_reference(self):
        payload = self._webhook_payload("payment.captured", "unknown_ref")
        raw = json.dumps(payload).encode()

        response = self.client.post(
            "/api/v1/payments/webhook/",
            data=raw,
            content_type="application/json",
            headers=self._headers(raw, "evt_1"),
        )
        self.assertEqual(response.status_code, 404)
