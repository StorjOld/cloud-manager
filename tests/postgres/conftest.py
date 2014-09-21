# -*- coding: utf-8 -*-
from six.moves.urllib.parse import urlparse, urlunparse
import pytest

from cloudmanager.setup_db import setup_db

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from settings import TEST_DB_PATH
#from utils.migrate import run_migrations

test_uri = list(urlparse(TEST_DB_PATH))

DB_NAME = test_uri[2].replace('/', '')
# Connection URI used for creating the test database
# Strip the database name from the URI since the DB doesn't exist yet
test_uri[2] = ''
PG_URI = urlunparse(test_uri)

DB_CONN = None       # Connection for creating the test database
DB_TEST_CONN = None  # Connection to the test database used by tests

def pytest_configure(config):
    """Create test database and initialize connection"""
    global DB_CONN, DB_TEST_CONN
    try:
        DB_CONN = psycopg2.connect(PG_URI)
        DB_CONN.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = DB_CONN.cursor()
        try:
            cur.execute('CREATE DATABASE %s;' % DB_NAME)
        except:
            cur.execute('DROP DATABASE %s;' % DB_NAME)
            cur.execute('CREATE DATABASE %s;' % DB_NAME)
        cur.close()

        setup_db(TEST_DB_PATH)
        DB_TEST_CONN = psycopg2.connect(TEST_DB_PATH)

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        pytest_unconfigure(config)
        raise e

def pytest_unconfigure(config):
    """Drop test database"""
    if DB_TEST_CONN:
        DB_TEST_CONN.close()

    cur = DB_CONN.cursor()
    cur.execute('DROP DATABASE %s;' % DB_NAME)
    cur.close()
    DB_CONN.close()

def pytest_runtest_setup(item):
    """Run the DB migrations required for this test

    This looks for a module-level `DB_MIGRATIONS` list, which should contain
    names of yoyo migrations (without the extension) located in migrations/.
    """
    migrations = getattr(item.module, 'DB_MIGRATIONS', [])
    if migrations:
        run_migrations(DB_TEST_CONN, migrations)

def pytest_runtest_teardown(item, nextitem):
    """Clean the database after each test

    We won't drop it, since the connection is still open.
    """
    cur = DB_TEST_CONN.cursor()
    cur.execute('DROP SCHEMA public CASCADE; CREATE SCHEMA public;')
    cur.close()

@pytest.fixture
def db(request):
    """Create a Psycopg cursor instance"""
    cur = DB_TEST_CONN.cursor()
    def close_cur():
        cur.close()
    request.addfinalizer(close_cur)

    return cur

@pytest.fixture
def patch_urandom(monkeypatch):
    monkeypatch.setattr('os.urandom', lambda f: 'f' * f)