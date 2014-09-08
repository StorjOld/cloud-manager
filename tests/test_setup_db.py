import os
from cloudmanager.setup_db import setup_db

def test_setup_db():
	try:
		setup_db('test.db')
		assert 1 == 1
	except Exception as e:
		raise e
	finally:
		os.remove('test.db')
	
