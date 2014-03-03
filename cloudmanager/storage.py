import os
import helpers
import shutil

class Storage(object):
    """Handles local cache storage.

    """
    def __init__(self, storage_path, storage_size):
        self.storage_path = storage_path
        self.storage_size = storage_size

    def fits(self, file_bytes):
        """Check if there is enough room for the given bytes.

        This method checks if there is enough room in the
        local cache storage to accomodate for the given number
        of bytes.

        """
        return file_bytes <= 0.9 * self.storage_size

    def add(self, file_path, file_hash):
        """Add a file to local storage.

        Copies the given file to local storage, and renames it
        so that the final name includes a hash, to avoid collisions.

        """
        filename = file_hash[:7] + "_" + os.path.basename(file_path)
        shutil.copyfile(
            file_path,
            self.path(filename))

        return filename

    def remove(self, filename):
        """Remove a file from local storage."""
        os.remove(self.path(filename))

    def used(self):
        """Return number of bytes used."""
        return helpers.directory_size(self.storage_path)

    def size(self):
        """Return the local storage capacity, in bytes."""
        return self.storage_size

    def path(self, filename):
        """Return the full path of a file that is to be stored in local cache."""
        return self.storage_path + "/" + filename
