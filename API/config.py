class Config:
    # Configuration de la base de données MySQL
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@mysql-db/client_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
