import inspect
import graphene
from graphene.types.mutation import MutationOptions
from graphene.types import InputObjectType
from graphene.utils.props import props
from functools import partial
from graphene_arango import logger


class ArangoInsertMetadata(graphene.ObjectType):
    id = graphene.String()
    key = graphene.String()
    rev = graphene.String()


class ArangoMutationOptions(MutationOptions):
    type_class = None


class ArangoInsertMutation(graphene.Mutation):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, type_class, **options):
        _meta = ArangoMutationOptions(cls)
        _meta.type_class = type_class

        # composing arguments here
        type_class_attrs = inspect.getmembers(
            type_class,
            lambda a: not(inspect.isroutine(a))
        )
        arguments = {attr: maybe_type.__class__()
                     for attr, maybe_type in type_class_attrs
                     if isinstance(maybe_type, graphene.types.base.BaseType)}
        arguments.pop('id')

        # composing mutation fields here
        cls.set_mutation_fields(type_class)

        # assign resolver
        # @TODO test that resolver can be passed through options, or done
        # inline by declaring a mutate method, and that it otherwise finally
        # resorts to default_resolver
        resolver = options.pop('resolver', None)
        if not resolver and not getattr(cls, 'mutate', None):
            resolver = cls.default_resolver

        super().__init_subclass_with_meta__(
            _meta=_meta,
            arguments=arguments,
            resolver=resolver,
            **options
        )

    @classmethod
    def set_mutation_fields(cls, type_class):
        setattr(cls, "metadata", graphene.Field(ArangoInsertMetadata))
        setattr(cls, "new", graphene.Field(type_class))

    @classmethod
    def default_resolver(cls, root, info, **kwargs):
        collection = cls._meta.type_class._meta.collection
        metadata = collection.insert(kwargs, return_new=True)
        # logger.debug(metadata)
        metadata['id'] = metadata.pop('_id')
        metadata['key'] = metadata.pop('_key')
        metadata['rev'] = metadata.pop('_rev')
        new = metadata.pop('new')
        # logger.debug(new)
        return cls(metadata=metadata, new=new)
