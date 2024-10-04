from flask import (
    Flask,
    Blueprint,
    request,
    make_response,
    current_app
)
from functools import wraps
from werkzeug.security import check_password_hash
import datetime
import jwt
from app.persistent.entity import UserEntity
from app.service.configuration import user_service
from app.persistent.repository import user_repository

#
import logging
from logging import error

logging.basicConfig(level=logging.INFO)


def configure_security(app: Flask) -> None:
    # ---------------------------------------------
    # LOGOWANIE
    # ---------------------------------------------

    @app.route('/users/login', methods=['POST'])
    def login():
        data = request.get_json()
        name = data['name']
        password = data['password']
        user = user_repository.find_by_name(name)

        if not user:
            return make_response({'message': 'Authentication - user not found [1]!'}, 400)

        if not user.is_active:
            return make_response({'message': 'Authentication - user is not active [2]'}, 500)

        if not user.check_password(password):
            return make_response({'message': 'Authentication - password is not correct [2]'}, 400)

        access_token_exp = int(
            (datetime.datetime.now(datetime.UTC) + datetime.timedelta(
                minutes=app.config['JWT_ACCESS_MAX_AGE'])).timestamp())
        refresh_token_exp = int(
            (datetime.datetime.now(datetime.UTC) + datetime.timedelta(
                minutes=app.config['JWT_REFRESH_MAX_AGE'])).timestamp())

        access_token_payload = {
            'iat': datetime.datetime.now(datetime.UTC),
            'exp': access_token_exp,
            'sub': user.id,
            'role': user.role,
        }

        # access token exp, refresh token ma w sobie refresh token exp. i na tej posdtaiwe
        # okresalym czy mozemy wygenerowac nowy token.
        refresh_token_payload = {
            'iat': datetime.datetime.now(datetime.UTC),
            'exp': refresh_token_exp,
            'sub': user.id,
            'role': user.role,
            'access_token_exp': access_token_exp
        }

        access_token = jwt.encode(access_token_payload, app.config['JWT_SECRET'], algorithm=app.config['JWT_AUTHTYPE'])
        refresh_token = jwt.encode(refresh_token_payload, app.config['JWT_SECRET'],
                                   algorithm=app.config['JWT_AUTHTYPE'])

        # wersja 1 przygotowujemy json body z tokenami
        response_body = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        response = make_response(response_body, 201)

        # wersja 2 ustaiwamy headery

        response.headers['Access-Token'] = access_token
        response.headers['Refresh-Token'] = refresh_token

        # wersja 3 ustawiamy cookies

        response.set_cookie('AccessToken', access_token, httponly=True)
        response.set_cookie('RefreshToken', refresh_token, httponly=True)

        return response

    # ---------------------------------------------
    # REFRESH TOKEN
    # ---------------------------------------------
    @app.route('/users/refresh', methods=['POST'])
    def refresh():
        # w json body bedziemy przesylac refresh token, lub mozesz go pobrac z cookies.
        request_data = request.get_json()
        refresh_token = request_data['token']
        # refresh_token = request.headers.get(['Refresh-Token')
        # refresh_token = request.cookies.get('RefreshToken')
        logging.info("********************")
        logging.info(refresh_token)
        # dokdujmey refresh token
        decoded_refresh_token = jwt.decode(refresh_token,
                                           app.config['JWT_SECRET'],
                                           algorithms=[app.config['JWT_AUTHTYPE']])
        logging.info("TIMESTAMPSSSSSSSS")

        # todo dorob sprawdzenie czy masz ciagle aktywny access token. Musze sie odwolac
        # do decoded_refresh token i jest opcja access_token. I sprawdzam
        # czy access token nie ma czasu wygasniecia przed aktyalnym czasem.

        if decoded_refresh_token['access_token_exp'] < datetime.datetime.now(datetime.UTC).timestamp():
            return make_response({'message': 'Cannot refresh token - access token has been expired'})

        new_access_token_exp = int(
            (datetime.datetime.now(datetime.UTC) + datetime.timedelta(
                minutes=app.config['JWT_ACCESS_MAX_AGE'])).timestamp())

        access_token_payload = {
            'iat': datetime.datetime.now(datetime.UTC),
            'exp': new_access_token_exp,
            'sub': decoded_refresh_token['sub'],
            'role': decoded_refresh_token['role'],
        }

        refresh_token_payload = {
            'iat': datetime.datetime.now(datetime.UTC),
            'exp': decoded_refresh_token['exp'],
            'sub': decoded_refresh_token['sub'],
            'role': decoded_refresh_token['role'],
            'access_token_exp': new_access_token_exp
        }

        access_token = jwt.encode(access_token_payload, app.config['JWT_SECRET'], algorithm=app.config['JWT_AUTHTYPE'])
        refresh_token = jwt.encode(refresh_token_payload, app.config['JWT_SECRET'],
                                   algorithm=app.config['JWT_AUTHTYPE'])

        # wersja 1 przygotouwjym json body z tokenami
        response_body = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        response = make_response(response_body, 201)

        # wrsja2 wersja z headarami
        response.headers['Access-Token'] = access_token
        response.headers['Refresh-Token'] = refresh_token

        # wersja 3 ustawiamy cookies
        response.set_cookie('AccessToken', access_token, httponly=True)
        response.set_cookie('RefreshToken', refresh_token, httponly=True)
        return response

    # mam access token, refresh token. Do czasu wygadnisecia refresh tokena, jesli
    # z kazdym razem dostarczam refresh token z aktywnym access tokene, to mam
    # fajnie wszystkosie odswieza.
    # mamy pracownika, przychodzi rano i sie loguje
    # jego aktywnosc jest mierzona  przez access token jezelin nie odchodzi
    # od komputera na dluzej niz 5 minut, to jak sobie klika to wszystko sie odswieza
    # nic nie musi robic. Aplikacja za akzdym razme moze pobierac refresh tokena, zwracac
    # nowego access tokena, za kazdym requestem access token wyciagany jest przez backend. to
    # wszystko sie kreci. Chyba ze ktos pojdzie od komputera np na 5 minut, Jak kots nie przyjdzie,
    # nie zdazy to przkeireowany zostanie na strone logowania.

    # ---------------------------------------------
    # DEKORATOR DO ATORYZACJI.
    # ---------------------------------------------
    # request moze byc obslugiwany przed admina i usera.


