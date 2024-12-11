import os

class ProductionConfig():
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # Use just the URI itself, not DATABASE_URL=...
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', "sqlite:////app/db/app.db")  
    print(SQLALCHEMY_DATABASE_URI)

class TestConfig():
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'



