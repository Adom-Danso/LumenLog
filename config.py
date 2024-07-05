import secrets

class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = secrets.token_hex(20)
    SESSION_COOKIE_SECURE = True
    
class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SESSION_PROTECTION = "strong"
    LANGUAGES = ['en', 'es', 'de', 'fr']
    IMAGE_FOLDER = 'lumenlog/static/img'

class TestingConfig(Config):
    TESTING = True
    DB_NAME = "test_database"

    
    
