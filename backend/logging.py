from logging.handlers import RotatingFileHandler





# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'standard': {
#             'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
#         },
#     },
#     'handlers': {
#          'file': {
#             'level': 'INFO',
#             'class': 'logging.FileHandler',
#             'filename': 'log1.log',
#         },
#     },
#     'loggers': {
#         logger_name: {
#             'level': 'WARNING',
#             'propagate': True,
#         } for logger_name in ('django', 'django.request', 'django.db.backends', 'django.template', 'thenewboston')
#     },
#     'root': {
#         'level': 'DEBUG',
#         'handlers': ['file', 'console'],
#     }
# }