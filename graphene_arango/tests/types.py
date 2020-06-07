import graphene
from ..types import ArangoCollectionType
from .conftest import _test_db


db = _test_db()


class Person(ArangoCollectionType):
    class Meta:
        db = db
        collection_name = 'people'

    name = graphene.String()
    age = graphene.Int()
