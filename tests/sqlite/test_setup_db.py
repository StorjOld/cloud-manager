import os
import cloudmanager
from cloudmanager.database import connect

def test_setup_db_sqllite3():
    setup_db = cloudmanager.setup_db.setup_db
    assert setup_db('test.db')
    os.remove('test.db')

def test_sqllite3_connection():
	db = connect('test.db')
	assert db
	db.close()
	