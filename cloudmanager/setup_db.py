import sys
from pkg_resources import resource_string

def setup_db(db_uri='test.db'):
    #Import sql schema
    if 'postgres://' in db_uri:

        import psycopg2
        connection = psycopg2.connect(db_uri)
        cursor = connection.cursor()
        cursor.execute(resource_string(__name__, 'schema.sql'))
        connection.commit()
        cursor.close()

    else:

        import sqlite3
        connection = sqlite3.connect(db_uri)
        cursor = connection.cursor()
        schema = resource_string(__name__, 'schema.sql')
        if isinstance(schema, bytes):
            schema = schema.decode("utf-8")
        cursor.executescript(schema)
        connection.commit()
        cursor.close()

    connection.close()

    return True