def authorize(roles: list[str] | None = None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):  # ta funkcja bedzie obtoczona, ta z naszym requestem
            try:

                # pobieranie tokena z headera.

                # w tej funkcji pobieramy access token (z naglowka, cookies itp)
                access_token = request.cookies.get('access_token', None)
                # jakby robic headarami, to zapisac do header Authorization
                header = request.headers['Authorization']
                if not header:
                    return make_response({'message': 'Authorization failed - no header'})

                # kowencnja mowi, ze jak wysylamy acccest tokenw naglowkyu autorhization ton nalezy
                # poprzedzic go Bearer odstep
                if not header.startswith(current_app.config['JWT_PREFIX']):
                    return make_response({'message': 'Authorization failed - access token without prefix'}, 401)

                # logging.info(header)
                # oddzielamy prefix od tokena
                access_token = header.split(' ')[1]

                decoded_access_token = jwt.decode(access_token, current_app.config['JWT_SECRET'],
                                                  algorithms=[current_app.config['JWT_AUTHTYPE']])
                # decode sprawdzi czy access token ma dobry expiratio time, czy jwt secret
                # sie zgfadza cxzy algorytm sie zgadza.

                if roles and decoded_access_token['role'].lower() not in [r.lower() for r in roles]:
                    return make_response({'message': 'Access denied'}, 403)


            except Exception as error:
                logging.info(error)
                logging.info(repr(error))
                return make_response({'message': "Authrozation failed"}, 401)

            return f(*args, **kwargs)

        return decorated_function

    return decorator

# przy decode jest sprawdzamy czas tokena.
