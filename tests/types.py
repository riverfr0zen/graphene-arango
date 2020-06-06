import graphene
from ..types import ArangoCollectionType
from .conftest import _test_db


db = _test_db()


class TestPerson(ArangoCollectionType):
    class Meta:
        db = db
        collection_name = 'test_people'

    name = graphene.String()
    age = graphene.Int()
