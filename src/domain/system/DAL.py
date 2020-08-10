import os
import threading
from datetime import timedelta, datetime, date

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import object_session
from sqlalchemy.pool import SingletonThreadPool
from sqlalchemy.engine import Engine


from src.domain.system.control_observer import DBStatus, DalStatus
from src.protocol_classes.classes_utils import TypedDict, TypedList

# an Engine, which the Session will use for connection
# resources

db_name = os.environ.get('DB_PATH', 'db')
project_directory = os.getcwd()
db_path = f'{project_directory}/{db_name}.db'
if os.environ.get('chosen_db', 'sqlite') == 'sqlite':
    engine_path = 'sqlite:///' + db_path
else:
    engine_path = 'postgresql+psycopg2://postgres:16941694@127.0.0.1/sadna'
# engine_path = 'sqlite:///' + db_path if db_name == "db" else 'sqlite://'
some_engine = create_engine(engine_path, poolclass=SingletonThreadPool)

@event.listens_for(some_engine, 'connect')
def receive_connect(dbapi_connection, connection_record):
    print('Connected listener')
    DAL.get_instance().send_server(DBStatus.DBUp)

# # Ref: https://www.bookstack.cn/read/sqlalchemy-1.3/ad4d5a232910993a.md
# @event.listens_for(Engine, 'close')
# def receive_close(dbapi_connection, connection_record):
#     print('Close listener')
#     DAL.get_instance().send_server(DBStatus.DBDown)

# @event.listens_for(Engine, 'invalidate')
# def receive_invalidate(dbapi_connection, connection_record, exception):
#     print('Invalidate listener')
#     DAL.get_instance().send_server(DBStatus.DBDown)
#
# @event.listens_for(Engine, 'reset')
# def receive_reset(dbapi_connection, connection_record):
#     print('Reset listener')
#     DAL.get_instance().send_server(DBStatus.DBDown)
#
#
# @event.listens_for(Engine, 'soft_invalidate')
# def receive_soft_invalidate(dbapi_connection, connection_record, exception):
#     print('Soft invalidate listener')
#     DAL.get_instance().send_server(DBStatus.DBDown)


# create a configured "Session" class
Session = sessionmaker(bind=some_engine)


