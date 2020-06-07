import logging

# #
# # Logging
# #
# LOG_LEVELS = {
#     'graphene-arango': logging.DEBUG,
#     'requests': logging.WARN,
#     'urllib3': logging.WARN,
# }


# logging.basicConfig(level=LOG_LEVELS['graphene-arango'])
logger = logging.getLogger(__name__)
# for litem in LOG_LEVELS.keys():
#     logging.getLogger(litem).setLevel(LOG_LEVELS[litem])
