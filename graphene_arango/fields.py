import graphene
from collections import OrderedDict
from graphene.types.argument import to_arguments
from functools import partial
from graphene.types import Field, List, NonNull
from graphene_arango import logger
from .types import ArangoCollectionType


class ArangoListField(Field):
    def __init__(self, _type, resolve_with="all", resolve_to_object_type=False,
                 *args, **kwargs):
        self.resolve_with = resolve_with
        self.resolve_to_object_type = resolve_to_object_type
        self._base_args = None
        super().__init__(_type, *args, **kwargs)

    @property
    def type(self):
        _type = super().type
        if self.resolve_to_object_type:
            return type(f"{_type._meta.name}ListResults",
                        (graphene.ObjectType, NonNull),
                        {"docs": graphene.List(_type),
                         "total": graphene.Int()})
        else:
            return List(_type)

    @property
    def args(self):
        return to_arguments(self._base_args or OrderedDict(),
                            self._all_resolver_args())

    @args.setter
    def args(self, args):
        self._base_args = args

    @staticmethod
    def _all_resolver_args():
        return {
            "skip": graphene.Int(description="Number of documents to skip."),
            "limit": graphene.Int(description="Max number of documents returned."),
        }

    @staticmethod
    def all_resolver(arango_coll_type, to_object_type, resolver,
                     root, info, **kwargs):
        if to_object_type:
            return {
                "docs": arango_coll_type._meta.collection.all(**kwargs),
                "total": arango_coll_type._meta.collection.count()
            }
        return arango_coll_type._meta.collection.all(**kwargs)

    def get_resolver(self, parent_resolver):
        if self.resolve_with == 'all':
            return partial(self.all_resolver,
                           super().type,
                           self.resolve_to_object_type,
                           parent_resolver)
