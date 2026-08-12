"""**Name:** Israel Adetubo
**Contact:** israetubo@gmail.com"""

import uuid
from decimal import Decimal


class MockPaymentGateway:
    """Mock Razorpay integration.

    In production this would call Razorpay's Orders API via `requests`:
        POST https://api.razorpay.com/v1/orders
        {"amount": <paise>, "currency": "INR", "receipt": <booking_id>}

    so here we are simulating the response shape locally so the rest of the app
    (booking_service, webhook_service) can be built and tested against
    the real Razorpay data shape without needing live API keys yet.
    """

    @staticmethod
    def rupees_to_paise(amount_rupees):
        return int(Decimal(amount_rupees) * 100)

    @staticmethod
    def create_order(booking_id, amount_rupees, currency="INR"):
        amount_paise = MockPaymentGateway.rupees_to_paise(amount_rupees)
        return {
            "order_id": f"order_mock_{uuid.uuid4().hex[:14]}",
            "amount": amount_paise,
            "currency": currency,
            "status": "created",
            "receipt": str(booking_id),
        }
