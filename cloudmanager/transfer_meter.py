import sqlite3

class TransferMeter(object):
    """Register transfer statistics.

    Stores the total number of bytes that
    were downloaded and uploaded. One must
    specify a path to the database where
    this information is to be stored.

    This database must have a table called
    transfer_meter with two integer columns,
    uploaded and downloaded.

    """
    def __init__(self, database_path):
        """Initialize a transfer meter.

        Arguments:
        database_path -- Path to the sqlite3 database.

        """
        self.db = sqlite3.connect(database_path)
        self.db.row_factory = sqlite3.Row

    def measure_download(self, byte_count):
        """Add a given amount to the total download count."""
        cursor = self.db.cursor()
        cursor.execute(
            """
                UPDATE transfer_meter
                SET downloaded = downloaded + ?;
            """,
            [byte_count])

        self.db.commit()

    def measure_upload(self, byte_count):
        """Add a given amount to the total upload count."""
        cursor = self.db.cursor()
        cursor.execute(
            """
                UPDATE transfer_meter
                SET uploaded = uploaded + ?;
            """,
            [byte_count])

        self.db.commit()

    def total_download(self):
        """Retrieve the total number of bytes downloaded."""
        row = self.db.cursor().execute(
            "SELECT downloaded FROM transfer_meter;")

        return row['downloaded']

    def total_upload(self):
        """Retrieve the total number of bytes uploaded."""
        row = self.db.cursor().execute(
            "SELECT uploaded FROM transfer_meter;")

        return row['uploaded']
