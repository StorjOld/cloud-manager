import sqlite3
import json

class FileRecord(object):
    """FileRecord represents a file tracked by the database.

    It exposes the file attributes as members,
    instead of relying on a dictionary.
    """
    def __init__(self, record):
        self.name      = record['name']
        self.hash      = record['hash']
        self.size      = record['size']
        self.payload   = json.loads(record['payload'])
        self.is_cached = record['is_cached']

class FileDatabase(object):
    """FileDatabase stores information on all uploaded files.

    """
    def __init__(self, database_path):
        self.database_path = database_path
        self.db = sqlite3.connect(database_path)
        self.db.row_factory = sqlite3.Row

    def close(self):
        """Release all resources."""
        self.db.close()

    def fetch(self, file_hash):
        """Retrieve a file record associated to the given hash."""
        cursor = self.db.cursor()
        result = cursor.execute(
            "SELECT * FROM files WHERE hash = ?",
            [file_hash])

        row = result.fetchone()

        return self.convert(row)

    def store(self, file_name, cloud_info, is_cached):
        """Store information regarding an uploaded file.

        Arguments:
        file_name  -- Basename of the uploaded file
        cloud_info -- Information provided by plowshare
        is_cached  -- Boolean indicating if the file is in local cache
        """
        cursor = self.db.cursor()
        cursor.execute(
            """
                INSERT INTO files (name, hash, size, payload, is_cached)
                VALUES(?, ?, ?, ?, ?);
            """,
            [file_name,
              cloud_info["filehash"],
              int(cloud_info["filesize"]),
              json.dumps(cloud_info),
              is_cached])

        self.db.commit()

    def removed_from_cache(self, file_hash):
        """Notify the database that a file was removed from local cache."""
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE files SET is_cached = ? WHERE hash = ?;",
            [False, file_hash])
        self.db.commit()

    def restored_to_cache(self, file_hash):
        """Notify the database that a file was restored to local cache."""
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE files SET is_cached = ? WHERE hash = ?;",
            [True, file_hash])
        self.db.commit()

    def closest_cache_in_size(self, size):
        """Determine which file should be removed to free a given number of bytes."""
        cursor = self.db.cursor()
        result = cursor.execute(
            """
                SELECT * FROM
                    (SELECT * FROM files
                        WHERE size >= ? AND is_cached
                        ORDER BY size LIMIT 1) x
                UNION
                SELECT * FROM
                    (SELECT * FROM files
                        WHERE is_cached
                        ORDER BY size DESC LIMIT 1) y;
            """, [size])

        row = result.fetchone()
        return self.convert(row)

    def convert(self, row):
        """Convert a database row into a file record."""
        if row == None:
            return None

        return FileRecord(row)
