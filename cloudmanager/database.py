import sqlite3

def connect(**kwargs):
    db = sqlite3.connect(**kwargs)

    db.row_factory = sqlite3.Row

    return db
