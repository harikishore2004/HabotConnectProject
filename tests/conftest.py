from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app import create_app
from app.extensions import db as _db
from app.models import Parent, LSAProfile


@pytest.fixture()
def app():
    app = create_app(testing=True)
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def sample_parent(app):
    parent = Parent(full_name="Test Parent", email="parent@example.com")
    _db.session.add(parent)
    _db.session.commit()
    return parent


@pytest.fixture()
def sample_lsa(app):
    lsa = LSAProfile(
        full_name="Test LSA",
        email="lsa@example.com",
        is_available=True,
        hourly_rate=Decimal("500.00"),
        skills=["Math"],
    )
    _db.session.add(lsa)
    _db.session.commit()
    return lsa


@pytest.fixture()
def future_date():
    return (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()