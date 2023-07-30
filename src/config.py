import os
import logging
import sqlalchemy as db

HOST = '0.0.0.0' 
PORT = 5000
BUFFER_SIZE = 1024

DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

DATABASE_ADDRESS = f'{DB_HOST}:{DB_PORT}/{DB_NAME}'
DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DATABASE_ADDRESS}'
ENGINE = db.create_engine(DATABASE_URI)

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S'
)
