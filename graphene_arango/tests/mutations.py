import graphene
from ..mutations import ArangoInsertMutation
from .types import Person


class CreatePerson(ArangoInsertMutation):
    class Meta:
        type_class = Person


class CreatePersonOverriden(ArangoInsertMutation):
    class Meta:
        type_class = Person

    output = graphene.String()

    def mutate(root, info, **kwargs):
        output = "All your mutates are override by us"
        return CreatePersonOverriden(output=output)


def some_resolver_func(root, info, **kwargs):
    """ For testing CreatePersonOverriden2 below """
    out = f"Override by {kwargs['name']}"
    return CreatePersonOverriden2(my_new_field=out)


class CreatePersonOverriden2(ArangoInsertMutation):
    class Meta:
        type_class = Person
        resolver = some_resolver_func

    @classmethod
    def set_mutation_fields(cls, type_class):
        setattr(cls, "my_new_field", graphene.String())
