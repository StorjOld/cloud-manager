import sys
import sqlite3
from pkg_resources import resource_string

if __name__ == "__main__":
    connection = sqlite3.connect(sys.argv[1])

    cursor = connection.cursor()
    cursor.executescript(resource_string(__name__, 'schema.sql'))

    connection.commit()
    cursor.close()
    connection.close()
