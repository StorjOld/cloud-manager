import sqlite3

class TransferMeter(object):
    def __init__(self, database_path):
        self.db = sqlite3.connect(database_path)
        self.db.row_factory = sqlite3.Row

    def measure_download(self, byte_count):
        cursor = self.db.cursor()
        cursor.execute(
            """
                UPDATE transfer_meter
                SET downloaded = downloaded + ?;
            """,
            [byte_count])

        self.db.commit()

    def measure_upload(self, byte_count):
        cursor = self.db.cursor()
        cursor.execute(
            """
                UPDATE transfer_meter
                SET uploaded = uploaded + ?;
            """,
            [byte_count])

        self.db.commit()

    def total_download(self):
        row = self.db.cursor().execute(
            "SELECT downloaded FROM transfer_meter;")

        return row['downloaded']

    def total_upload(self):
        row = self.db.cursor().execute(
            "SELECT uploaded FROM transfer_meter;")

        return row['uploaded']
