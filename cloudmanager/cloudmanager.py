import os
import plowshare
import json

import file_database
import storage
import transfer_meter
import payload
import helpers

class CloudManager(object):
    """Manages files uploaded to cloud services.

    This cloud manager uses plowshare to upload files
    to file locker providers, and keeps track of them
    in a local database. It also keeps a local cache.

    """
    RedundancyLevel = 3

    Plowshare = plowshare.Plowshare
    Database  = file_database.FileDatabase
    Storage   = storage.Storage
    Meter     = transfer_meter.TransferMeter

    def __init__(self, database_path, storage_path, storage_size):
        """Initialize a CloudManager instance.

        Arguments:
        database_path -- Path to a sqlite3 database
        storage_path  -- Path to the local cache directory
        storage_size  -- Maximum number of bytes to keep in local cache

        """
        self.file_database = self.Database(database_path)
        self.plowshare     = self.Plowshare()
        self.storage       = self.Storage(storage_path, storage_size)
        self.meter         = self.Meter(database_path)

    def close(self):
        """Clean up all resources."""
        self.file_database.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def upload(self, file_path):
        """Add a file to the cloud.

        If the given file didn't exist yet, this method
        makes room for it (by deleting older cached files).
        This file will be put in a queue to be uploaded to
        multiple cloud hosts.

        """
        key = helpers.sha256(file_path)
        if self.exists(key):
            return key

        needed = os.path.getsize(file_path)

        if not self.make_room_for(needed):
            return False

        saved_path = self.storage.add(file_path, key)
        self.meter.measure_incoming(needed)
        self.file_database.store(key, needed, saved_path, None)
        return key


    def cloud_sync(self):
        """Upload files to the cloud.

        This method checks the database for all files that
        haven't yet been uploaded to the cloud, and processes
        them.

        """
        for record in self.upload_candidates():
            uploads = self.plowshare.upload(
                self.storage.path(record.name),
                self.RedundancyLevel)

            # Probably not a good idea to have the serialization code in here.
            info = json.dumps(payload.to_dict(payload.build(
                record.name,
                record.hash,
                record.size,
                uploads)))

            self.file_database.set_payload(record.hash, info)
            self.meter.measure_outgoing(record.size * self.RedundancyLevel)


    def warm_up(self, file_hash):
        """Warm up the cache for the given hash

        This method makes room for the given file,
        and then fetches it from one of the cloud hosts.
        It returns the full path of the file.

        """
        record = self.file_database.fetch(file_hash)
        if record is None:
            return None

        if self.storage.is_cached(record.name):
            self.meter.measure_outgoing(record.size)
            return self.storage.path(record.name)

        if record.payload is None:
            return False

        if not self.make_room_for(record.size):
            return False

        info = payload.from_dict(json.loads(record.payload))

        self.plowshare.download(info.uploads, self.storage.storage_path, record.name)

        self.meter.measure_incoming(record.size)
        self.meter.measure_outgoing(record.size)

        return self.storage.path(record.name)


    def download(self, file_hash):
        """Same as warm_up."""
        return self.warm_up(file_hash)


    def info(self, file_hash):
        """Return file information for a given hash."""
        record = self.file_database.fetch(file_hash)
        if record is None or record.payload is None:
            return None

        return json.loads(record.payload)


    def upload_queue_info(self):
        """Return the cloud hosting queue size."""
        info = { "size": 0, "count": 0 }
        for record in self.file_database.upload_candidates():
            info["size"]  += record.size
            info["count"] += 1

        return info

    def blockchain_queue_info(self):
        """Return the blockchain queue size."""
        info = { "size": 0, "count": 0 }

        for record in self.file_database.blockchain_candidates():
            info["size"]  += record.size
            info["count"] += 1

        return info

    def used_space(self):
        """Return this node's storage usage."""
        return self.storage.used()

    def capacity(self):
        """Return this node's local storage capacity."""
        return self.storage.size()

    def usage_ratio(self):
        """Return the percentage of used space."""
        return 1.0 * self.storage.used() / self.storage.size()

    def total_incoming(self):
        """Return the total number of bytes downloaded."""
        return self.meter.total_incoming()

    def total_outgoing(self):
        """Return the total number of bytes uploaded."""
        return self.meter.total_outgoing()

    def current_incoming(self):
        """Return the number of bytes downloaded for the month."""
        return self.meter.current_incoming()

    def current_outgoing(self):
        """Return the number of bytes uploaded for the month."""
        return self.meter.current_outgoing()

    def exists(self, file_hash):
        """Check if a given file is in this cloud system."""
        return self.file_database.fetch(file_hash) != None

    def on_cache(self, file_hash):
        """Check if a given file is on cache."""
        record = self.file_database.fetch(file_hash)

        return record != None and self.storage.is_cached(record.name)

    def data_dump(self, data_limit):
        """Dump json to be inserted in the blockchain."""
        files = self.export_candidates(data_limit)
        self.file_database.mark_exported(files)

        if len(files) == 0:
            return None

        return json.dumps([json.loads(record.payload) for record in files])

    def data_load(self, data, blockchain_hash):
        """Load json from the blockchain."""
        payloads = payload.from_blockchain_payload(data)
        if payloads is None:
            return None

        files = [{
            "name": p.name,
            "hash": p.hash,
            "size": p.size,
            "payload": payload.serialize(p) } for p in payloads]

        return self.file_database.import_files(files, blockchain_hash)


    def make_room_for(self, needed):
        """Make room in the storage space.

        This method deletes files from the storage space
        until the given number of bytes fits into it.

        """
        if not self.storage.fits(needed):
            return False

        used_space = self.storage.used()
        while not self.storage.fits(used_space + needed):
            to_be_removed = self.removal_candidate(needed)

            self.storage.remove(to_be_removed.name)
            used_space -= to_be_removed.size

        return True

    def removal_candidate(self, needed):
        for f in self.file_database.removal_candidates(needed):
            if self.storage.is_cached(f.name):
                return f

        return None

    def export_candidates(self, data_limit):
        files = []
        byte_count = 2

        for record in self.file_database.blockchain_candidates():
            json = record.payload
            # "[]", ", ", files
            if 2 + byte_count + 2*len(files) + len(json) > data_limit:
                break

            byte_count += len(json)
            files.append(record)

        return files

    def upload_candidates(self):
        return self.file_database.upload_candidates()


    def sync_status(self):
        """Return synchronization status information.

        This method returns a dictionary with two lists,
        one containing all the files that are waiting to
        be uploaded to the cloud hosting websites, and
        another one containing all the files that are
        waiting to be uploaded to the blockchain.

        """
        not_yet_blockchained = self.file_database.blockchain_candidates()
        not_yet_cloudshared  = self.file_database.upload_candidates()

        return {
            "cloud_queue":      [self.dict_description(f) for f in not_yet_cloudshared],
            "blockchain_queue": [self.dict_description(f) for f in not_yet_blockchained]
        }


    def dict_description(self, f):
        base = {
            "filename": f.name,
            "filehash": f.hash,
            "filesize": f.size,
        }

        if f.payload is not None:
            base['uploads'] = json.loads(f.payload)['uploads']
            base['datetime'] = json.loads(f.payload)['datetime']

        return base
