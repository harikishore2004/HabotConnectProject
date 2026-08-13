
from decimal import Decimal

from app.extensions import db
from app.models import Parent, LSAProfile


def seed_data():
    if Parent.query.first() or LSAProfile.query.first():
        print("Seed data already exists, skipping.")
        return

    parents = [
        Parent(full_name="Asha Verma", email="asha.verma@example.com", phone_number="9876543210"),
        Parent(full_name="Rohit Sharma", email="rohit.sharma@example.com", phone_number="9876500000"),
    ]

    lsas = [
        LSAProfile(
            full_name="Priya Nair",
            email="priya.nair@example.com",
            bio="Specialist in early-years reading support.",
            is_available=True,
            hourly_rate=Decimal("650.00"),
            skills=["Reading", "Math", "English"],
        ),
        LSAProfile(
            full_name="Karan Mehta",
            email="karan.mehta@example.com",
            bio="Experienced with autism spectrum support.",
            is_available=True,
            hourly_rate=Decimal("800.00"),
            skills=["Autism Support", "Behavioral Therapy"],
        ),
        LSAProfile(
            full_name="Sneha Kulkarni",
            email="sneha.kulkarni@example.com",
            bio="Math and science tutor for middle schoolers.",
            is_available=False,
            hourly_rate=Decimal("700.00"),
            skills=["Math", "Science"],
        ),
    ]

    db.session.add_all(parents + lsas)
    db.session.commit()
    print(f"Seeded {len(parents)} parents and {len(lsas)} LSAs.")