import os
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
from dotenv import load_dotenv


load_dotenv()

database_uri = os.environ['DATABASE3']
database_user = os.environ['USER4SQL3']
database_password = os.environ['PASSWORD4SQL3']

pool = SimpleConnectionPool(minconn=1, maxconn=10, database=database_uri, user=database_user, password=database_password)


@contextmanager
def get_connection():
    connection = pool.getconn()

    try:
        yield connection
    finally:
        pool.putconn(connection)
