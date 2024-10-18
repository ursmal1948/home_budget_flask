import logging

from flask import Flask, request, jsonify
import flask_praetorian
from app.persistent.entity import UserEntity

guard = flask_praetorian.Praetorian()
logging.basicConfig(level=logging.INFO)


def configure_security(app: Flask):
    guard.init_app(app, UserEntity)

    @app.route('/users/login', methods=['POST'])
    def login():
        data = request.get_json()
        email = data['email']
        password = data['password']
        logging.info(email)
        logging.info(password)
        user = guard.authenticate(email, password)
        logging.info("POI AUTENTYKACJI")
        token = {
            'access_token': guard.encode_jwt_token(user)
        }
        return jsonify(token)

    @app.route('/users/refresh', methods=['POST'])
    def refresh():
        old_token = request.headers.get('Authorization')
        new_token = guard.refresh_jwt_token(old_token)
        token = {
            'access_token': new_token
        }
        return jsonify(token)
