def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    from app import (
        models,
    )  # this ensures all models are registered before anything queries the DB

    api = Api(app, prefix="/api/v1")
    from app.resources.booking_resource import BookingResource, BookingDetailResource
    from app.resources.lsa_search_resource import LSASearchResource
    from app.resources.payment_webhook_resource import PaymentWebhookResource

    api.add_resource(BookingResource, "/bookings", "/bookings/")
    api.add_resource(BookingDetailResource, "/bookings/<int:booking_id>")
    api.add_resource(LSASearchResource, "/lsas/search", "/lsas/search/")
    api.add_resource(PaymentWebhookResource, "/payments/webhook", "/payments/webhook/")
    return app
