import os
import hashlib

def directory_size(start_path):
    """Return the total size of a given directory."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def sha256(path):
    """Return the sha256 digest of a file."""
    h = hashlib.sha256()
    with open(path) as f:
        for chunk in iter(lambda: f.read(8192), b''):
            if not chunk: break
            h.update(chunk.encode('utf-8'))
    return h.hexdigest()
