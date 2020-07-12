import pytest
import graphene
import json
from graphene.test import Client
from graphene.types import InputObjectType
from .types import Person, Outfit
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


def test_get_input_type_class():
    doc_class = CreatePerson._get_input_type_class(Person)
    assert issubclass(doc_class, InputObjectType)
    assert doc_class.__name__ == 'CreatePersonDoc'
    assert 'id' in doc_class._meta.fields
    assert doc_class._meta.fields['id'].type == graphene.ID
    assert 'key' in doc_class._meta.fields
    assert doc_class._meta.fields['key'].type == graphene.String
    assert 'is_clown' in doc_class._meta.fields
    assert doc_class._meta.fields['is_clown'].type == graphene.Boolean
    assert 'name' in doc_class._meta.fields
    assert doc_class._meta.fields['name'].type == graphene.String
    assert 'age' in doc_class._meta.fields
    assert doc_class._meta.fields['age'].type == graphene.Int
    assert 'aliases' in doc_class._meta.fields
    assert doc_class._meta.fields['aliases'].type.__class__ == graphene.types.structures.List
    assert doc_class._meta.fields['aliases'].type.of_type == graphene.String
    # @TODO figure out how to test this
    assert 'outfit' in doc_class._meta.fields


def test_arango_insert_mutation_field(schema, cleanup):
    client = Client(schema)
    result = client.execute(introspect_mutations)
    # print(json.dumps(result, indent=4, sort_keys=True))
    mut_fields = result['data']['__schema']['mutationType']['fields']
    mut_def = [field for field in mut_fields
               if field['name'] == 'createPerson'][0]
    assert len(mut_def['args']) == 2
    assert mut_def['args'][0]['name'] == 'doc'
    assert mut_def['args'][0]['type']['kind'] == 'INPUT_OBJECT'
    assert mut_def['args'][0]['type']['name'] == 'CreatePersonDoc'
    assert mut_def['args'][1]['name'] == 'overwrite'


def test_arango_insert_mutation(schema, cleanup):
    client = Client(schema)
    result = client.execute('''
        mutation {
            createPerson(doc: {name: "bozo", age: 42}) {
                metadata {
                    id
                    rev
                    key
                },
                new {
                    id
                    key
                    name
                    age
                }
            }
        }
    ''')
    logger.debug(result)
    assert result['data']['createPerson']['metadata']['id']
    assert result['data']['createPerson']['metadata']['key']
    assert result['data']['createPerson']['metadata']['rev']
    assert 'people/' in result['data']['createPerson']['new']['id']
    assert result['data']['createPerson']['new']['name'] == 'bozo'
    assert result['data']['createPerson']['new']['age'] == 42


def test_arango_insert_mutation_passing_id_or_key(schema, cleanup):
    client = Client(schema)

    result = client.execute('''
        mutation {
            createPerson(doc: {id: "people/joker" name: "joker", age: 45}) {
                metadata {
                    id
                    rev
                    key
                }
            }
        }
    ''')
    assert result['data']['createPerson']['metadata']['id'] == 'people/joker'
    assert result['data']['createPerson']['metadata']['key'] == 'joker'
    assert result['data']['createPerson']['metadata']['rev']

    result = client.execute('''
        mutation {
            createPerson(doc: {key: "pennywise",
                               name: "pennywise",
                               age: 200})
            {
                metadata {
                    id
                    rev
                    key
                }
            }
        }
    ''')
    metadata = result['data']['createPerson']['metadata']
    assert metadata['id'] == 'people/pennywise'
    assert metadata['key'] == 'pennywise'
    assert metadata['rev']


def test_arango_insert_mutation_overwrite(schema, cleanup):
    client = Client(schema)

    result = client.execute('''
        mutation {
            createPerson(doc: {id: "people/sam" name: "sam", age: 45}) {
                metadata {
                    id
                    rev
                    key
                }
            }
        }
    ''')

    result = client.execute('''
        mutation {
            createPerson(doc: {id: "people/sam" name: "sam", age: 45}) {
                metadata {
                    id
                    rev
                    key
                }
            }
        }
    ''')
    assert 'errors' in result
    assert 'unique constraint violated' in result['errors'][0]['message']

    result = client.execute('''
        mutation {
            createPerson(
                doc: {id: "people/sam" name: "samuel", age: 20},
                overwrite: true
            ) {
                new {
                    id
                    key
                    name
                    age
                }
                old {
                    id
                    key
                    name
                    age
                }
            }
        }
    ''')
    logger.debug(result)
    new = result['data']['createPerson']['new']
    assert new['id'] == 'people/sam'
    assert new['name'] == 'samuel'
    assert new['age'] == 20

    old = result['data']['createPerson']['old']
    assert old['id'] == 'people/sam'
    assert old['name'] == 'sam'
    assert old['age'] == 45


def test_arango_insert_mutation_overriding(schema, cleanup):
    client = Client(schema)
    result = client.execute('''
        mutation {
            createPersonOverriden(doc: {name: "bozo", age: 42}) {
                output
            }
        }
    ''')
    output = result['data']['createPersonOverriden']['output']
    logger.debug(output)
    assert 'All your mutates are' in output

    result = client.execute('''
        mutation {
            createPersonOverriden2(doc: {name: "bozo", age: 42}) {
                myNewField
            }
        }
    ''')
    logger.debug(result)
    my_new_field = result['data']['createPersonOverriden2']['myNewField']
    assert 'Override by bozo' in my_new_field
