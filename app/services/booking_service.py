"""**Name:** Israel Adetubo
**Contact:** israetubo@gmail.com"""

from decimal import Decimal
from datetime import datetime
from app.extensions import db
from app.models.booking import Booking
from app.models.lsa_profile import LSAProfile
from app.models.parent import Parent
from app.models.payment import Payment
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.services.payment_gateway import MockPaymentGateway


class BookingServiceError(Exception):
    pass


class ResourceNotFoundError(BookingServiceError):
    pass


class LSANotAvailableError(BookingServiceError):
    pass


class SlotUnavailableError(BookingServiceError):
    def __init__(self, message, conflicting_booking_id=None):
        super().__init__(message)
        self.conflicting_booking_id = conflicting_booking_id


class BookingService:

    @staticmethod
    def create_booking(data):
        parent = db.session.get(Parent, data["parent_id"])
        if not parent:
            raise ResourceNotFoundError(f"Parent {data['parent_id']} not found")

        lsa = db.session.get(LSAProfile, data["lsa_id"])
        if not lsa:
            raise ResourceNotFoundError(f"LSA {data['lsa_id']} not found")

        if not lsa.is_available:
            raise LSANotAvailableError(f"LSA {lsa.id} is not available")

        # App-level overlap check with row lock which reduces race conditions;
        # a database-level exclusion constraint will be added in migrations
        # for full protection under concurrent requests)
        overlap = (
            Booking.query.filter(
                Booking.lsa_id == lsa.id,
                Booking.session_date == data["session_date"],
                Booking.status.in_(["pending_payment", "confirmed"]),
                Booking.start_time < data["end_time"],
                Booking.end_time > data["start_time"],
            )
            .with_for_update()
            .first()
        )

        if overlap:
            raise SlotUnavailableError(
                conflicting_booking_id=overlap.id,
            )

        start_dt = datetime.combine(data["session_date"], data["start_time"])
        end_dt = datetime.combine(data["session_date"], data["end_time"])
        hours = Decimal((end_dt - start_dt).total_seconds()) / Decimal(3600)
        amount = lsa.hourly_rate * hours

        booking = Booking(
            parent_id=data["parent_id"],
            lsa_id=data["lsa_id"],
            child_name=data["child_name"],
            session_date=data["session_date"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            notes=data.get("notes"),
            status="pending_payment",
        )
        db.session.add(booking)
        db.session.flush()

        # Create a mock payment order with Razorpay and store the provider reference in the Payment model
        order = MockPaymentGateway.create_order(booking.id, amount)
        payment = Payment(
            booking_id=booking.id,
            amount=amount,
            status="pending",
            provider_reference=order["order_id"],
        )

        try:
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            if "no_overlapping_bookings" in str(exc):
                raise SlotUnavailableError(
                    "This LSA already has a booking that overlaps "
                    "the requested time window."
                ) from exc
            raise

        return booking

    @staticmethod
    def get_booking(booking_id):
        booking = Booking.query.options(
            joinedload(Booking.parent), joinedload(Booking.lsa)
        ).get(booking_id)
        if not booking:
            raise ResourceNotFoundError(f"Booking {booking_id} not found")
        return booking

    @staticmethod
    def list_bookings_for_parent(parent_id):
        return (
            Booking.query.options(joinedload(Booking.parent), joinedload(Booking.lsa))
            .filter(Booking.parent_id == parent_id)
            .order_by(Booking.session_date.desc())
            .all()
        )

    @staticmethod
    def list_bookings_for_lsa(lsa_id):
        return (
            Booking.query.options(joinedload(Booking.parent), joinedload(Booking.lsa))
            .filter(Booking.lsa_id == lsa_id)
            .order_by(Booking.session_date.desc())
            .all()
        )
