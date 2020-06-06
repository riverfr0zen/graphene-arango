import pytest
from ..types import \
    ArangoCollectionType, \
    GrapheneArangoException
from arango.database import StandardDatabase
from arango.collection import StandardCollection


@pytest.fixture
def cleanup(test_db):
    yield
    assert test_db.delete_collection('test_people')


def test_arango_collection_type_init(test_db, cleanup):
    # Testing for collection that does not exist yet
    class TestPersonType(ArangoCollectionType):
        class Meta:
            db = test_db
            collection_name = 'test_people'

    assert isinstance(TestPersonType._meta.db, StandardDatabase)
    db = TestPersonType._meta.db
    test_people = db.collection('test_people')
    assert isinstance(test_people, StandardCollection)

    # Testing for collection that already exists
    class TestPersonType2(ArangoCollectionType):
        class Meta:
            db = test_db
            collection_name = 'test_people'

    assert isinstance(TestPersonType2._meta.db, StandardDatabase)
    db = TestPersonType2._meta.db
    test_people = db.collection('test_people')
    assert isinstance(test_people, StandardCollection)


def test_passing_invalid_meta_in_subclasses(test_db):
    class TypeSubclassWithBadOpts(ArangoCollectionType):
        class Meta:
            abstract = True

        @classmethod
        def __init_subclass_with_meta__(cls, **kwargs):
            _meta = ["hi"]
            super(TypeSubclassWithBadOpts,
                  cls).__init_subclass_with_meta__(_meta=_meta, **kwargs)

    with pytest.raises(GrapheneArangoException) as einfo:
        class FaultyType(TypeSubclassWithBadOpts):
            class Meta:
                db = test_db
                collection_name = 'faulty_items'
    assert ('must be an instance of '
            'ArangoCollectionTypeOptions') in str(einfo.value)
