from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']  # 모든 호스트 적용

INTERNAL_IPS = [
    '127.0.0.1',
]

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]
