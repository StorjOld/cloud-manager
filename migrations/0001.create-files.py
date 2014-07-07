from yoyo import step

step("""
CREATE TABLE files (
  name varchar,
  size int,
  hash varchar,
  payload text);
    """,
    """DROP TABLE files""")
