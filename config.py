import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(DATA_DIR, 'site.db').replace('\\', '/')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SITE_OWNER_NAME = 'mxluo'
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret')
    OWNER_PASSWORD = os.environ.get('OWNER_PASSWORD', 'owner123')

