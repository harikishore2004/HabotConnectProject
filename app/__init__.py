
from flask import Flask
import logging
from app.extensions import db
from app.config import get_settings


def create_app(testing: bool = False) -> Flask:
    """Application factory — builds and configures the Flask app."""
    app = Flask(__name__)

    settings = get_settings()
    #segregated the testing db uri with the dev db uri
    if testing:
        app.config["SQLALCHEMY_DATABASE_URI"] = settings.SQLALCHEMY_TEST_DATABASE_URI
        app.config["TESTING"] = True
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = settings.SQLALCHEMY_DATABASE_URI

    _configure_logging(app)

    db.init_app(app)

   
    from app.models import parent, booking, lsa_profile 


    with app.app_context():
        db.create_all()

    return app

def _configure_logging(app: Flask) -> None:
    logging.basicConfig(
        level=app.config.get("LOG_LEVEL", "INFO"),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
