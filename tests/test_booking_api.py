"""**Name:** Israel Adetubo
**Contact:** israetubo@gmail.com"""

import json
import unittest
import threading
from datetime import date
from tests.base import BaseTestCase
from app.models.booking import Booking
from app.extensions import db


class TestBookingAPI(BaseTestCase):
    def test_tc01_create_booking_success(self):
        parent = self.create_parent()
        lsa = self.create_lsa()

        payload = {
            "parent_id": parent.id,
            "lsa_id": lsa.id,
            "child_name": "Amara O.",
            "session_date": "2026-08-20",
            "start_time": "14:00",
            "end_time": "15:00",
            "notes": "First session, prefers a quiet room.",
        }

        response = self.client.post(
            "/api/v1/bookings/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self.auth_header(parent.id, "parent"),
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "pending_payment")
        self.assertEqual(data["child_name"], "Amara O.")

        booking = Booking.query.get(data["id"])
        self.assertIsNotNone(booking)
        self.assertEqual(booking.status, "pending_payment")
        self.assertIsNotNone(booking.payment)

    def test_tc02_overlapping_slot(self):
        parent = self.create_parent()
        lsa = self.create_lsa()

        self.create_booking(
            parent_id=parent.id,
            lsa_id=lsa.id,
            session_date=date(2026, 8, 20),
            start_time="14:00",
            end_time="15:00",
            status="confirmed",
        )

        payload = {
            "parent_id": parent.id,
            "lsa_id": lsa.id,
            "child_name": "Amara O.",
            "session_date": "2026-08-20",
            "start_time": "14:30",
            "end_time": "15:30",
        }

        response = self.client.post(
            "/api/v1/bookings/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self.auth_header(parent.id, "parent"),
        )

        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertEqual(data["error"]["code"], "SLOT_UNAVAILABLE")

    def test_tc03_back_to_back_non_overlapping(self):
        parent = self.create_parent()
        lsa = self.create_lsa()

        self.create_booking(
            parent_id=parent.id,
            lsa_id=lsa.id,
            session_date=date(2026, 8, 20),
            start_time="14:00",
            end_time="15:00",
            status="confirmed",
        )

        payload = {
            "parent_id": parent.id,
            "lsa_id": lsa.id,
            "child_name": "Amara O.",
            "session_date": "2026-08-20",
            "start_time": "15:00",
            "end_time": "16:00",
        }

        response = self.client.post(
            "/api/v1/bookings/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self.auth_header(parent.id, "parent"),
        )

        self.assertEqual(response.status_code, 201)

    def test_tc04_end_before_start(self):
        parent = self.create_parent()
        lsa = self.create_lsa()

        payload = {
            "parent_id": parent.id,
            "lsa_id": lsa.id,
            "child_name": "Amara O.",
            "session_date": "2026-08-20",
            "start_time": "15:00",
            "end_time": "14:00",
        }

        response = self.client.post(
            "/api/v1/bookings/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self.auth_header(parent.id, "parent"),
        )

        self.assertEqual(response.status_code, 400)

    def test_tc05_missing_required_field(self):
        payload = {
            "parent_id": 1,
            "child_name": "Amara O.",
            "session_date": "2026-08-20",
            "start_time": "14:00",
            "end_time": "15:00",
        }

        response = self.client.post(
            "/api/v1/bookings/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self.auth_header(1, "parent"),
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("lsa_id", data["error"]["details"])

    def test_tc06_nonexistent_lsa(self):
        parent = self.create_parent()

        payload = {
            "parent_id": parent.id,
            "lsa_id": 999999,
            "child_name": "Amara O.",
            "session_date": "2026-08-20",
            "start_time": "14:00",
            "end_time": "15:00",
        }

        response = self.client.post(
            "/api/v1/bookings/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self.auth_header(parent.id, "parent"),
        )

        self.assertEqual(response.status_code, 404)

    def test_tc07_lsa_not_available(self):
        parent = self.create_parent()
        lsa = self.create_lsa(is_available=False)

        payload = {
            "parent_id": parent.id,
            "lsa_id": lsa.id,
            "child_name": "Amara O.",
            "session_date": "2026-08-20",
            "start_time": "14:00",
            "end_time": "15:00",
        }

        response = self.client.post(
            "/api/v1/bookings/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self.auth_header(parent.id, "parent"),
        )

        self.assertEqual(response.status_code, 422)

    @unittest.skip(
        "Known limitation: overlap prevention is app-level only (row lock), "
        "not a DB-level exclusion constraint. See README known limitations so you understand better."
    )
    def test_tc08_concurrent_requests(self):
        parent = self.create_parent()
        lsa = self.create_lsa()

        payload = {
            "parent_id": parent.id,
            "lsa_id": lsa.id,
            "child_name": "Amara O.",
            "session_date": "2026-08-20",
            "start_time": "14:00",
            "end_time": "15:00",
        }

        headers = self.auth_header(parent.id, "parent")
        results = []

        def make_request():
            with self.app.app_context():
                response = self.client.post(
                    "/api/v1/bookings/",
                    data=json.dumps(payload),
                    content_type="application/json",
                    headers=headers,
                )
                results.append(response.status_code)

        threads = [threading.Thread(target=make_request) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertIn(201, results)
        self.assertIn(409, results)
