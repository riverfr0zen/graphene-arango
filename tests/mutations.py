import graphene
from ..mutations import ArangoCreateMutation
from .types import TestPerson


class CreateTestPerson(ArangoCreateMutation):
    class Meta:
        type_class = TestPerson


# class CreateTestPersonOverriden(ArangoCreateMutation):
#     class Meta:
#         type_class = TestPerson

#     output = graphene.String()

#     def mutate(root, info, **kwargs):
#         output = "All your base is overriden"
#         return CreateTestPerson(output=output)
