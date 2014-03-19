import sqlite3

class FileRecord(object):
    """FileRecord represents a file tracked by the database.

    It exposes the file attributes as members,
    instead of relying on a dictionary.
    """
    def __init__(self, record):
        self.name      = record['name']
        self.hash      = record['hash']
        self.size      = record['size']
        self.payload   = record['payload']

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
            """SELECT * FROM files WHERE hash = ?""",
            [file_hash])

        row = result.fetchone()

        return self.convert(row)


    def key_by_token(self, token):
        """Retrieve a file hash associated with the given request token."""
        cursor = self.db.cursor()
        result = cursor.execute(
            """SELECT hash FROM files WHERE request_token = ?""",
            [token])

        row = result.fetchone()

        if row is None:
            return None

        return row['hash']


    def store(self, key, size, name, payload, token=None):
        """Store information regarding an uploaded file.

        Arguments:
        key        -- Unique file identifier (usually sha256)
        size       -- Size of the file, in bytes
        name       -- File name
        payload    -- Blockchain payload
        token      -- Request token

        """
        cursor = self.db.cursor()
        cursor.execute(
            """
                INSERT INTO files (name, hash, size, payload, request_token)
                SELECT ?, ?, ?, ?, ?
                WHERE NOT EXISTS (SELECT 1 FROM files WHERE hash = ?);
            """,
            [name, key, size, payload, token, key])

        self.db.commit()


    def set_payload(self, key, payload):
        """Store payload for an existing file."""

        cursor = self.db.cursor()
        cursor.execute(
            """
                UPDATE files SET payload = ? WHERE hash = ?
            """,
            [payload, key])

        self.db.commit()


    def import_files(self, records, blockchain_hash):
        """Import file metadata associated with a blockchain hash.

        This method loads all file metadata within the
        given payload. It updates all included files to
        register the blockchain identifier.

        """
        files = [self.convert(r) for r in records]

        for f in files:
            self.store(f.hash, f.size, f.name, f.payload, None)

        cursor = self.db.cursor()
        cursor.execute(
            """
                UPDATE files set blockchain_hash = ?
                WHERE hash IN ({0})
            """.format(','.join(
                ["'%s'" % f.hash for f in files])),
            [blockchain_hash])

        self.db.commit()
        return True


    def mark_exported(self, files):
        cursor = self.db.cursor()
        cursor.execute(
            """
                UPDATE files SET exported_timestamp = datetime('now')
                WHERE hash IN ({0})
            """.format(','.join(
                ["'%s'" % f.hash for f in files])))

        self.db.commit()


    def blockchain_candidates(self):
        """Iterate through unexported files."""

        cursor = self.db.cursor()
        result = cursor.execute(
            """
                SELECT * FROM files
                WHERE blockchain_hash IS NULL
                AND payload IS NOT NULL
                AND (exported_timestamp IS NULL OR
                    exported_timestamp < DATE(datetime('now'), '-1 hour'))
                ORDER BY length(payload);
            """)

        while True:
            row = result.fetchone()
            if row is None:
                return

            yield self.convert(row)

        result.close()


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
                        AND payload IS NOT NULL
                        ORDER BY size ASC) x
                UNION
                SELECT * FROM
                    (SELECT * FROM files
                        WHERE size < ?
                        AND payload IS NOT NULL
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
