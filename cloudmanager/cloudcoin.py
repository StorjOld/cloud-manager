import json
import base64

class CloudCoin(object):
    """CloudCoin coordinates interactions between a blockchain and a local database."""

    def __init__(self, coin, cloud):
        self.coin  = coin
        self.cloud = cloud

    def scan_database(self):
        """Scan database for non published data."""
        while True:
            payload = self.cloud.data_dump(self.coin.MaxPayloadSize)
            if payload is None:
                return

            self.process_database(payload)

    def scan_blockchain(self):
        """Scan blockchain for non registered data."""
        for block in self.coin.blocks():
            for txid, data in dw.transactions(block):
                try:
                    info = json.loads(data)
                    info["version"] ## checking if the key exists
                except:
                    continue

                self.process_blockchain(txid, info)

    def process_blockchain(self, txid, info):
        """Load payload into local database."""
        self.cloud.data_load(info, txid)

    def process_database(self, payload):
        """Publish payload into blockchain."""
        self.coin.send_data(payload)
