import os
from dotenv import load_dotenv


load_dotenv(dotenv_path='.env')

DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASS = os.environ.get('DB_PASS', '')
DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
DB_PORT = os.environ.get('DB_PORT', 5432)
DB_NAME = os.environ.get('DB_NAME', 'factiva')
DB_SCHEMA = os.environ.get('DB_SCHEMA', 'factiva')

HIV4_DICTIONARY_FILE = 'HIV-4.csv'
LM_DICTIONARY_FILE = 'LoughranMcDonald_MasterDictionary_2016.csv'
MAIN_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir))
RTF_DIR = os.path.join(MAIN_DIR, 'rtfs')
DICTS_FOLDER = os.path.join(MAIN_DIR, 'dictionaries')
