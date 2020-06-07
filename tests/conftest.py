import pytest
from .settings import CLIENT_CONF, DB_CONF
from arango import ArangoClient


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
    assert test_db.delete_collection('test_people')
