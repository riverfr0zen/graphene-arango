import graphene
from ..types import ArangoCollectionType
from .conftest import _test_db


db = _test_db()


class Outfit(graphene.ObjectType):
    head = graphene.String()
    torso = graphene.String()
    legs = graphene.String()
    feet = graphene.String()


class Person(ArangoCollectionType):
    class Meta:
        db = db
        collection_name = 'people'

    is_clown = graphene.Boolean()
    name = graphene.String()
    age = graphene.Int()
    aliases = graphene.List(graphene.String)
    outfit = graphene.Field(Outfit)
