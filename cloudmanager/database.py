import sqlite3

def connect(*args, **kwargs):
    db = sqlite3.connect(*args, **kwargs)

    db.row_factory = sqlite3.Row

    return db
