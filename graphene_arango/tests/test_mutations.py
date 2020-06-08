import pytest
import graphene
import json
from graphene.test import Client
from .mutations import CreatePerson, CreatePersonOverriden, \
                       CreatePersonOverriden2
from .queries import introspect_mutations
from graphene_arango import logger


@pytest.fixture
def schema(test_db):
    class Mutation(graphene.ObjectType):
        create_person = CreatePerson.Field()
        create_person_overriden = CreatePersonOverriden.Field()
        create_person_overriden2 = CreatePersonOverriden2.Field()

    schema = graphene.Schema(
        mutation=Mutation,
    )
    yield schema


def test_arango_create_mutation_field(schema, cleanup):
    client = Client(schema)
    result = client.execute(introspect_mutations)
    # print(json.dumps(result, indent=4, sort_keys=True))
    mut_fields = result['data']['__schema']['mutationType']['fields']
    mut_def = [field for field in mut_fields
               if field['name'] == 'createPerson'][0]
    assert len(mut_def['args']) == 2
    assert mut_def['args'][0]['name'] == 'age'
    assert mut_def['args'][1]['name'] == 'name'


def test_arango_create_mutation(schema, cleanup):
    client = Client(schema)
    result = client.execute('''
        mutation {
            createPerson(name: "bozo", age: 42) {
                metadata {
                    id
                    rev
                    key
                },
                new {
                    id
                    name
                    age
                }
            }
        }
    ''')
    assert result['data']['createPerson']['metadata']['id']
    assert result['data']['createPerson']['metadata']['key']
    assert result['data']['createPerson']['metadata']['rev']
    assert 'people/' in result['data']['createPerson']['new']['id']
    assert result['data']['createPerson']['new']['name'] == 'bozo'
    assert result['data']['createPerson']['new']['age'] == 42


def test_arango_create_mutation_overriding(schema, cleanup):
    client = Client(schema)
    result = client.execute('''
        mutation {
            createPersonOverriden(name: "bozo", age: 42) {
                output
            }
        }
    ''')
    output = result['data']['createPersonOverriden']['output']
    logger.debug(output)
    assert 'All your mutates are' in output

    result = client.execute('''
        mutation {
            createPersonOverriden2(name: "bozo", age: 42) {
                myNewField
            }
        }
    ''')
    logger.debug(result)
    my_new_field = result['data']['createPersonOverriden2']['myNewField']
    assert 'Override by bozo' in my_new_field
