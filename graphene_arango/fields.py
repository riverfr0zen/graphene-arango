from functools import partial
from graphene.types import Field, List, NonNull


class ArangoListField(Field):
    def __init__(self, _type, *args, **kwargs):
        super().__init__(List(_type), *args, **kwargs)

    @staticmethod
    def list_resolver(arango_coll_type, resolver,
                      root, info, **kwargs):
        return arango_coll_type._meta.collection.find({})

    def get_resolver(self, parent_resolver):
        return partial(self.list_resolver, self.type.of_type, parent_resolver)
