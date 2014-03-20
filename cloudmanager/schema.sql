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

ALTER TABLE transfer_meter ADD COLUMN month VARCHAR;
CREATE UNIQUE INDEX transfer_meter_month_idx ON transfer_meter(month);
