import sqlite3

class FileDatabase(object):
    """Stores information on all uploaded files.

    """
    def __init__(self, database_path):
        self.database_path = database_path
        self.db = sqlite3.connect(database_path)

    def fetch(self, file_hash):
        cursor = self.db.cursor()
        result = cursor.execute(
            "SELECT * FROM files WHERE file_hash = ?",
            file_hash)

        row = result.fetchone()

        return row

    def store(self, file_name, cloud_info, is_cached):
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO files (name, hash, payload, is_cached) VALUES(?, ?, ?, ?);",
            file_name,
            cloud_info["filehash"],
            json.dumps(cloud_info),
            is_cached)

    def removed_from_cache(self, file_hash):
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE files SET is_cached = ? WHERE file_hash = ?;",
            False, file_hash)

    def restored_to_cache(self, file_hash):
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE files SET is_cached = ? WHERE file_hash = ?;",
            True, file_hash)

