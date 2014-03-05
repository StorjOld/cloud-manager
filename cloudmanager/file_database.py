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

    def store(self, file_name, cloud_info):
        """Store information regarding an uploaded file.

        Arguments:
        file_name  -- Basename of the uploaded file
        cloud_info -- Information provided by plowshare
        """
        cursor = self.db.cursor()
        cursor.execute(
            """
                INSERT INTO files (name, hash, size, payload)
                VALUES(?, ?, ?, ?);
            """,
            [file_name,
              cloud_info["filehash"],
              int(cloud_info["filesize"]),
              json.dumps(cloud_info)])

        self.db.commit()

    def data_dump(self, data_limit):
        """Dumps a blockchain json.

        This method dumps a json with as many file metadata
        as it can fit in data_limit (in bytes). If there is
        nothing to export, it returns None.

        """
        records = self.exportee_candidates(data_limit)
        if len(records) == 0:
            return None

        cursor = self.db.cursor()
        cursor.execute(
            """
                UPDATE files SET exported_timestamp = datetime('now')
                WHERE hash IN ({0})
            """.format(','.join(
                ["'%s'" % r['hash'] for r in records])))

        self.db.commit()

        # Build the json manually so that we don't have to
        # json.loads() the payload just to json.dumps() it
        # right after.
        return "[%s]" % ','.join([r['payload'] for r in records])

    def exportee_candidates(self, data_limit):
        """Select files to export."""

        cursor = self.db.cursor()
        cursor.execute(
            """
                SELECT hash, payload FROM files
                WHERE blockchain_hash IS NULL
                AND (exported_timestamp IS NULL OR
                    exported_timestamp < DATE(datetime('now'), '-1 hour'))
                ORDER BY length(payload);
            """)

        files      = []
        byte_count = 2

        for record in cursor:
            json = record['payload']
            # two bytes for the array boundaries, one per comma delimiter (n-1),
            # and all the payloads.
            if 2 + len(files) + byte_count + len(json) > data_limit:
                break

            byte_count += len(json)
            files.append(record)

        return files

    def detected_on_blockchain(self, file_hash, blockchain_hash):
        """Mark a file identified by the given hash as being in the blockchain."""

        cursor = self.db.cursor()
        cursor.execute(
            """UPDATE files SET blockchain_hash = ? WHERE hash = ?""",
            [blockchain_hash, file_hash])

        self.db.commit()


    def removal_candidates(self, size):
        """List files to be removed.

        This method determines which file should
        be removed in order to free the given number
        of bytes. It yields them, ordered by preference.

        """
        cursor = self.db.cursor()
        result = cursor.execute(
            """
                SELECT * FROM
                    (SELECT * FROM files
                        WHERE size >= ?
                        ORDER BY size ASC) x
                UNION
                SELECT * FROM
                    (SELECT * FROM files
                        WHERE size < ?
                        ORDER BY size DESC) y;
            """, [size, size])

        while True:
            row = result.fetchone()
            if row is None:
                return

            yield self.convert(row)

        result.close()

    def convert(self, row):
        """Convert a database row into a file record."""
        if row == None:
            return None

        return FileRecord(row)
