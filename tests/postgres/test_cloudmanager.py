import cloudmanager
from settings import TEST_DB_PATH

def test_cloudmanager():

    with cloudmanager.CloudManager(TEST_DB_PATH, "storage", 20 * (2**20)) as cm:
        assert cm.usage_ratio()

        upload1 = cm.upload("files/README.md")
        assert upload1
        upload2 = cm.upload("files/test.mp3")
        assert upload2

        assert cm.exists(upload1)
        assert cm.on_cache(upload1)
        assert cm.usage_ratio()

        assert cm.warm_up(upload1)
        assert cm.warm_up(upload2)

        data = cm.data_dump(128000)
        #print data
        #print cm.data_load(data, "blockchain-hash")
