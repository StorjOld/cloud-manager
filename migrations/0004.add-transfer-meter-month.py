from yoyo import step

transaction(
  step(
    """ALTER TABLE transfer_meter ADD COLUMN month VARCHAR;""",
    """ALTER TABLE transfer_meter DROP COLUMN month;"""),
  step("""CREATE UNIQUE INDEX transfer_meter_month_idx ON transfer_meter(month);"""))
