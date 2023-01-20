from datetime import timedelta
# import os

# databaseUrl = os.environ["DATABASE_URL"]


class Configuration:
    # SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/authentication"
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@localhost:3306/store"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    REDIS_HOST = "localhost"
    REDIS_PRODUCT_LIST = "products"
