import graphene
from ..mutations import ArangoCreateMutation
from .types import Person


class CreatePerson(ArangoCreateMutation):
    class Meta:
        type_class = Person


class CreatePersonOverriden(ArangoCreateMutation):
    class Meta:
        type_class = Person

    output = graphene.String()

    def mutate(root, info, **kwargs):
        output = "All your mutate are override"
        return CreatePerson(output=output)
