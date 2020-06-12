import graphene
from flask import Flask
from flask_graphql import GraphQLView
from graphene_arango.tests import types, mutations, settings
from graphene_arango.fields import ArangoListField


class Query(graphene.ObjectType):
    test_people = ArangoListField(types.Person)
    test_people_obj = ArangoListField(types.Person,
                                      resolve_to_object_type=True)


class Mutation(graphene.ObjectType):
    create_person = mutations.CreatePerson.Field()
    create_person_overriden = mutations.CreatePersonOverriden.Field()
    create_person_overriden2 = mutations.CreatePersonOverriden2.Field()


def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=False)
    app.config.from_pyfile('../tests/settings.py')
    if test_config:
        app.config.from_mapping(test_config)

    schema = graphene.Schema(
        query=Query,
        mutation=Mutation,
    )

    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql',
            schema=schema,
            graphiql=True,
        )
    )

    return app


app = create_app()
