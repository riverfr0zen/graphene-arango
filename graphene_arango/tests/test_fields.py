import pytest
import graphene
import json
from graphene.test import Client
from .queries import introspect_queries
from .types import Person
from ..fields import ArangoListField
from graphene_arango import logger


@pytest.fixture
def schema(test_db):
    class Query(graphene.ObjectType):
        test_people = ArangoListField(Person)

    schema = graphene.Schema(
        query=Query,
    )
    yield schema


def test_arango_list_field_all_resolve_method_args(schema, cleanup):
    client = Client(schema)
    result = client.execute(introspect_queries)
    logger.debug(json.dumps(result, indent=4, sort_keys=True))
    # mut_fields = result['data']['__schema']['mutationType']['fields']
    # mut_def = [field for field in mut_fields
    #            if field['name'] == 'createPerson'][0]
    # assert len(mut_def['args']) == 2
    # assert mut_def['args'][0]['name'] == 'age'
    # assert mut_def['args'][1]['name'] == 'name'


def test_arango_list_field_all_resolve_method(schema, cleanup):
    inserted = Person._meta.collection.insert_many(
        [{'name': 'bozo', 'age': 50},
         {'name': 'pennywise', 'age': 200},
         {'name': 'joker', 'age': 45}, ],
        return_new=True
    )
    # logger.debug(inserted)

    client = Client(schema)
    result = client.execute('''
        {
            testPeople {
                id
                name
                age
            }
        }
    ''')
    logger.debug(result)
    assert len(result['data']['testPeople']) == 3
    # logger.debug(result)
