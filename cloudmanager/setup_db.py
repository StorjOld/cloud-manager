import sys
import sqlite3
from pkg_resources import resource_string

def setup_db(db_name='test.db'):
    #Import sql schema
    connection = sqlite3.connect(db_name)

    cursor = connection.cursor()
    cursor.executescript(resource_string(__name__, 'schema.sql'))

    connection.commit()
    cursor.close()
    connection.close()


if __name__ == "__main__":
    setup_db(sys.argv[1])