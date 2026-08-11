from flask import Flask
from flask_restful import Api
from app.config import config_by_name
from app.extensions import db, migrate, ma


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    api = Api(app, prefix="/api/v1")

    from app.resources.booking_resource import BookingResource
    from app.resources.lsa_search_resource import LSASearchResource
    from app.resources.payment_webhook_resource import PaymentWebhookResource

    api.add_resource(BookingResource, "/bookings/")
    api.add_resource(LSASearchResource, "/lsas/search/")
    api.add_resource(PaymentWebhookResource, "/payments/webhook/")

    return app
