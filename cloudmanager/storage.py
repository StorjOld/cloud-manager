import os
import helpers
import shutil

class Storage(object):
    def __init__(self, storage_path, storage_size):
        self.storage_path = storage_path
        self.storage_size = storage_size

    def fits(self, file_bytes):
        return file_bytes <= 0.9 * self.storage_size

    def add(self, file_path, file_hash):
        filename = file_hash[:7] + "_" + os.path.basename(file_path)
        shutil.copyfile(
            file_path,
            self.storage_path + "/" + filename)
        return filename

    def remove(self, filename):
        os.remove(self.storage_path + "/" + filename)

    def used(self):
      return helpers.directory_size(self.storage_path)

    def size(self):
      return self.storage_size
