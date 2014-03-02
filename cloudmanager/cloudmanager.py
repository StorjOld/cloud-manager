import os
import file_database
import storage
import helpers
import plowshare

class CloudManager(object):
    Plowshare = plowshare.Plowshare
    Database  = file_database.FileDatabase
    Storage   = storage.Storage

    def __init__(self, database_path, storage_path, storage_size):
        self.file_database = self.Database(database_path)
        self.plowshare     = self.Plowshare()
        self.storage       = self.Storage(storage_path, storage_size)

    def close(self):
        self.file_database.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def upload(self, file_path):
        """Adds a file to the cloud.

        If the given file didn't exist yet, this method
        makes room for it (by deleting older cached files)
        and then uploads it to three different cloud hosts.
        """
        # Check if file exists
        key = helpers.sha256(file_path)
        if self.exists(key):
            return False

        needed = os.path.getsize(file_path)

        if self.make_room_for(needed) == False:
            return False

        info = self.plowshare.upload(file_path, 3)
        saved_path = self.storage.add(file_path, key)
        self.file_database.store(saved_path, info, True)

    def download(self, file_hash):
        """Warms up the cache for the given hash"""
        return self.warm_up(file_hash)

    def warm_up(self, file_hash):
        """Warms up the cache for the given hash

        This method makes room for the given file,
        and then fetches it from one of the cloud hosts.

        """
        record = self.file_database.fetch(file_hash)
        if record.is_cached:
            return True

        self.make_room_for(record.size)

        # I do not like the fact that plowshare gets to determine the final URL.
        ret = self.plowshare.download(record.payload, self.storage.storage_path)

        self.file_database.restored_to_cache(record.hash)

    def usage_ratio(self):
        """Returns the percentage of used space."""
        return 1.0 * self.storage.used() / self.storage.size()

    def exists(self, file_hash):
        """Checks if a given file is in this cloud system."""
        return self.file_database.fetch(file_hash) != None

    def on_cache(self, file_hash):
        """Checks if a given file is on cache."""
        record = self.file_database.fetch(file_hash)

        return record != None and record.is_cached == True

    def make_room_for(self, needed):
        """Makes room in the storage space.

        This method deletes files from the storage space
        until the given number of bytes fits into it.

        """
        if not self.storage.fits(needed):
            return False

        used_space = self.storage.used()
        while not self.storage.fits(used_space + needed):
            to_be_removed = self.file_database.closest_cache_in_size(needed)

            self.storage.remove(to_be_removed.name)
            self.file_database.removed_from_cache(to_be_removed.hash)
            used_space -= to_be_removed.size

