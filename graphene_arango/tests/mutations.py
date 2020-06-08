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
        output = "All your mutate are override"
        return CreatePersonOverriden(output=output)
