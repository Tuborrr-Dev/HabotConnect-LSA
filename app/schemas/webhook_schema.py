from marshmallow import Schema, fields, validate


class PaymentEntitySchema(Schema):
    id = fields.String(required=True)
    order_id = fields.String(required=True)
    amount = fields.Integer(required=True)
    currency = fields.String(required=True, validate=validate.OneOf(["INR"]))
    status = fields.String(required=True)


class PaymentPayloadSchema(Schema):
    entity = fields.Nested(PaymentEntitySchema, required=True)


class WebhookPayloadSchema(Schema):
    payment = fields.Nested(PaymentPayloadSchema, required=True)


class WebhookSchema(Schema):
    event = fields.String(
        required=True, validate=validate.OneOf(["payment.captured", "payment.failed"])
    )
    payload = fields.Nested(WebhookPayloadSchema, required=True)
