import time
import json

class Payload(object):
    def __init__(self):
        self.hash     = ""
        self.size     = ""
        self.datetime = ""
        self.uploads  = []


def build(hash, size, uploads):
    """Build a payload for a new upload."""
    p = Payload()

    p.hash     = hash
    p.size     = size
    p.datetime = str(int(time.time()))
    p.uploads  = uploads

    return p


def to_dict(payload):
    """Serialize a payload into a json compatible object."""
    return {
        "version":  "0.1",
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
    p = Payload()

    if data["version"] != "0.1":
        return None
    
    p.size     = data["filesize"]
    p.hash     = data["filehash"]
    p.datetime = data["datetime"]
    p.uploads  = data["uploads"]

    return p
