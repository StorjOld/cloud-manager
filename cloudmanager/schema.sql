CREATE TABLE files (
  name varchar,
  size int,
  hash varchar,
  payload text);

CREATE TABLE transfer_meter (
  uploaded integer,
  downloaded integer);

INSERT INTO transfer_meter VALUES(0, 0);
