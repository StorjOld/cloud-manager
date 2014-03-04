import os
import plowshare

import file_database
import storage
import transfer_meter
import helpers

class CloudManager(object):
    """Manages files uploaded to cloud services.

    This cloud manager uses plowshare to upload files
    to file locker providers, and keeps track of them
    in a local database. It also keeps a local cache.

    """
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
        makes room for it (by deleting older cached files)
        and then uploads it to three different cloud hosts.
        """
        # Check if file exists
        key = helpers.sha256(file_path)
        if self.exists(key):
            return False

        needed = os.path.getsize(file_path)

        if not self.make_room_for(needed):
            return False

        info = self.plowshare.upload(file_path, 3)
        saved_path = self.storage.add(file_path, key)
        self.file_database.store(saved_path, info)
        self.meter.measure_upload(needed)
        return key

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
            return self.storage.path(record.name)

        if not self.make_room_for(record.size):
            return False

        self.plowshare.download(record.payload, self.storage.storage_path)
        self.meter.measure_upload(record.size)
        return self.storage.path(record.name)

    def download(self, file_hash):
        """Same as warm_up."""
        return self.warm_up(file_hash)


    def used_space(self):
        return self.storage.used()

    def usage_ratio(self):
        """Return the percentage of used space."""
        return 1.0 * self.storage.used() / self.storage.size()

    def downloaded(self):
        """Return the number of bytes downloaded"""
        return self.meter.total_download()

    def uploaded(self):
        """Return the number of bytes uploaded"""
        return self.meter.total_upload()

    def exists(self, file_hash):
        """Check if a given file is in this cloud system."""
        return self.file_database.fetch(file_hash) != None

    def on_cache(self, file_hash):
        """Check if a given file is on cache."""
        record = self.file_database.fetch(file_hash)

        return record != None and self.storage.is_cached(record.name)


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
