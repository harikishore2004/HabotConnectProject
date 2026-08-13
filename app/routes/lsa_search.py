from flask_restful import Resource
from flask import request
from sqlalchemy import select
from pydantic import ValidationError
from app.schemas import LSASearchRequestchema
from app.models import LSAProfile



class LSASearchResource(Resource):
    def get(self):
        try:
            query_params = LSASearchRequestchema(
                skills=request.args.get("skills"),
                is_available=request.args.get("is_available"),
            )
        except ValidationError as exc:
            return {"error": "Invalid query parameters", "details": exc.errors()}, 400

        # single query, no N+1: skills is a JSON column on the same row
        stmt = select(LSAProfile)

        if query_params.is_available is not None:
            stmt = stmt.where(LSAProfile.is_available == query_params.is_available)

        results = db_session_execute_all(stmt)

        if query_params.skills:
            wanted = {s.lower() for s in query_params.skills}
            results = [
                lsa for lsa in results
                if wanted.intersection({s.lower() for s in (lsa.skills or [])})
            ]

        return {"count": len(results), "results": [lsa.to_dict() for lsa in results]}, 200


def db_session_execute_all(stmt):
    from app.extensions import db
    return db.session.execute(stmt).scalars().all()