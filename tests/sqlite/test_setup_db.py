import os
import cloudmanager

def test_setup_db_sqllite3():
    setup_db = cloudmanager.setup_db.setup_db
    assert setup_db('test.db')
    os.remove('test.db')
