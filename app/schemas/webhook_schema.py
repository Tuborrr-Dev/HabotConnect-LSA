"""**Name:** Israel Adetubo
**Contact:** israetubo@gmail.com"""

from marshmallow import Schema, fields, validate


# the below scheme mirros razorpay's webhook payload for payment events, specifically for the payment.captured and payment.failed events. It is used to validate the incoming webhook payload from Razorpay to ensure that it contains the expected fields and data types.
# so the webhook payload is a dictionary with two keys: "event" and "payload". The "event" key is a string that indicates the type of event that triggered the webhook, and the "payload" key is a nested dictionary that contains the details of the payment event. The "payload" dictionary has a single key, "payment", which is another nested dictionary that contains the details of the payment itself. The "payment" dictionary has several keys, including "id", "order_id", "amount", "currency", and "status", which correspond to the fields in the PaymentEntitySchema.
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
