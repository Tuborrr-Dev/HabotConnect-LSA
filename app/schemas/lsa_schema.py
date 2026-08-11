from marshmallow import Schema, fields, validate


class SkillNameSchema(Schema):
    name = fields.String()


class LSASearchSchema(Schema):
    skills = fields.String(load_default=None)
    min_experience = fields.Integer(load_default=None, validate=validate.Range(min=0))
    page = fields.Integer(load_default=1, validate=validate.Range(min=1))
    page_size = fields.Integer(load_default=20, validate=validate.Range(min=1, max=100))


class LSAResponseSchema(Schema):
    id = fields.Integer(dump_only=True)
    full_name = fields.String()
    hourly_rate = fields.Decimal(as_string=True, places=2)
    years_experience = fields.Integer()
    is_available = fields.Boolean()
    skills = fields.List(fields.Nested(SkillNameSchema))
