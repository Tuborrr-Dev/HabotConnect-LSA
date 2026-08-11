from datetime import date
from marshmallow import Schema, fields, validate, validates_schema, ValidationError


# this is the input schema for creating a booking, which validates the input data and ensures that all constraints are followed
class BookingCreateSchema(Schema):
    parent_id = fields.Integer(required=True)
    lsa_id = fields.Integer(required=True)
    child_name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    session_date = fields.Date(required=True)
    start_time = fields.Time(required=True, format="%H:%M")
    end_time = fields.Time(required=True, format="%H:%M")
    # so the notes field is optional and if it is returned empty it doesnt break the schema, it will be returned as None if not provided
    notes = fields.String(
        validate=validate.Length(max=500), load_default=None, allow_none=True
    )

    @validates_schema
    def validate_logic(self, data, **kwargs):
        if data["end_time"] <= data["start_time"]:
            raise ValidationError(
                "End time must be strictly after start time.", "end_time"
            )
        if data["session_date"] < date.today():
            raise ValidationError(
                "Session date must not be in the past.", "session_date"
            )


# this is the output schema for a booking, which defines how the booking data will be serialized and returned to the client
class BookingResponseSchema(Schema):
    id = fields.Integer(dump_only=True)
    parent_id = fields.Integer()
    lsa_id = fields.Integer()
    child_name = fields.String()
    session_date = fields.Date()
    start_time = fields.Time(format="%H:%M")
    end_time = fields.Time(format="%H:%M")
    status = fields.String()
    created_at = fields.DateTime()
    notes = fields.String()
