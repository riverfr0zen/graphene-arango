import pytest
import graphene
import json
from graphene.test import Client
from .mutations import CreateTestPerson
from .queries import introspect_mutations


@pytest.fixture(scope='session')
def cleanup(test_db):
    yield
    assert test_db.delete_collection('test_people')


@pytest.fixture
def schema(test_db):
    class Mutation(graphene.ObjectType):
        create_test_person = CreateTestPerson.Field()

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
                output
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
    print(result)
