from flask import Flask
from configuration import Configuration
from flask_migrate import Migrate, init, migrate, upgrade
from models import database, User, Role, UserRole, User
from sqlalchemy_utils import database_exists, create_database

application = Flask(__name__)
application.config.from_object(Configuration)

migrateObject = Migrate(application, database)

if not database_exists(application.config["SQLALCHEMY_DATABASE_URI"]):
    create_database(application.config["SQLALCHEMY_DATABASE_URI"])

database.init_app(application)

with application.app_context() as context:
    init()
    migrate(message="Production migration")
    upgrade()

    adminRole = Role(name="admin")
    userRole = Role(name="customer")
    warehouseRole = Role(name="warehouse")

    database.session.add(adminRole)
    database.session.add(userRole)
    database.session.add(warehouseRole)
    database.session.commit()

    admin = User(
        email="admin@admin.com",
        password="1",
        forename="admin",
        surname="admin",
    )

    database.session.add(admin)
    database.session.commit()

    adminRole = UserRole(
        userId=admin.id,
        roleId=adminRole.id
    )

    database.session.add(adminRole)
    database.session.commit()
