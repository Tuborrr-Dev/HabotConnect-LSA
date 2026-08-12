"""**Name:** Israel Adetubo
**Contact:** israetubo@gmail.com"""

from flask import request
from flask_restful import Resource
from sqlalchemy.orm import selectinload
from marshmallow import ValidationError
from app.models.lsa_profile import LSAProfile
from app.models.skill import Skill
from app.schemas.lsa_schema import LSASearchSchema, LSAResponseSchema


# This resource handles the search for LSAs based on skills and experience. It supports pagination and returns the results in a structured format.
class LSASearchResource(Resource):
    def get(
        self,
    ):  # <-- This method handles GET requests to search for LSAs based on query parameters such as skills, minimum experience, page number, and page size. It validates the input parameters, constructs a query to filter LSAs based on the provided criteria, and returns the results in a paginated format.
        # Load and validate query parameters using the LSASearchSchema
        schema = LSASearchSchema()
        try:
            params = schema.load(request.args.to_dict())
        except ValidationError as err:
            return {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid query parameters",
                    "details": err.messages,
                }
            }, 400

        query = LSAProfile.query.options(selectinload(LSAProfile.skills)).filter_by(
            is_available=True
        )

        if params.get("skills"):
            skill_names = [s.strip() for s in params["skills"].split(",")]
            query = (
                query.join(LSAProfile.skills)
                .filter(Skill.name.in_(skill_names))
                .distinct()
            )

        # Filter by minimum experience if provided
        if params.get("min_experience"):
            query = query.filter(
                LSAProfile.years_experience >= params["min_experience"]
            )

        total = query.count()
        page = params.get("page", 1)
        page_size = params.get("page_size", 20)
        lsas = query.offset((page - 1) * page_size).limit(page_size).all()
        # Return the results in a structured format with pagination details
        return {
            "results": LSAResponseSchema(many=True).dump(lsas),
            "page": page,
            "page_size": page_size,
            "total_results": total,
        }, 200
