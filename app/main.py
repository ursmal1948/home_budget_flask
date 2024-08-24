from flask import Flask, jsonify, Response

import logging
from app.config import DB_URL

logging.basicConfig(level=logging.INFO)


def create_app() -> Flask:
    app = Flask(__name__)
    with app.app_context():
        app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL

        app.config['SQLALCHEMY_ECHO'] = True

        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        logging.info("HEERLLO")

        # sa.init_app(app)

    return app


if __name__ == '__main__':
    create_app()
