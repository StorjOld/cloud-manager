import database
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
        database_path -- database connection string.

        """
        self.db = database.connect(database_path)

    def current_month_timestamp(self):
        """Return the current month identifier."""
        dt = datetime.datetime.now()

        return "{0:04}-{1:02}".format(dt.year, dt.month)


    def measure_download(self, byte_count):
        """Add a given amount to the total download count."""
        month = self.current_month_timestamp()

        cursor = self.db.cursor()
        cursor.execute(
            """
                INSERT OR REPLACE INTO transfer_meter (uploaded, downloaded, month)
                VALUES (
                  COALESCE((SELECT uploaded FROM transfer_meter WHERE month = ?), 0),
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
                  COALESCE((SELECT downloaded FROM transfer_meter WHERE month = ?), 0),
                  ?);
            """,
            [byte_count, month, month, month])

        self.db.commit()


    def total_download(self):
        """Retrieve the total number of bytes downloaded."""
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT SUM(downloaded) AS total FROM transfer_meter;")

        return cursor.fetchone()['total']

    def total_upload(self):
        """Retrieve the total number of bytes uploaded."""
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT SUM(uploaded) AS total FROM transfer_meter;")

        return cursor.fetchone()['total']


    def current_download(self):
        """Retrieve the number of bytes downloaded for the current month."""
        cursor = self.db.cursor()
        cursor.execute(
            """
                SELECT downloaded AS total FROM transfer_meter
                WHERE month = ?;
            """,
            [self.current_month_timestamp()])

        row = cursor.fetchone()

        return 0 if row is None else row['total']


    def current_upload(self):
        """Retrieve the number of bytes uploaded for the current month."""
        cursor = self.db.cursor()
        cursor.execute(
            """
                SELECT uploaded AS total FROM transfer_meter
                WHERE month = ?;
            """,
            [self.current_month_timestamp()])

        row = cursor.fetchone()

        return 0 if row is None else row['total']

    def measure_outgoing(self, byte_count):
        self.measure_upload(byte_count)

    def measure_incoming(self, byte_count):
        self.measure_download(byte_count)

    def total_incoming(self):
        return self.total_download()

    def total_outgoing(self):
        return self.total_upload()

    def current_incoming(self):
        return self.current_download()

    def current_outgoing(self):
        return self.current_upload()

