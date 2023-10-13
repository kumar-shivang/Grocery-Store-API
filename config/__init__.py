import os
from datetime import timedelta

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config(object):
    # database config
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(parent_dir, 'database.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # jwt config
    JWT_SECRET_KEY = 'super-secret'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    JWT_TOKEN_LOCATION = ['cookies', 'headers']
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_CSRF_PROTECT = True
    # mail config
    MAIL_SERVER = '0.0.0.0'
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False

