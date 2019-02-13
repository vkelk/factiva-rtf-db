import os
from dotenv import load_dotenv


load_dotenv('.env')

MAIN_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir))
RTF_DIR = os.path.join(MAIN_DIR, 'rtfs')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASS = os.environ.get('DB_PASS', '')
DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
DB_PORT = os.environ.get('DB_PORT', 5432)
DB_NAME = os.environ.get('DB_NAME', 'factiva')
DB_SCHEMA = os.environ.get('DB_SCHEMA', 'factiva')
