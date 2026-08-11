from datetime import date
from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class BookingCreateSchema(Schema):
    parent_id = fields.Integer(required=True)
    lsa_id = fields.Integer(required=True)
    child_name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    session_date = fields.Date(required=True)
    start_time = fields.Time(required=True, format="%H:%M")
    end_time = fields.Time(required=True, format="%H:%M")
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


class BookingResponseSchema(Schema):
    id = fields.Integer(dump_only=True)
    parent_id = fields.Integer()
    # this is added to improve query optimization and reduce the number of queries needed to get the parent name
    parent_name = fields.String(attribute="parent.full_name", dump_only=True)
    lsa_id = fields.Integer()
    lsa_name = fields.String(attribute="lsa.full_name", dump_only=True)
    child_name = fields.String()
    session_date = fields.Date()
    start_time = fields.Time(format="%H:%M")
    end_time = fields.Time(format="%H:%M")
    status = fields.String()
    created_at = fields.DateTime()
    notes = fields.String()
