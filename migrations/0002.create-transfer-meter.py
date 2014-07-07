from yoyo import step

step("""
CREATE TABLE transfer_meter (
  uploaded integer,
  downloaded integer);
    """,
    """DROP TABLE transfer_meter""")
