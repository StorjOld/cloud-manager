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

    def upload(self, file_path):
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

    def warm_up(self, file_hash):
        record = self.file_database.fetch(file_hash)
        if record.is_cached:
            return True

        self.make_room_for(record.size)

        # I do not like the fact that plowshare gets to determine the final URL.
        ret = self.plowshare.download(record.payload, self.storage.storage_path)

        self.file_database.restored_to_cache(record.hash)

    def usage_ratio(self):
        return 1.0 * self.storage.used() / self.storage.size()

    def exists(self, file_hash):
        return self.file_database.fetch(file_hash) != None

    def on_cache(self, file_hash):
        record = self.file_database.fetch(file_hash)

        return record != None and record.is_cached == True

    def make_room_for(self, needed):
        if not self.storage.fits(needed):
            return False

        used_space = self.storage.used()
        while not self.storage.fits(used_space + needed):
            print "Removing something"
            to_be_removed = self.file_database.closest_cache_in_size(needed)

            print "picked", to_be_removed.name
            self.storage.remove(to_be_removed.name)
            self.file_database.removed_from_cache(to_be_removed.hash)
            used_space -= to_be_removed.size

