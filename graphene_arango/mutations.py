import inspect
import graphene
from graphene.types.mutation import MutationOptions
from graphene.types import InputObjectType
from graphene.utils.props import props
from functools import partial
from graphene_arango import logger
from .utils.info import get_fields


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
    def _get_attr_field(cls, maybe_type):
        if isinstance(maybe_type, graphene.types.field.Field):
            return cls._get_input_type_class(
                    maybe_type.type,
                    name_suffix=str(maybe_type.type)
            )()
        if isinstance(maybe_type, graphene.types.base.BaseType):
            return maybe_type.__class__()
        if isinstance(maybe_type, graphene.types.structures.Structure):
            return maybe_type.__class__(maybe_type.of_type)

    @classmethod
    def _get_input_type_class(cls, type_class, name_suffix=''):
        type_class_attrs = inspect.getmembers(
            type_class,
            lambda a: not(inspect.isroutine(a))
        )
        fields = {
            attr: cls._get_attr_field(maybe_type)
            for attr, maybe_type in type_class_attrs
            if (
                isinstance(maybe_type, graphene.types.field.Field) or
                isinstance(maybe_type, graphene.types.base.BaseType) or
                isinstance(maybe_type, graphene.types.structures.Structure)
            )
        }
        return type(f"{cls.__name__}{name_suffix}Doc",
                    (InputObjectType,),
                    fields)

    @classmethod
    def compose_arguments(cls, type_class):
        return {
            "doc": graphene.Argument(cls._get_input_type_class(type_class)),
            "overwrite": graphene.Boolean()
        }

    @classmethod
    def __init_subclass_with_meta__(cls, type_class, **options):
        _meta = ArangoMutationOptions(cls)
        _meta.type_class = type_class

        # compose arguments
        arguments = options.pop('arguments', None)
        if not arguments:
            arguments = cls.compose_arguments(type_class)

        # composing mutation fields here
        cls.set_mutation_fields(type_class)

        # assign resolver
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
        setattr(cls, "old", graphene.Field(type_class))

    @classmethod
    def default_resolver(cls, root, info, **kwargs):
        doc = kwargs.pop('doc')
        if 'id' in doc:
            doc['_id'] = doc.pop('id')
        if 'key' in doc:
            doc['_key'] = doc.pop('key')

        overwrite = kwargs.pop('overwrite', False)

        return_new = False
        return_old = False
        requested_fields = get_fields(info)
        if 'new' in requested_fields.keys():
            return_new = True
        if 'old' in requested_fields.keys():
            return_old = True
        # logger.debug(requested_fields)

        collection = cls._meta.type_class._meta.collection
        metadata = collection.insert(doc,
                                     sync=True,
                                     overwrite=overwrite,
                                     return_new=return_new,
                                     return_old=return_old)
        # logger.debug(metadata)
        metadata['id'] = metadata.pop('_id')
        metadata['key'] = metadata.pop('_key')
        metadata['rev'] = metadata.pop('_rev')
        new = metadata.pop('new', None)
        old = metadata.pop('old', None)
        # logger.debug(new)
        return cls(metadata=metadata, new=new, old=old)
