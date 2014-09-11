import os
from cloudmanager.setup_db import setup_db

def test_setup_db_sqllite3():
    try:
        assert setup_db('test.db')
    except Exception as e:
        raise e
    finally:
        os.remove('test.db')
