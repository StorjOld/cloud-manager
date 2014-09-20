from . import database

class ChainState(object):
    """Register blockchain known state.

    Stores which was the last block that was
    synchronized into the database.

    """

    def __init__(self, database_path):
        """Initialize the chain state.

        Arguments:
        database_path -- database connection string.

        """
        self.db = database.connect(database_path)

    def last_known_block(self):
        """Retrieve the last known block height."""

        cursor = self.db.cursor()
        cursor.execute(
            """
                SELECT last_known_block FROM blockchain_state;
            """)

        row = cursor.fetchone()

        return 0 if row is None else row['last_known_block']

    def visit_block(self, block_height):
        """Mark the given block height as visited."""

        cursor = self.db.cursor()
        cursor.execute(
            """
                UPDATE blockchain_state SET last_known_block = %s;
            """, [block_height])

        self.db.commit()
