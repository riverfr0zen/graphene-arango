import pytest
import logging
from .settings import CLIENT_CONF, DB_CONF
from arango import ArangoClient


#
# Logging
#
LOG_LEVELS = {
    'graphene-arango': logging.DEBUG,
    'requests': logging.WARN,
    'urllib3': logging.WARN,
}
logging.basicConfig(level=LOG_LEVELS['graphene-arango'])
for litem in LOG_LEVELS.keys():
    logging.getLogger(litem).setLevel(LOG_LEVELS[litem])


def _test_db():
    cli = ArangoClient(**CLIENT_CONF)
    return cli.db(**DB_CONF)


@pytest.fixture(scope="session")
def test_db():
    # cli = ArangoClient(**CLIENT_CONF)
    yield _test_db()


@pytest.fixture(scope="session")
def cleanup(test_db):
    yield
    assert test_db.delete_collection('people')
