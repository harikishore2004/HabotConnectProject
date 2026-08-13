import logging
import uuid

import requests
from requests.exceptions import RequestException, Timeout

from app.config import get_settings

logger = logging.getLogger(__name__)


class PaymentServiceError(Exception):
    """Raised when the mock payment/verification service call fails."""


def verify_and_charge(booking_payload: dict) -> str:
    """
    calls a mock internel payment API.
    """
    settings = get_settings()
    url = settings.MOCK_PAYMENT_API_URL

    try:
        response = requests.post(
            url,
            json=booking_payload,
            timeout=settings.MOCK_API_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        payment_reference = data.get("payment_reference", str(uuid.uuid4()))
        logger.info("Payment verified successfully: ref=%s", payment_reference)
        return payment_reference

    except Timeout:
        logger.error("Payment service timed out calling %s", url)
        raise PaymentServiceError("Payment verification service timed out.")

    except RequestException as exc:
        logger.error("Payment service call failed: %s", exc)
        raise PaymentServiceError("Payment verification service is unavailable.")

    except ValueError:
        logger.error("Payment service returned invalid JSON")
        raise PaymentServiceError("Payment verification service returned an invalid response.")