
from flask import Flask
import logging
from flask_restful import Api
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
    api = Api(app)

    print("API initialized")

    from app.routes import BookingListResource
    from app.routes import LSASearchResource
    from app.routes import MockPaymentResource

    print("Registering BookingListResource...")
    api.add_resource(BookingListResource, "/api/v1/bookings/")

    print("Registering LSASearchResource...")
    api.add_resource(LSASearchResource, "/api/v1/lsas/search/")

    print("Registering MockPaymentResource...")
    api.add_resource(MockPaymentResource, "/api/v1/mock/payment/")

    print("After:", app.url_map)

    from flask_swagger_ui import get_swaggerui_blueprint

    swagger_bp = get_swaggerui_blueprint(
        "/docs", "/static/openapi.yaml", config={"app_name": "LSA Booking API"}
    )
    app.register_blueprint(swagger_bp, url_prefix="/docs")
   
    from app.models import parent, booking, lsa_profile 


    with app.app_context():
        db.create_all()

    return app

def _configure_logging(app: Flask) -> None:
    logging.basicConfig(
        level=app.config.get("LOG_LEVEL", "INFO"),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
