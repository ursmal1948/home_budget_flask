from dotenv import load_dotenv
import os
from os import getenv

load_dotenv(override=True)

# Parametr override True w funkcji load_dotenv() z biblitoeki python-dotenv  pozwala na
# nadpisywanie istniejacych wartosci zmiennych srodowiskowych zaladowanych do srodowiska
# uruchimieniowego Pythona nowymi wartosciami z pliku .env. Domyslnie, kiedy ladujesz
#  zmienne srodowiskowe za pomoca load_dotenv(), nowe wartosci z pliku .env nie zastepuja
# juz isteniejacych wartosci zmiennych srodowiskowych. Ustawienie override=True zmienia
# to zachowanie, pozwalajac nowo zaladowanym wartosciom z pliku .env na nadpisywanie
# wszelkich wczesniej ustawionych wartoisc.

# ------------------------------------------------------------
# DB CONFIGURATION
# ------------------------------------------------------------
DB_USERNAME = getenv('DB_USERNAME', 'user')
DB_PASSWORD = getenv('DB_PASSWORD', 'user1234')
DB_PORT = getenv('DB_PORT', '3307')
DB_TEST_PORT = getenv('DB_PORT', '3308')
DB_NAME = getenv('DB_NAME', 'db_1')
DB_HOST = getenv('DB_HOST', 'mysql')
DB_URL = f'mysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# ------------------------------------------------------------
# MAIL CONFIGURATION
# ------------------------------------------------------------
MAIL_SETTINGS = {
    'MAIL_SERVER': getenv('MAIL_SERVER', 'smtp.gmail.com'),
    'MAIL_PORT': int(getenv('MAIL_PORT', 465)),
    'MAIL_USE_SSL': bool(getenv('MAIL_USE_SSL', True)),
    'MAIL_USERNAME': getenv('MAIL_USERNAME', 'ula.malin35@gmail.com'),
    'MAIL_PASSWORD': getenv('MAIL_PASSWORD', 'dmmzadtkkgjteysw'),
}

# ------------------------------------------------------------
# CONFIGURATION OF TOKEN TO ACTIVATE REGISTERED USER
# ------------------------------------------------------------
ACTIVATION_TOKEN_EXPIRATION_TIME_IN_SECONDS = int(getenv('ACTIVATION_TOKEN_EXPIRATION_TIME_IN_SECONDS', '300'))
ACTIVATION_TOKEN_LENGTH = int(getenv('ACTIVATION_TOKEN_LENGTH', '30'))

# ------------------------------------------------------------
# SECURITY
# ------------------------------------------------------------

SECRET_KEY = getenv('SECRET_KEY')
JWT_ACCESS_LIFESPAN = int(getenv('JWT_ACCESS_LIFESPAN'))
JWT_REFRESH_LIFESPAN = int(getenv('JWT_REFRESH_LIFESPAN'))

SECURITY_SETTINGS = {
    'SECRET_KEY': SECRET_KEY,
    'JWT_ACCESS_LIFESPAN': {'hours': JWT_ACCESS_LIFESPAN},
    'JWT_REFRESH_LIFESPAN': {'days': JWT_REFRESH_LIFESPAN}
}
