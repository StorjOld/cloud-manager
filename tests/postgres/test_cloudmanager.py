import cloudmanager
from settings import TEST_DB_PATH
import os

def test_cloudmanager():

    with cloudmanager.CloudManager(TEST_DB_PATH, "storage", 20 * (2**20)) as cm:
        assert cm.usage_ratio()

        upload1 = cm.upload("files/README.md")
        assert upload1
        upload2 = cm.upload("files/test.mp3")
        assert upload2

        result = cm.download("invalidhash")
        assert not result

        assert cm.exists(upload1)
        assert cm.on_cache(upload1)
        assert cm.usage_ratio()

        assert cm.warm_up(upload1)
        assert cm.warm_up(upload2)

        cm.cloud_sync()

        data = cm.data_dump(128000)
        lkb = cm.last_known_block()
        assert lkb == 0
        genesis_block = cm.visit_block(lkb)
        assert not genesis_block

        assert cm.exists(upload2)
        uploadinfo = cm.info(upload2)
        assert uploadinfo['filesize'] == os.stat('files/test.mp3').st_size

        load_success = cm.data_load(data, upload2)
        assert load_success

        assert cm.total_incoming() == 0
        assert cm.total_outgoing() == 0
        assert cm.current_incoming() == 0
        assert cm.current_outgoing() == 0
