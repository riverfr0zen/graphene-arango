import inspect
import graphene
from graphene.types.mutation import MutationOptions
from graphene.types import InputObjectType
from graphene.utils.props import props
from functools import partial


class ArangoInsertMetadata(graphene.ObjectType):
    id = graphene.String()
    key = graphene.String()
    rev = graphene.String()


class ArangoMutationOptions(MutationOptions):
    type_class = None


class ArangoCreateMutation(graphene.Mutation):
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
        setattr(cls, "output", graphene.String())
        setattr(cls, "metadata", graphene.Field(ArangoInsertMetadata))
        setattr(cls, "new", graphene.Field(type_class))

        # generic mutation method
        def mutate(root, info, **kwargs):
            metadata, new = cls.do_mutation(root, info, **kwargs)
            return cls(metadata=metadata, new=new)

        resolver = None
        if not getattr(cls, 'mutate', None):
            resolver = mutate

        super().__init_subclass_with_meta__(
            _meta=_meta,
            arguments=arguments,
            resolver=resolver,
            **options
        )

    @classmethod
    def do_mutation(cls, root, info, **kwargs):
        collection = cls._meta.type_class._meta.collection
        metadata = collection.insert(kwargs, return_new=True)
        metadata['id'] = metadata.pop('_id')
        metadata['key'] = metadata.pop('_key')
        metadata['rev'] = metadata.pop('_rev')
        new = metadata.pop('new')
        new['id'] = new.pop('_id')
        new.pop('_key')
        new.pop('_rev')
        # print(metadata)
        # print(new)
        return metadata, new
