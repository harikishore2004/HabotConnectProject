import random
import time
import uuid

from flask import request
from flask_restful import Resource


class MockPaymentResource(Resource):
    """
    simulates a third-party payment/verification API.
    Lives inside the same app purely for local dev convenience 
    """

    def post(self):
        payload = request.get_json(silent=True) or {}

        time.sleep(0.2)

        if random.random() < 0.1:
            return {"error": "Payment gateway declined the transaction."}, 502

        return {
            "status": "success",
            "payment_reference": f"MOCK-{uuid.uuid4().hex[:10].upper()}",
            "amount_charged": payload.get("amount"),
        }, 200