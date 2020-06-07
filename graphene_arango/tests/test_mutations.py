import pytest
import graphene
import json
from graphene.test import Client
from .mutations import CreateTestPerson, CreateTestPersonOverriden
from .queries import introspect_mutations


@pytest.fixture
def schema(test_db):
    class Mutation(graphene.ObjectType):
        create_test_person = CreateTestPerson.Field()
        create_test_person_overriden = CreateTestPersonOverriden.Field()

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
               if field['name'] == 'createTestPerson'][0]
    assert len(mut_def['args']) == 2
    assert mut_def['args'][0]['name'] == 'age'
    assert mut_def['args'][1]['name'] == 'name'


def test_arango_create_mutation(schema, cleanup):
    client = Client(schema)
    result = client.execute('''
        mutation {
            createTestPerson(name: "bozo", age: 42) {
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
    assert result['data']['createTestPerson']['metadata']['id']
    assert result['data']['createTestPerson']['metadata']['key']
    assert result['data']['createTestPerson']['metadata']['rev']
    assert 'test_people/' in result['data']['createTestPerson']['new']['id']
    assert result['data']['createTestPerson']['new']['name'] == 'bozo'
    assert result['data']['createTestPerson']['new']['age'] == 42


def test_arango_create_mutation_overriding(schema, cleanup):
    client = Client(schema)
    result = client.execute('''
        mutation {
            createTestPersonOverriden(name: "bozo", age: 42) {
                output
            }
        }
    ''')
    output = result['data']['createTestPersonOverriden']['output']
    assert 'All your base' in output