class DAL:
    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if DAL.__instance is None:
            DAL()
        return DAL.__instance

    def __init__(self):
        self._db_session = None
        self._dal_subject: DalStatus = None
        # Insert here all the models files.
        self._dal_lock = threading.Semaphore()
        DAL.__instance = self

    def update_session(self, db):
        """
        initializing first session and cofiguration
        :param db: SQLAlchemy object for database queries and configurations
        :return: NONE
        """
        db.session.expire_on_commit = False
        self._db = db
        self._db_session = Session()

    def renew_session(self):
        """
        creating a new session for the current use case
        :return: None
        """
        self._dal_lock.acquire()
        self._db_session = Session()

    def drop_session(self):
        """
        closing the given session and release it for further use
        :return:
        """
        self._db_session.commit()
        self._db_session.expire_all()
        self._db_session.close()
        self._dal_lock.release()

    def merge(self, o):
        """
        merging the given object to the current session
        :param o: db.Model Object to merge
        :return: None
        """
        self._db_session.merge(o)

    def insert_some_fun(self):
        """FOR TESTING PURPOSES"""
        from src.domain.system.discounts import ProductDiscountStrategy, DiscountConditionCombo, CategoryToNeededPrice, \
            ProductToNeededPrice, ProductToQuantity, CategoryToNeededItems, _IDiscount
        s1 = ProductDiscountStrategy(0.3, "phone")
        d1 = DiscountConditionCombo(
            datetime.now() + timedelta(days=0, hours=3, minutes=45),
            0,
            [CategoryToNeededPrice("cat1", 3.7), CategoryToNeededPrice("cat2", 6.2)],
            [ProductToNeededPrice("bake", 1.3), ProductToNeededPrice("wow", 3.6)],
            [ProductToQuantity("water", 2), ProductToQuantity("bred", 1)],
            [CategoryToNeededItems("cat1", 7), CategoryToNeededItems("cat2", 2)])
        try:
            self._db_session.add_all([s1, d1])
            self._db_session.commit()

            self._db_session.add_all([
                _IDiscount(d1, s1)
            ])
            self._db_session.commit()
        except:
            pass



    def get_all_stats(self):
        from src.communication.notification_handler import DailyStat
        stats = self.query(DailyStat).all()
        return TypedDict(date, DailyStat, {
            stat._date:  stat

        for stat in stats})

    def get_discount_map_with_id_keys(self, ids):
        """
        get all the discounts that matched the given keys
        :param ids: list of id's of discounts objects
        :return: dictionary of {discount id -> discount}
        """
        from src.domain.system.discounts import _IDiscount
        discounts = self.query(_IDiscount).filter(_IDiscount.id.in_(ids)).all()
        return TypedDict(int, _IDiscount, {dis.id: dis for dis in discounts})

    def get_policy_map_with_id_keys(self, ids):
        """
        get all the policies that matched the given keys
        :param ids: list of id's of policies objects
        :return: dictionary of {policy id -> policy}
        """
        from src.domain.system.shopping_policies import IShoppingPolicies
        policies = self.query(IShoppingPolicies).filter(IShoppingPolicies.id.in_(ids)).all()
        return TypedDict(int, IShoppingPolicies, {pol.id: pol for pol in policies})

    def get_all_products_of_basket(self, basket_id):
        """
        get all products that belongs to a given basket
        :param basket_id: id of the wanted basket
        :return: list of products that belong to the basket
        """
        from src.domain.system.cart_purchase_classes import ProductInShoppingCart
        products = self.query(ProductInShoppingCart).filter_by(_basket_id=basket_id).all()
        return products

    def get_num_of_registered_users(self):
        """
        :return: number of registered users in the system
        """
        from src.domain.system.users_classes import LoggedInUser
        num_of_users = self.query(LoggedInUser).count()
        return num_of_users

    def get_all_registered_users(self):
        """
        :return: list of all logged in users
        """
        from src.domain.system.users_classes import LoggedInUser
        all_registered_users = self.query(LoggedInUser).all()
        return all_registered_users

    def get_user_by_name(self, name):
        """
        get registered user from the data based that connected to that name. if not found return None
        :param name: name of wanted user
        :return: LoggedInUser if found, None otherwise
        """
        from src.domain.system.users_classes import LoggedInUser
        users = self.query(LoggedInUser).filter_by(_user_name=name).all()
        if len(users) == 0:
            return None
        else:
            return users[0]

    def get_store_by_name(self, store_name: str):
        """
        get store by given name if possible
        :param store_name: name of the wanted store
        :return: Store if found, None otherwise
        """
        from src.domain.system.store_classes import Store
        res = Store.query.filter_by(_name=store_name).all()
        if len(res) == 0:
            return None
        else:
            return res[0]

    def get_store_that_contains_name(self, store_name: str):
        """
        get all stores that contain the given name
        :param store_name: string to search for in stores
        :return: list of Stores that contain the name. None if no matching stores found
        """
        from src.domain.system.store_classes import Store
        stores = self._db_session.query(Store).filter(Store._name.contains(store_name)).all()
        if len(stores) == 0:
            return None
        else:
            return stores

    def update_quantity_of_item(self, product_in_inventoy_id, store_name, new_quantity):
        """
        update quantity of an item in database
        :param product_in_inventoy_id: id of product
        :param store_name: name of the store th product belong to
        :param new_quantity: qunatity to update
        :return: None
        """
        from src.domain.system.products_classes import ProductInInventory
        self.query(ProductInInventory).filter_by(id=product_in_inventoy_id, _store_fk=store_name).update(
            {ProductInInventory._quantity: new_quantity})

    def get_all_stores_according_to_list(self, stores: TypedList):
        """
        returns all stores that are in the list from the database
        :param stores: list of store name
        :return: list of stores
        """
        output = []
        if len(stores) > 0:
            for store in stores:
                cur_stores = self.get_store_that_contains_name(store)
                if cur_stores is not None:
                    output = output + cur_stores
        else:
            output = self.get_store_that_contains_name("")
        return output

    def get_permission_by_user_fk_store_fk(self, user_name, store):
        """
        get all permissions of a user in a given store
        :param user_name: wanted user name
        :param store: wanted store name
        :return: Permission object to connect between the user and the store if possible, else None
        """
        from src.domain.system.permission_classes import Permission
        return self.query(Permission).filter(Permission._user_fk == user_name,
                                             Permission._store_fk == store).one_or_none()

    def get_permission_with_id_keys(self, id_list, store):
        """
        get all permission of users in a given store in the system
        :param id_list: list of usernames
        :param store: given store
        :return: dictionary of {username -> Permisssion object} that represent all the permissions in a given store
        """
        from src.domain.system.permission_classes import Permission
        permission_output = self.query(Permission).filter(Permission._user_fk.in_(id_list),
                                                          Permission._store_fk == store).all()
        return {perm._user_fk: perm for perm in permission_output}

    def update_store_permissions_ls(self, store_name, new_json_ls):
        from src.domain.system.store_classes import Store
        self.query(Store).filter_by(_name=store_name).update(
            {Store._permissions_ls: new_json_ls})

    def get_permission_with_id_keys_for_store(self, id_list, store):
        from src.domain.system.permission_classes import Permission
        permission_output = self.query(Permission).filter(Permission._user_fk.in_(id_list),
                                                          Permission._store_fk == store).all()
        return {perm._user_fk: perm for perm in permission_output}

    def get_permission_with_id_keys_for_user(self, id_list, username):
        from src.domain.system.permission_classes import Permission
        permission_output = self.query(Permission).filter(Permission._store_fk.in_(id_list),
                                                          Permission._user_fk == username).all()
        return {perm._store_fk: perm for perm in permission_output}

    def is_admin(self, username):
        from src.domain.system.users_classes import LoggedInUser
        user: LoggedInUser = self.query(LoggedInUser).filter(LoggedInUser._user_name == username).one_or_none()
        if user:
            # return "" in user._permissions_list
            return user._admin_counter > 0
        return False

    # def get_permission_with_id_keys(self, store_fk, appointed_by_fk, role):
    #     from src.domain.system.permission_classes import Permission
    #     permission_output = self.query(Permission).filter(Permission._store_fk == store_fk,
    #                                                       Permission._appointed_by_fk == appointed_by_fk,
    #                                                       Permission._role == role).all()
    #     return {perm._user_fk: perm for perm in permission_output}

    def get_purchases_with_id_keys_for_store(self, id_list):
        from src.domain.system.cart_purchase_classes import Purchase
        permission_output = self.query(Purchase).filter(Purchase._purchase_id.in_(id_list)).all()
        return permission_output

    def get_baskets_by_user(self, user):
        from src.domain.system.cart_purchase_classes import Basket
        output = self.query(Basket).filter(Basket._user == user, Basket._is_used == True).all()
        return {b._store_name: b for b in output}

    def get_purchases_of_user(self, user_name):
        from src.domain.system.cart_purchase_classes import Purchase
        permission_output = self.query(Purchase).filter(Purchase._user_name == user_name).all()
        return permission_output

    def get_all_purchases(self):
        from src.domain.system.cart_purchase_classes import Purchase
        permission_output = self.query(Purchase).all()
        return permission_output

    def add_new_store(self, store, permission):

        # self._db_session.add(self._db_session.merge(store))
        # self._db_session.add(self._db_session.merge(permission))

        self._db_session.add(store)

        self._db_session.add(permission)
        self.commit()

    def get_product_in_inventory(self, product_in_inventory_id: int):
        from src.domain.system.cart_purchase_classes import ProductInInventory
        return self._db_session.query(ProductInInventory).filter(
            ProductInInventory.id == product_in_inventory_id).one_or_none()

    def get_product_in_cart(self, product_in_inventory_id: int, basket_id: int):
        from src.domain.system.cart_purchase_classes import ProductInShoppingCart
        product = self._db_session.query(ProductInShoppingCart).filter(
            ProductInShoppingCart._product_in_inventory_id == product_in_inventory_id,
            ProductInShoppingCart._basket_id == basket_id).all()
        return product[0]

    def get_all_pending_message(self):
        from src.communication.notification_handler import PendingMessage
        all_messages = self._db_session.query(PendingMessage).all()
        return all_messages

    def delete(self, o, del_only=False):
        self._db_session.delete(o)
        if not del_only:
            self.commit()

    def delete_permissions_as_query(self, ids):
        from src.domain.system.permission_classes import Permission
        for pid in ids:
            # self.query(Permission).filter_by(id=pid).delete()
            self.query(Permission).filter_by(_user_fk=pid[0], _store_fk=pid[1]).delete()

    def clear_pending_messages_for_user(self, user_name: str):
        from src.communication.notification_handler import PendingMessage
        self.query(PendingMessage).filter_by(_username=user_name).delete()

    def update_permission_of_acting_member_after_deletion(self, pid, is_owner, new_appointed_by):
        from src.domain.system.permission_classes import Permission
        if is_owner:
            self.query(Permission).filter_by(_user_fk=pid[0], _store_fk=pid[1]).update(
                {Permission._owners_appointed_ls: new_appointed_by})
        else:
            self.query(Permission).filter_by(_user_fk=pid[0], _store_fk=pid[1]).update(
                {Permission._managers_appointed_ls: new_appointed_by})

    def delete_all(self, l, del_only=False):
        for o in l:
            self._db_session.delete(o)
        if not del_only:
            self.commit()

    def delete_all_products(self, in_inventory_ids, products_ids):
        from src.domain.system.products_classes import ProductInInventory, Product
        for pid in in_inventory_ids:
            self.query(ProductInInventory).filter_by(id=pid).delete()
        for pid in in_inventory_ids:
            self.query(Product).filter_by(id=pid).delete()

    def copy_store(self, dest, source):
        # dest._name = source._name
        dest._initial_owner_fk = source._initial_owner_fk
        dest._initial_owner = source._initial_owner
        dest._opened = source._opened
        dest._creation_date = source._creation_date
        dest._inventory_ls = source._inventory_ls
        dest._permissions_ls = source._permissions_ls
        dest._pending_ownership_proposes_ls = source._pending_ownership_proposes_ls
        dest._discount_fk = source._discount_fk
        dest._discount = source._discount
        dest._shopping_policies_fk = source._shopping_policies_fk
        dest._shopping_policies = source._shopping_policies

    def copy_perm(self, dest, source):
        # dest.id = source.id
        # dest._role = source._role
        # dest._store_fk = source._store_fk
        # dest._user_fk = source._user_fk
        # dest._appointed_by_fk = source._appointed_by_fk
        # dest._store = source._store
        # dest._user = source._user
        # dest._appointed_by = source._appointed_by
        # dest._can_manage_inventory = source._can_manage_inventory
        # dest._appoint_new_store_owner = source._appoint_new_store_owner
        # dest._appoint_new_store_manager = source._appoint_new_store_manager
        # dest._watch_purchase_history = source._watch_purchase_history
        # dest._open_and_close_store = source._open_and_close_store
        # dest._can_manage_discount = source._can_manage_discount
        dest._managers_appointed_ls = source._managers_appointed_ls
        dest._owners_appointed_ls = source._owners_appointed_ls

    def add(self, o, add_only=False):
        temp_session = object_session(o)
        if self._db_session != temp_session and temp_session is not None:
            temp_session.close()
            self._db_session.merge(o)
        res = None
        try:
            self._db_session.add(o)
        except Exception as e:
            res = self._db_session.merge(o)
            from src.domain.system.store_classes import Store
            from src.domain.system.permission_classes import Permission
            # if isinstance(o, Store):
            #     # self.copy_store(o, res)
            #     o.__dict__.update(res.__dict__)
            # elif isinstance(o, Permission):
            #     o.__dict__.update(res.__dict__)
            #     self.copy_perm(o, res)
            # else:
            #     o.__dict__.update(res.__dict__)

        if not add_only:
            self.commit()
        return res

    def add_all(self, l, add_only=False):
        for o in l:
            self._db_session.add(o)
        if not add_only:
            self.commit()

    def commit(self):
        self._db_session.commit()

    def rollback(self):
        self._db_session.rollback()

    def query(self, x):
        return self._db_session.query(x)

    def begin_nested(self):
        self._db_session.begin_nested()

    def flush(self):
        self._db_session.flush()

    def set_subject(self, dalSubject):
        self._dal_subject = dalSubject

    def send_server(self, msg: DBStatus):
        if self._dal_subject:
            self._dal_subject.notify(msg)
