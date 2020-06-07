import pytest
import graphene
import json
from graphene.test import Client
from .types import Person
from ..fields import ArangoListField


@pytest.fixture
def schema(test_db):
    class Query(graphene.ObjectType):
        test_people = ArangoListField(Person)

    schema = graphene.Schema(
        query=Query,
    )
    yield schema


def test_arango_list_field(schema, cleanup):
    Person._meta.collection.insert(
        {'name': 'bozo', 'age': 50},
        {'name': 'pennywise', 'age': 200},
        {'name': 'joker', 'age': 45},
    )

    client = Client(schema)
    # result = client.execute('''
    #     {
    #         testPeople {
    #             metadata {
    #                 id
    #                 rev
    #                 key
    #             },
    #             new {
    #                 id
    #                 name
    #                 age
    #             }
    #         }
    #     }
    # ''')

    pass
