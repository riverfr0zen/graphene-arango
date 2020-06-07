import graphene
from graphene.types.objecttype import ObjectType, ObjectTypeOptions
# from davinciman_appserver import logger


class GrapheneArangoException(Exception):
    pass


class ArangoCollectionTypeOptions(ObjectTypeOptions):
    db = None
    collection_name = None


class ArangoCollectionType(ObjectType):
    id = graphene.ID()

    @classmethod
    def __init_subclass_with_meta__(cls, db=None, collection_name=None,
                                    _meta=None, **options):
        if _meta:
            if not isinstance(_meta, ArangoCollectionTypeOptions):
                raise GrapheneArangoException(
                    '_meta must be an instance of ArangoCollectionTypeOptions '
                    f'but received {_meta.__class__}'
                )
        else:
            _meta = ArangoCollectionTypeOptions(cls)

        _meta.db = db
        _meta.collection_name = collection_name

        if _meta.db.has_collection(collection_name):
            _meta.collection = _meta.db.collection(collection_name)
        else:
            _meta.collection = _meta.db.create_collection(collection_name)

        super(ArangoCollectionType, cls).__init_subclass_with_meta__(
            _meta=_meta, **options
        )
