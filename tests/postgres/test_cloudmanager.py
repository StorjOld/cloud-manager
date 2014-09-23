import cloudmanager
from settings import TEST_DB_PATH
import os
import glob
import time


file1 = "files/README.md"
file2 = "files/test.mp3"
file3 = "files/test.md"


def remove_storage_files(regex='storage/*'):
    r = glob.glob(regex)
    for i in r:
        os.remove(i)


def test_cloudmanager():
    remove_storage_files()

    with cloudmanager.CloudManager(TEST_DB_PATH, "storage", 31) as cm:

        assert cm.data_dump(128000) is None
        
        load_success = cm.data_load(None, '0000')
        assert load_success is None

        warm_up = cm.warm_up('0000')
        assert warm_up is None

        result = cm.download("invalidhash")
        assert not result

        #assert cm.usage_ratio()
        upload1 = cm.upload(file1)
        assert upload1
        #call upload again for coverage
        upload1 = cm.upload(file1)
        assert upload1
        assert cm.warm_up(upload1)
        assert cm.exists(upload1)
        assert cm.on_cache(upload1)

        cm.cloud_sync()

        data = cm.data_dump(128000)
        lkb = cm.last_known_block()
        assert lkb == 0
        genesis_block = cm.visit_block(lkb)
        assert not genesis_block

        uploadinfo = cm.info(upload1)
        assert uploadinfo['filesize'] == os.stat(file1).st_size
        load_success = cm.data_load(data, upload1)
        assert load_success

        
        upload2 = cm.upload(file2)
        assert upload2
        assert cm.warm_up(upload2)

        assert cm.usage_ratio()
        assert cm.total_incoming() == 0
        assert cm.total_outgoing() == 0
        assert cm.current_incoming() == 0
        assert cm.current_outgoing() == 0

        assert cm.upload_queue_info()
        assert cm.blockchain_queue_info()
        assert cm.used_space()
        assert cm.capacity()

        assert cm.sync_status()
        
        record = cm.file_database.fetch(upload1)
        assert 'uploads' in cm.dict_description(record)

        #test download of file if not in storage
        remove_storage_files()
        assert cm.warm_up(upload1)

        #Test if we run out of disk space
        old = cm.make_room_for
        def make_room_for_stub(needed):
            return False
        cm.make_room_for = make_room_for_stub
        assert cm.upload(file3) is False
        remove_storage_files()
        cm.make_room_for = old

        #Test if file is missing for warm_up
        upload3 = cm.upload(file3)
        remove_storage_files()
        assert cm.warm_up(upload3) is False

        cm.close()
