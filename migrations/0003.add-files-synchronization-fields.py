from yoyo import step

transaction(
  step(
    """ALTER TABLE files ADD COLUMN blockchain_hash VARCHAR;""",
    """ALTER TABLE files DROP COLUMN blockchain_hash;"""),
  step(
    """ALTER TABLE files ADD COLUMN exported_timestamp TIMESTAMP;""",
    """ALTER TABLE files DROP COLUMN exported_timestamp;"""))
