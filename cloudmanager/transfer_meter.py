import sqlite3
import datetime

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

    def current_month_timestamp(self):
        """Return the current month identifier."""
        dt = datetime.datetime.now()

        return "{0}-{1}".format(dt.year, dt.month)


    def measure_download(self, byte_count):
        """Add a given amount to the total download count."""
        month = self.current_month_timestamp()

        cursor = self.db.cursor()
        cursor.execute(
            """
                INSERT OR REPLACE INTO transfer_meter (uploaded, downloaded, month)
                VALUES (
                  (SELECT uploaded FROM transfer_meter WHERE month = ?),
                  ? + COALESCE((SELECT downloaded FROM transfer_meter WHERE month = ?), 0),
                  ?);
            """,
            [month, byte_count, month, month])

        self.db.commit()

    def measure_upload(self, byte_count):
        """Add a given amount to the total upload count."""
        month = self.current_month_timestamp()

        cursor = self.db.cursor()
        cursor.execute(
            """
                INSERT OR REPLACE INTO transfer_meter (uploaded, downloaded, month)
                VALUES (
                  ? + COALESCE((SELECT uploaded FROM transfer_meter WHERE month = ?), 0),
                  (SELECT downloaded FROM transfer_meter WHERE month = ?),
                  ?);
            """,
            [byte_count, month, month, month])

        self.db.commit()


    def total_download(self):
        """Retrieve the total number of bytes downloaded."""
        result = self.db.cursor().execute(
            "SELECT SUM(downloaded) AS total FROM transfer_meter;")

        return result.fetchone()['total']

    def total_upload(self):
        """Retrieve the total number of bytes uploaded."""
        result = self.db.cursor().execute(
            "SELECT SUM(uploaded) AS total FROM transfer_meter;")

        return result.fetchone()['total']


    def current_download(self):
        """Retrieve the number of bytes downloaded for the current month."""
        result = self.db.cursor().execute(
            """
                SELECT downloaded AS total FROM transfer_meter
                WHERE month = ?;
            """,
            [self.current_month_timestamp()])

        row = result.fetchone()

        return 0 if row is None else row['total']


    def current_upload(self):
        """Retrieve the number of bytes uploaded for the current month."""
        result = self.db.cursor().execute(
            """
                SELECT uploaded AS total FROM transfer_meter
                WHERE month = ?;
            """,
            [self.current_month_timestamp()])

        row = result.fetchone()

        return 0 if row is None else row['total']
