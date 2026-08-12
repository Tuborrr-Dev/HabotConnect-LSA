"""**Name:** Israel Adetubo
**Contact:** israetubo@gmail.com"""

from marshmallow import Schema, fields, validate


# created this schema to be used for searching for LSAs based on their skills and experience
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
    # created hourly_rate and years_experience to be included in the response schema for LSA search results
    hourly_rate = fields.Decimal(as_string=True, places=2)
    years_experience = fields.Integer()
    is_available = fields.Boolean()
    skills = fields.List(fields.Nested(SkillNameSchema))


# the above schema is used to return the LSA search results in a paginated format
