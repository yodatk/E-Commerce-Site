# Database settings
# https://github.com/sqlalchemy/sqlalchemy/issues/4858
import json
import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db: SQLAlchemy = SQLAlchemy(session_options={"expire_on_commit": False, "autoflush": False})


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if os.environ.get('chosen_db', 'sqlite') == 'sqlite':
        cursor = dbapi_connection.cursor()
        # '''
        # By default SQLite do not enforce foreign keys.
        # So: https://stackoverflow.com/questions/2614984/sqlite-sqlalchemy-how-to-enforce-foreign-keys
        # '''
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def receive_after_create():
    "listen for the 'after_create' event"

    with open('initialise_config.json') as json_file:
        data = json.load(json_file)

    _insert_users_and_admins(data)
    _insert_stores_and_initial_owners_permissions(data)
    _insert_products(data)
    db.session.commit()


def _insert_users_and_admins(data):
    from src.domain.system.users_classes import User, LoggedInUser
    from src.domain.system.permission_classes import Permission, Role
    for user in data["users"]:
        new_user: User = User.create_new_user_for_guest()
        new_user.user_state = LoggedInUser(user["_user_name"], user["_password"], user["_email"])
        if user["_is_admin"] == 1:
            perm: Permission = Permission.define_permissions_for_init(Role.system_manager,
                                                                      new_user.user_state.user_name, None, None)
            new_user.user_state.add_permission(perm)
            db.session.add(perm)
        db.session.add(new_user)


def _insert_stores_and_initial_owners_permissions(data):
    from src.domain.system.store_classes import Store
    from src.domain.system.permission_classes import Permission, Role
    for store in data["stores"]:
        new_store = Store(store["_name"], store["_initial_owner"])
        perm_initial_owner = Permission.define_permissions_for_init(Role.store_initial_owner, store["_initial_owner"],
                                                                    store["_name"])
        db.session.add(perm_initial_owner)
        db.session.add(new_store)


def _insert_products(data):
    from src.domain.system.products_classes import ProductInInventory, Product
    for p in data["products_in_inventory"]:
        product: Product = Product(p["_name"], p["_brand"], p['_categories'], p['_description'])
        product_in_inventory: ProductInInventory = ProductInInventory(product, p["_price"], p["_quantity"],
                                                                      p["_store_fk"])
        db.session.add(product)
        db.session.add(product_in_inventory)
