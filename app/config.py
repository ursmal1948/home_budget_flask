from dotenv import load_dotenv
import os

load_dotenv()

# ------------------------------------------------------------
# DB CONFIGURATION
# ------------------------------------------------------------
DB_USERNAME = os.getenv('DB_USERNAME', 'user')
DB_PASSOWRD = os.getenv('DB_PASSWORD', 'user1234')
DB_PORT = os.getenv('DB_PORT', '3307')
DB_NAME = os.getenv('DB_NAME', 'db_1')
DB_HOST = os.getenv('DB_HOST', 'mysql')
DB_URL = f'mysql://{DB_USERNAME}:{DB_PASSOWRD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
