import sqlite3
import psycopg2
import psycopg2.extras
try:
    import urlparse
except:
    import urllib.parse as urlparse

def connect(uri):
    result = urlparse.urlparse(uri)
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname

    if result.scheme == 'postgres' or result.scheme == 'postgresql':
        return connect_psycopg2(
                database=database,
                user=username,
                password=password,
                host=hostname)

    return None

def connect_sqlite3(*args, **kwargs):
    db = sqlite3.connect(*args, **kwargs)

    db.row_factory = sqlite3.Row

    return db

def connect_psycopg2(*args, **kwargs):
    db = psycopg2.connect(*args, **kwargs)

    db.cursor_factory = psycopg2.extras.DictCursor

    return db
