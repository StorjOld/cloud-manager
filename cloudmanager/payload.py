import time
import json

class Payload(object):
    def __init__(self):
        self.name     = ""
        self.hash     = ""
        self.size     = ""
        self.datetime = ""
        self.uploads  = []


def build(name, hash, size, uploads):
    """Build a payload for a new upload."""
    p = Payload()

    p.name     = name
    p.hash     = hash
    p.size     = size
    p.datetime = str(int(time.time()))
    p.uploads  = uploads

    return p


def to_dict(payload):
    """Serialize a payload into a json compatible object."""
    return {
        "version":  "0.2",
        "filename": payload.name,
        "filesize": payload.size,
        "filehash": payload.hash,
        "datetime": payload.datetime,
        "uploads":  payload.uploads }


def from_blockchain_payload(data):
    """Load an array of payloads."""
    try:
        data = json.loads(data)
        payloads = [from_dict(p) for p in data]
        if any(x is None for x in payloads):
            return None

        return payloads
    except:
        return None

def serialize(payload):
    """Convert a payload into a json string."""
    return json.dumps(to_dict(payload))


def from_dict(data):
    """Deserialize a payload from a json compatible object."""

    if data["version"] == "0.2":
        p = Payload()
        p.name     = data["filename"]
        p.size     = data["filesize"]
        p.hash     = data["filehash"]
        p.datetime = data["datetime"]
        p.uploads  = data["uploads"]
        return p

    if data["version"] == "0.1":
        p = Payload()
        p.name     = data["filehash"][0:10]
        p.size     = data["filesize"]
        p.hash     = data["filehash"]
        p.datetime = data["datetime"]
        p.uploads  = data["uploads"]
        return p

    return None
