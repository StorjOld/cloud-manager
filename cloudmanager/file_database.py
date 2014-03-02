import sqlite3
import json

class FileDatabase(object):
    """Stores information on all uploaded files.

    """
    def __init__(self, database_path):
        self.database_path = database_path
        self.db = sqlite3.connect(database_path)
        self.db.row_factory = sqlite3.Row

    def fetch(self, file_hash):
        cursor = self.db.cursor()
        result = cursor.execute(
            "SELECT * FROM files WHERE hash = ?",
            [file_hash])

        row = result.fetchone()

        return self.convert(row)

    def store(self, file_name, cloud_info, is_cached):
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO files (name, hash, size, payload, is_cached) VALUES(?, ?, ?, ?, ?);",
            [file_name,
              cloud_info["filehash"],
              int(cloud_info["filesize"]),
              json.dumps(cloud_info),
              is_cached])

        self.db.commit()

    def removed_from_cache(self, file_hash):
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE files SET is_cached = ? WHERE hash = ?;",
            [False, file_hash])

    def restored_to_cache(self, file_hash):
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE files SET is_cached = ? WHERE hash = ?;",
            [True, file_hash])

    def closest_cache_in_size(self, size):
        cursor = self.db.cursor()
        result = cursor.execute(
            """
              SELECT * FROM
                  (SELECT * FROM files WHERE size >= ? ORDER BY size LIMIT 1) x
              UNION
              SELECT * FROM
                  (SELECT * FROM files ORDER BY size DESC LIMIT 1) y;""", [size])

        row = result.fetchone()
        return self.convert(row)

    def convert(self, row):
      if row == None:
          return None

      return {
          'name': row['name'],
          'hash': row['hash'],
          'size': row['size'],
          'payload': json.loads(row['payload']),
          'is_cached': row['is_cached']
      }
