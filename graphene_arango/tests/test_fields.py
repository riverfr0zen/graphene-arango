import pytest
import graphene
import json
from graphene.test import Client
from .queries import introspect_queries
from .types import Person
from ..fields import ArangoListField
from graphene_arango import logger


@pytest.fixture
def data(test_db):
    Person._meta.collection.truncate()
    people = Person._meta.collection.insert_many(
        [{'name': 'bozo', 'age': 50},
         {'name': 'pennywise', 'age': 200},
         {'name': 'joker', 'age': 45},
         {'name': "l'orange", 'age': 73}, ],
        return_new=True
    )
    yield people
    Person._meta.collection.truncate()


@pytest.fixture
def schema(test_db):
    class Query(graphene.ObjectType):
        test_people = ArangoListField(Person)
        test_people_obj = ArangoListField(Person, resolve_to_object_type=True)

    schema = graphene.Schema(
        query=Query,
    )
    yield schema


def test_arango_list_field_all_resolve_method_args(schema, cleanup):
    client = Client(schema)
    result = client.execute(introspect_queries)
    # logger.debug(json.dumps(result, indent=4, sort_keys=True))
    query_fields = result['data']['__schema']['queryType']['fields']
    query_field = [field for field in query_fields
                   if field['name'] == 'testPeople'][0]
    assert len(query_field['args']) == 2
    assert query_field['args'][0]['name'] == 'skip'
    assert query_field['args'][1]['name'] == 'limit'


def test_arango_list_field_all_resolve_method_as_list(schema, data, cleanup):
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
    # logger.debug(result)
    assert len(result['data']['testPeople']) == 4

    client = Client(schema)
    result = client.execute('''
        {
            testPeople(skip: 2) {
                id
                name
                age
            }
        }
    ''')
    # logger.debug(result)
    assert len(result['data']['testPeople']) == 2
    assert result['data']['testPeople'][0]['name'] == 'joker'
    assert result['data']['testPeople'][1]['name'] == "l'orange"

    client = Client(schema)
    result = client.execute('''
        {
            testPeople(limit: 3) {
                id
                name
                age
            }
        }
    ''')
    # logger.debug(result)
    assert len(result['data']['testPeople']) == 3
    assert result['data']['testPeople'][0]['name'] == 'bozo'
    assert result['data']['testPeople'][1]['name'] == "pennywise"
    assert result['data']['testPeople'][2]['name'] == "joker"

    client = Client(schema)
    result = client.execute('''
        {
            testPeople(skip: 1, limit: 2) {
                id
                name
                age
            }
        }
    ''')
    # logger.debug(result)
    assert len(result['data']['testPeople']) == 2
    assert result['data']['testPeople'][0]['name'] == "pennywise"
    assert result['data']['testPeople'][1]['name'] == "joker"


def test_arango_list_field_all_resolve_method_as_obj(schema, data, cleanup):
    client = Client(schema)
    result = client.execute('''
        {
            testPeopleObj {
                docs {
                    id
                    name
                    age
                }
                total
            }
        }
    ''')
    # logger.debug(result)
    assert len(result['data']['testPeopleObj']['docs']) == 4
    assert result['data']['testPeopleObj']['docs'][0]['name'] == 'bozo'
    assert result['data']['testPeopleObj']['docs'][1]['name'] == "pennywise"
    assert result['data']['testPeopleObj']['docs'][2]['age'] == 45
    assert result['data']['testPeopleObj']['docs'][3]['age'] == 73
    assert result['data']['testPeopleObj']['total'] == 4

    client = Client(schema)
    result = client.execute('''
        {
            testPeopleObj(skip: 1, limit: 2) {
                docs {
                    id
                    name
                    age
                }
                total
            }
        }
    ''')
    # logger.debug(result)
    assert len(result['data']['testPeopleObj']['docs']) == 2
    assert result['data']['testPeopleObj']['docs'][0]['name'] == 'pennywise'
    assert result['data']['testPeopleObj']['docs'][1]['name'] == "joker"
    assert result['data']['testPeopleObj']['total'] == 4
