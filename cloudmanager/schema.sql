CREATE TABLE files (
  name varchar,
  size int,
  hash varchar,
  payload text);

CREATE TABLE transfer_meter (
  uploaded BIGINT,
  downloaded BIGINT);

INSERT INTO transfer_meter
  SELECT 0, 0
  WHERE NOT EXISTS (SELECT * FROM transfer_meter);

-- Migration: Add synchronization fields
ALTER TABLE files ADD COLUMN blockchain_hash    VARCHAR;
ALTER TABLE files ADD COLUMN exported_timestamp TIMESTAMP;

-- Migration: Meters transferred bytes per month
ALTER TABLE transfer_meter ADD COLUMN month VARCHAR;
CREATE UNIQUE INDEX transfer_meter_month_idx ON transfer_meter(month);

-- Migration 2014-04-24: add blockchain synchronization table
CREATE TABLE blockchain_state (
  last_known_block integer);

INSERT INTO blockchain_state
  SELECT 0
  WHERE NOT EXISTS (SELECT * FROM blockchain_state);

