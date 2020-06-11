import graphene
from collections import OrderedDict
from graphene.types.argument import to_arguments
from functools import partial
from graphene.types import Field, List
from graphene_arango import logger


class ArangoListField(Field):
    def __init__(self, _type, resolve_with="all", *args, **kwargs):
        self.resolve_with = resolve_with
        self._base_args = None
        super().__init__(List(_type), *args, **kwargs)

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
    def all_resolver(arango_coll_type, resolver,
                     root, info, **kwargs):
        logger.debug(kwargs)
        return arango_coll_type._meta.collection.all(**kwargs)

    def get_resolver(self, parent_resolver):
        if self.resolve_with == 'all':
            return partial(self.all_resolver,
                           self.type.of_type,
                           parent_resolver)
