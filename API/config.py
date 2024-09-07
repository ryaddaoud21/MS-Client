import os

class Config:
    # Database URI from environment variable or default value
    #SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'mysql+pymysql://root@localhost/client_db')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'mysql+pymysql://root@mysql-db/client_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
