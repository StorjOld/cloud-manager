from yoyo import step

transaction(
  step(
    """ALTER TABLE transfer_meter ALTER COLUMN uploaded TYPE BIGINT;""",
    """ALTER TABLE transfer_meter ALTER COLUMN uploaded TYPE INTEGER;"""),
  step(
    """ALTER TABLE transfer_meter ALTER COLUMN downloaded TYPE BIGINT;""",
    """ALTER TABLE transfer_meter ALTER COLUMN downloaded TYPE INTEGER;"""))
