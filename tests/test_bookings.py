from unittest.mock import patch


def _mock_success(*args, **kwargs):
    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"payment_reference": "MOCK-REF-123"}

    return MockResponse()


@patch("app.services.payment_services.requests.post", side_effect=_mock_success)
def test_create_booking_success(mock_post, client, sample_parent, sample_lsa, future_date):
    response = client.post(
        "/api/v1/bookings/",
        json={
            "parent_id": sample_parent.id,
            "lsa_id": sample_lsa.id,
            "session_date": future_date,
        },
    )
    assert response.status_code == 201
    assert response.get_json()["status"] == "pending"


def test_create_booking_missing_fields(client):
    response = client.post("/api/v1/bookings/", json={"parent_id": 1})
    assert response.status_code == 400


@patch("app.services.payment_services.requests.post", side_effect=_mock_success)
def test_create_booking_nonexistent_parent(mock_post, client, sample_lsa, future_date):
    response = client.post(
        "/api/v1/bookings/",
        json={"parent_id": 9999, "lsa_id": sample_lsa.id, "session_date": future_date},
    )
    assert response.status_code == 404