import logging
from app import create_app
from app.util import seed_data
app = create_app()

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Adding dummy values to the database")
    with app.app_context():
        seed_data()
    app.run(host="0.0.0.0", port=5000)