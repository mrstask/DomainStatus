import logging
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

log = logging.getLogger("uvicorn")
log.setLevel(logging.DEBUG)
DATABASE_URL = 'sqlite:///test.db'
#
# env = load_dotenv()
# AUTH_KEY = os.getenv('AUTH_KEY')
# DB_WORKER_PORT = os.getenv('DB_WORKER_PORT')
#
#
# class PostgresConfiguration:
#     POSTGRES_USER = os.getenv('POSTGRES_USER')
#     POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
#     POSTGRES_ADDRESS = os.getenv('POSTGRES_ADDRESS')
#     POSTGRES_PORT = os.getenv('POSTGRES_PORT')
#     POSTGRES_DB = os.getenv('POSTGRES_DB')
#
#     @property
#     def postgres_db_path(self):
#         return f'postgres://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@' \
#                f'{self.POSTGRES_ADDRESS}:' \
#                f'{self.POSTGRES_PORT}/{self.POSTGRES_DB}'
#
#
# class PgHandler:
#     def __init__(self, db_string):
#         self.engine = create_engine(db_string)
#         self.session = sessionmaker(bind=self.engine)
#
#     def get_session(self):
#         return self.session
#
#
# session_handler = PgHandler(PostgresConfiguration().postgres_db_path)
