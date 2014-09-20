from yoyo import step

step("""
CREATE TABLE transfer_meter (
  uploaded BIGINT,
  downloaded BIGINT);
    """,
    """DROP TABLE transfer_meter""")
