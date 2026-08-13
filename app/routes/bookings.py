import logging

from flask import request
from flask_restful import Resource
from pydantic import ValidationError

from app.extensions import db
from app.models import Parent, LSAProfile, BookingRequest
from app.schemas import BookingRequestSchema
from app.services import verify_and_charge, PaymentServiceError

logger = logging.getLogger(__name__)


class BookingListResource(Resource):
    def post(self):
        raw = request.get_json(silent=True)
        if raw is None:
            return {"error": "Request body must be valid JSON."}, 400

        try:
            payload = BookingRequestSchema(**raw)
        except ValidationError as exc:
            return {"error": "Validation failed", "details": exc.errors()}, 400

        parent = db.session.get(Parent, payload.parent_id)
        if parent is None:
            return {"error": f"Parent {payload.parent_id} not found."}, 404

        lsa = db.session.get(LSAProfile, payload.lsa_id)
        if lsa is None:
            return {"error": f"LSA {payload.lsa_id} not found."}, 404

        if not lsa.is_available:
            return {"error": "Selected LSA is not currently available."}, 409

        try:
            payment_reference = verify_and_charge(
                {
                    "parent_id": payload.parent_id,
                    "lsa_id": payload.lsa_id,
                    "amount": float(lsa.hourly_rate),
                }
            )
        except PaymentServiceError as exc:
            logger.warning("Booking rejected due to payment failure: %s", exc)
            return {"error": str(exc)}, 502

        booking = BookingRequest(
            parent_id=payload.parent_id,
            lsa_id=payload.lsa_id,
            session_date=payload.session_date,
            notes=payload.notes,
            payment_reference=payment_reference,
        )
        db.session.add(booking)
        db.session.commit()

        logger.info("Booking created: id=%s", booking.id)
        return booking.to_dict(), 201