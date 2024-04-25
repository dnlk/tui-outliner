
import os

PROJECT_ROOT_DIR = os.path.dirname(__file__)
DB_DIR = os.path.join(PROJECT_ROOT_DIR, 'database')
DB_PATH = os.path.join(DB_DIR, 'db.sqlite')
SCHEMA_PATH = os.path.join(DB_DIR, 'schema')
ROOT_NODE_ID = -1
ROOT_NODE_TEXT = 'ROOT'
MAX_NUM_SEARCH_RESULTS = 4
BACKUPS_DIR = os.path.join(DB_DIR, 'backups')
