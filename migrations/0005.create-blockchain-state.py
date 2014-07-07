from yoyo import step

transaction(
  step(
    """
CREATE TABLE blockchain_state (
  last_known_block integer);
    """,
    """DROP TABLE blockchain_state;"""),
  step("""INSERT INTO blockchain_state VALUES(0);"""))
