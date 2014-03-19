CREATE TABLE files (
  name varchar,
  size int,
  hash varchar,
  payload text);

CREATE TABLE transfer_meter (
  uploaded integer,
  downloaded integer);

INSERT INTO transfer_meter VALUES(0, 0);

ALTER TABLE files ADD COLUMN blockchain_hash    VARCHAR;
ALTER TABLE files ADD COLUMN exported_timestamp INTEGER;
ALTER TABLE files ADD COLUMN request_token      VARCHAR;
