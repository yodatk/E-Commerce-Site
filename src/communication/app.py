import enum
import sys
import threading

from src.domain.system.control_observer import AppServer, Observer, Subject, DalStatus, DBStatus
from src.communication.notification_handler import SocketEmitter, StatManager, Category, NotificationHandler, Emitter

from src.service.initilizer import Initializer
import eventlet
from flask import Flask, request, send_from_directory, session, redirect
from flask import jsonify
from flask_cors import CORS
from flask_sessionstore import SqlAlchemySessionInterface, Session
from flask_socketio import SocketIO
from time import sleep
from src.external.publisher import Publisher
from src.service.persistency_interface.persistency_interface import PersistencyInterface

eventlet.monkey_patch(socket=True, select=True)

import os

from src.logger.log import Log
from src.protocol_classes.classes_utils import Result
from src.service.shopping_interface.shopping_handler import ShoppingHandler
from src.service.store_inventory_interface.inventory_handler import InventoryHandler
from src.service.system_adminstration.sys_admin_handler import SysAdminHandler
from src.service.user_handler.user_handler import UserHandler



SERVER_AVAILABLE = True

if os.environ.get('chosen_db', 'sqlite') == 'sqlite':
    try:
        os.remove('db.db')
        print("Removed DB")
    except:
        print("Removed db failed")
        SERVER_AVAILABLE = False

# TODO: avielfedida adds aivelfedida1 which adds avielfedida2
# TODO: I fail to click approve within avielfedida1 to add avielfedida2.

counter = 0

root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build")
static = os.path.join(root, 'static')
app = Flask(__name__, static_folder='./build')
db_name = 'db'
project_directory = os.getcwd()
db_path = f'{project_directory}/{db_name}.db'

if os.environ.get('chosen_db', 'sqlite') == 'sqlite':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:16941694@127.0.0.1/sadna_ssbb'#'postgres://ncifouckgoefqv:1bcab406056b1bd13ef9a076f661edda6019129badcb0976cb672260c77fdbec@ec2-46-137-84-140.eu-west-1.compute.amazonaws.com:5432/d689ahn68c0m8i'
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/signals/
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
ses = Session(app)
# To see the queries that are being run
app.config['SQLALCHEMY_ECHO'] = True
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SECRET_KEY'] = 'super secret key'
app.config['REACT_DEV_SERVER'] = 'http://localhost:3000/'  # React dev server
# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.

# todo: WHEN USING BUILD, REMOVE THE ARGUMENT cors_allowed_origins


def update_server_status(dbStatus: DBStatus):
    global SERVER_AVAILABLE
    if dbStatus == DBStatus.DBDown:
        SERVER_AVAILABLE = False
    elif dbStatus == DBStatus.DBUp:
        SERVER_AVAILABLE = True
    else:
        print('Unknown db status')
        SERVER_AVAILABLE = False


appServerObs: Observer = AppServer(update_server_status)
dalSubject: Subject = DalStatus()
dalSubject.attach(appServerObs)


socket_io = SocketIO(app, cors_allowed_origins='*')

emitter: Emitter = SocketEmitter(socket_io)
notification_handler: NotificationHandler = NotificationHandler(emitter)
Publisher.get_instance().set_communication_handler(notification_handler)

persistency_interface = PersistencyInterface()
user_handler = UserHandler(notification_handler)
shopping_handler = ShoppingHandler()
inventory_handler = InventoryHandler()
system_handler = SysAdminHandler()
initializer: Initializer = Initializer(2, "init_thread", user_handler, inventory_handler, shopping_handler,
                                       system_handler, app.app_context(), notification_handler)

# --------------------------------------------------------------------------


'''
To find the correct status to response:
https://httpstatuses.com/
'''


def bootstrap():
    pass
    # dictToSend1 = {
    #     'username': 'root',
    #     'email': 'root@app.com',
    #     'password': 'Parker51!',
    #     'user_id': -1
    # }
    # dictToSend2 = {
    #     'username': 'aviel1',
    #     'email': 'root@app.com',
    #     'password': 'numerator4$ME',
    #     'user_id': -1
    # }
    # dictToSend3 = {
    #     'username': 'aviel2',
    #     'email': 'root@app.com',
    #     'password': 'numerator4$ME',
    #     'user_id': -1
    # }
    # dictToSend4 = {
    #     'username': 'aviel3',
    #     'email': 'root@app.com',
    #     'password': 'numerator4$ME',
    #     'user_id': -1
    # }
    # requests.post('http://localhost:3000/register', json=dictToSend1)
    # requests.post('http://localhost:3000/register', json=dictToSend2)
    # requests.post('http://localhost:3000/register', json=dictToSend3)
    # requests.post('http://localhost:3000/register', json=dictToSend4)


class Status(enum.IntEnum):
    OK = 200
    Created = 201
    Unauthorized = 401
    NotAcceptable = 406
    BadRequest = 400
    Conflict = 409
    NotAvailable = 503


active_locust_flag = False
locust_session = {}


class Sess:

    @staticmethod
    def init_for_locust(random_number):
        if random_number != -1:
            if random_number not in locust_session:
                locust_session[random_number] = {}
            return locust_session[random_number]
        else:
            return session

    @staticmethod
    def is_logged_operation(user_id, random_number=-1):
        with app.app_context():
            sess = Sess.init_for_locust(random_number)
            if user_id == -1:
                user_handler.add_to_guest_counter()

            res: Result = user_handler.get_user_by_id_if_guest_create_one(user_id)
            sess["user_id"] = user_id if user_id != -1 else res.data
            if sess["user_id"] == -1:
                sess['logged'] = False
                sess['username'] = ""
                sess['is_admin'] = False
            elif Sess.getusername() != "":
                sess["is_admin"] = user_handler.is_admin(Sess.getusername()).data
            output = {
                'user_id': Sess.get_user_id(),
                'logged': Sess.is_logged(),
                'username': Sess.getusername(),
                'is_admin': Sess.is_admin()
                # todo_added_for_testing
            }
            return output

    @staticmethod
    def reg(random_number=-1):
        with app.app_context():
            sess = Sess.init_for_locust(random_number)
            sess['user_id'] = -1
            sess['logged'] = False

    @staticmethod
    def logout(random_number=-1):
        with app.app_context():
            sess = Sess.init_for_locust(random_number)
            sess['logged'] = False
            sess['username'] = ""
            sess['is_admin'] = False

    @staticmethod
    def logged(res: Result, username, random_number=-1):
        with app.app_context():
            sess = Sess.init_for_locust(random_number)
            sess['logged'] = True
            sess['username'] = username
            if res.requesting_id != -1:
                sess["user_id"] = res.requesting_id

            # todo - added for testing
            sess['is_admin'] = res.data
            # todo - added for testing

    @staticmethod
    def getusername(random_number=-1) -> str:
        with app.app_context():
            sess = Sess.init_for_locust(random_number)
            return sess.get('username', '')

    @staticmethod
    def get_user_id(random_number=-1) -> int:
        with app.app_context():
            sess = Sess.init_for_locust(random_number)
            return sess.get('user_id', -1)

    @staticmethod
    def is_logged(random_number=-1) -> bool:
        with app.app_context():
            sess = Sess.init_for_locust(random_number)
            return sess.get('logged', False)

    @staticmethod
    def is_admin(random_number=-1) -> bool:
        with app.app_context():
            sess = Sess.init_for_locust(random_number)
            return sess.get('is_admin', False)

    @staticmethod
    def get_all(random_number=-1):
        with app.app_context():
            sess = Sess.init_for_locust(random_number)
            return {
                'user_id': sess.get('user_id', -1),
                'logged': sess.get('logged', False),
                'username': sess.get('username', ""),
                # todo added_for_testing
                'is_admin': sess.get('is_admin', False)
                # todo_added_for_testing
            }


# https://github.com/corydolphin/flask-cors/issues/200
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', app.config['REACT_DEV_SERVER'])  # React dev server.
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


@app.before_request
def before_request_func():
    if not SERVER_AVAILABLE:
        return
    if Sess.is_logged():
        user_id = Sess.get_user_id()
        if user_id != -1:
            res: Result = user_handler.user_state_is_none(user_id)
            if not res.data:
                Sess.logout()

@app.teardown_request
def teardown_request(exception):
    global SERVER_AVAILABLE
    if exception:
        SERVER_AVAILABLE = False

@app.route('/static/<path:filename>', methods=['GET'])
def base_static(filename):
    return send_from_directory(static, filename)

@app.route('/', defaults={'filename': 'index.html'})
@app.route('/<filename>', methods=['GET'])
def main(filename):
    return app.send_static_file(filename)


@app.route('/is_logged', methods=['GET'])
def is_logged():
    # if user_sess['user_id'] == -1:

    state = Status.OK if SERVER_AVAILABLE else Status.NotAvailable
    return jsonify(Sess.is_logged_operation(Sess.get_user_id())), state

    # else:
    #     return jsonify(user_sess), Status.OK


# @app.route('/active_locust', methods=['POST'])
# def active_locust():
#     global active_locust_flag
#     active_locust_flag = True
#     return "hi"


# @app.route('/reset_release', methods=['POST'])
# def reset_release():
#     session_lock.release()
#     return ""


@app.route('/new_store', methods=['POST'])
def new_store():
    data = request.json
    user_id = Sess.get_user_id(data.get('rand_number', -1))
    #
    # # TODO: for locust tests
    # if user_id == -1:
    #     user_id = data['user_id']

    store_name = data['storename']
    res: Result = inventory_handler.opening_a_new_store(user_id, store_name)
    if res.succeed:
        return jsonify({'user_id': res.requesting_id}), Status.Created
    return jsonify({'error': res.msg}), Status.NotAcceptable


@app.route('/close_store', methods=['POST'])
def close_store():
    data = request.json
    user_id = Sess.get_user_id(data.get('rand_number', -1))
    store_name = data['store_name']
    res: Result = inventory_handler.close_store(user_id, store_name)
    if res.succeed:
        return jsonify({'user_id': res.requesting_id}), Status.OK
    return jsonify({'error': res.msg}), Status.NotAcceptable


@app.route('/open_store', methods=['POST'])
def open_store():
    data = request.json
    user_id = data['user_id']
    store_name = data['store_name']
    res: Result = inventory_handler.open_existing_store(user_id, store_name)
    if res.succeed:
        return jsonify({'user_id': res.requesting_id}), Status.OK
    return jsonify({'error': res.msg}), Status.NotAcceptable


@app.route('/fetch_store_personal_view/<store_name>', methods=['GET'])
def fetch_store_personal_view(store_name):
    try:
        un = Sess.getusername()
        # if len(un) == 0:
        #     return jsonify({'error': 'Unlogged user'})
        res: Result = shopping_handler.watch_info_on_store(un, store_name)
        if res.succeed:
            return jsonify(res.data), Status.OK
        else:  # Simple user
            return jsonify({'error': res.msg}), Status.Unauthorized
    except Exception as e:
        return jsonify({'error': 'Invalid request'}), Status.BadRequest


@app.route('/add_store_owner', methods=['POST'])
def add_store_owner():
    data = request.json
    # user_id = data['user_id']  # Adding user_id
    user_id = Sess.get_user_id(data.get('rand_number', -1))
    store_name = data['store_name']
    added_username = data['added_username']
    res: Result = inventory_handler.adding_new_owner_to_store(user_id, added_username, store_name)
    if res.succeed:
        return jsonify(succeded=True), Status.OK
    log: Log = Log.get_instance()
    log.get_logger().info(res.msg)
    return jsonify({'error': res.msg}), Status.NotAcceptable


@app.route('/add_admin', methods=['POST'])
def add_admin():
    data = request.json
    user_id = int(data['user_id'])  # Adding user_id
    added_username = data['added_username']
    res: Result = system_handler.add_admin(user_id, added_username)
    if res.succeed:
        return jsonify(succeded=True), Status.OK
    log: Log = Log.get_instance()
    log.get_logger().info(res.msg)
    return jsonify({'error': res.msg}), Status.NotAcceptable


@app.route('/add_store_manager', methods=['POST'])
def add_store_manager():
    data = request.json

    user_id = Sess.get_user_id(data.get('rand_number', -1))  # Adding user_id
    store_name = data['store_name']
    added_username = data['added_username']
    res: Result = inventory_handler.adding_new_manager_to_store(user_id, added_username, store_name)
    if res.succeed:
        return jsonify(succeded=True), Status.OK
    return jsonify({'error': res.msg}), Status.NotAcceptable


@app.route('/fetch_discounts/<user_id>/<store_name>', methods=['GET'])
def fetch_discounts(user_id, store_name):
    try:
        user_id = int(user_id)
        # un = Sess.getusername()
        # if len(un) == 0:
        #     return jsonify({'error': 'Unlogged user'})
        res: Result = inventory_handler.get_discounts(user_id, store_name)
        if res.succeed:
            return jsonify({'user_id': user_id, 'store_name': store_name, 'data': res.data}), Status.OK
        return jsonify({'error': res.msg})
    except:
        return jsonify({'error': 'user_id should be int'}), Status.BadRequest


@app.route('/fetch_policies/<user_id>/<storename>', methods=['GET'])
def fetch_policies(user_id, storename):
    data = request.json
    try:
        user_id = int(user_id)
        res: Result = inventory_handler.fetch_policies_from_store(user_id, storename)
        if res.succeed:
            return jsonify({'user_id': user_id, 'store_name': storename, 'data': res.data}), Status.OK
        return jsonify({'error': res.msg}), Status.NotAcceptable
    except:
        return jsonify({'error': 'Missing fields'}), Status.BadRequest


@app.route('/delete_owner_from_store', methods=['POST'])
def delete_owner_from_store():
    data = request.json
    user_id = data['user_id']
    store_name = data['store_name']
    removed_username = data['removed_username']
    res: Result
    try:
        res: Result = inventory_handler.removing_store_owner(int(user_id), removed_username, store_name)
        owner_to_remove_id: int = res.data
        # remove_manager from store
        if res.succeed:
            return jsonify({"user_id": res.requesting_id}), Status.OK
        else:
            return jsonify({'error': res.msg}), Status.NotAcceptable
    except Exception as e:
        log: Log = Log.get_instance()
        log.get_logger().error(f"comm uError:{str(e)}")
        return jsonify({'error': str(e)})


@app.route('/delete_manager_from_store', methods=['POST'])
def delete_manager_from_store():
    data = request.json
    user_id = Sess.get_user_id(data.get('rand_number', -1))
    store_name = data['store_name']
    removed_username = data['removed_username']
    res: Result
    try:
        res: Result = inventory_handler.removing_store_manager(int(user_id), removed_username, store_name)
        # remove_manager from store
        if res.succeed:
            return jsonify({"user_id": res.requesting_id}), Status.OK
        else:
            return jsonify({'error': res.msg}), Status.NotAcceptable
    except Exception as e:
        log: Log = Log.get_instance()
        log.get_logger().error(f"comm uError:{str(e)}")
        return jsonify({'error': str(e)})


def split_to_categs(categories):
    categories = categories.strip()
    if len(categories) > 0:
        categories = categories.split(',')
    else:
        categories = []
    return categories


@app.route('/add_product_to_store', methods=['POST'])
def add_product_to_store():
    try:
        data = request.json
        # user_id = data['user_id']
        user_id = Sess.get_user_id(data.get('rand_number', -1))
        store_name = data['storename']
        product_name = data['product_name']
        base_price = data['base_price']
        quantity = data['quantity']
        categories = data['categories']
        categories_list = split_to_categs(categories)
        brand = data['brand']
        description = data['description']
        res: Result = inventory_handler.add_product_to_store(int(user_id), store_name, product_name, float(base_price),
                                                             int(quantity), brand, categories_list, description)
        if res.succeed:
            return jsonify(succeded=True), Status.OK
        return jsonify({'error': res.msg}), Status.NotAcceptable
    except:
        return jsonify({'error': 'user id, new price should be int/float'}), Status.NotAcceptable


@app.route('/edit_product', methods=['POST'])
def edit_product():
    try:
        data = request.json
        user_id = Sess.get_user_id(data.get('rand_number', -1))
        store_name = data['storename']

        product_name = data['product_name']
        brand = data['brand']
        new_price = data['new_price']
        categories = data['categories']
        quantity = data['quantity']
        description = data['description']
        categories_list = None
        if categories != "":
            categories_list = categories.split(',')
        res: Result = inventory_handler.edit_existing_product_in_store(int(user_id), store_name, product_name, brand,
                                                                       float(new_price), int(quantity), categories_list,
                                                                       description)
        if res.succeed:
            return jsonify(succeded=True), Status.OK
        return jsonify({'error': res.msg}), Status.NotAcceptable
    except:
        return jsonify({'error': 'user id, new price should be int/float'}), Status.NotAcceptable


@app.route('/remove_product', methods=['POST'])
def remove_product():
    try:
        data = request.json
        user_id = Sess.get_user_id(data.get('rand_number', -1))
        store_name = data['storename']
        product_name = data['product_name']
        res: Result = inventory_handler.remove_product_to_store(user_id, store_name, product_name)
        if res.succeed:
            return jsonify(succeded=True), Status.OK
        return jsonify({'error': res.msg}), Status.NotAcceptable
    except:
        return jsonify({'error': 'Base price should be int/float'}), Status.NotAcceptable


@app.route('/new_discount', methods=['POST'])
def new_discount():
    data = request.json
    try:
        user_id = Sess.get_user_id(data.get('rand_number', -1))
        product_name = data['product_name'].strip()
        store_name = data['storename'].strip()
        discount_type = data['discount_type'].strip()
        percent = data['percent'].strip()
        category = data['category'].strip()
        free_per_x = data['free_per_x'].strip()
        overall_product_price = data['overall_product_price'].strip()
        overall_category_price = data['overall_category_price'].strip()
        overall_product_quantity = data['overall_product_quantity'].strip()
        overall_category_quantity = data['overall_category_quantity'].strip()
        up_to_date = data['up_to_date'].strip()
        basket_size = data['basket_size'].strip()
        res: Result = inventory_handler.add_discount(user_id, store_name, product_name, discount_type, percent,
                                                     category, free_per_x, overall_product_price,
                                                     overall_category_price, overall_product_quantity,
                                                     overall_category_quantity, up_to_date, basket_size)
        if res.succeed:
            return jsonify({'discount_id': res.data}), Status.OK
        return jsonify({'error': res.msg}), Status.NotAcceptable
    except:
        return jsonify({'error': 'Missing fields'}), Status.BadRequest


@app.route('/fetch_awaiting_approvals/<user_id>/<storename>', methods=['GET'])
def fetch_awaiting_approvals(user_id, storename):
    res: Result
    try:
        res: Result = shopping_handler.fetch_awaiting_approvals(int(user_id), storename)
        if res.succeed:
            return jsonify({'awaiting_approvals': res.data}), Status.OK
    except:
        return jsonify({'error': 'Server ERROR'}), Status.NotAcceptable
    return jsonify({'error': res.msg}), Status.Unauthorized


@app.route('/approve_new_owner', methods=['POST'])
def approve_new_owner():
    try:
        data = request.json
        user_id = Sess.get_user_id(data.get('rand_number', -1))
        store_name = data['storename']
        username = data['username']
        res: Result = shopping_handler.respond_new_owner_to_store(user_id, username, store_name, 1)
        if res.succeed:
            return jsonify(succeded=True), Status.OK
        return jsonify({'error': res.msg}), Status.NotAcceptable
    except:
        return jsonify({'error': 'Missing data'}), Status.BadRequest


@app.route('/deny_new_owner', methods=['POST'])
def deny_new_owner():
    try:
        data = request.json
        user_id = data['user_id']
        store_name = data['storename']
        username = data['username']
        res: Result = shopping_handler.respond_new_owner_to_store(user_id, username, store_name, 2)
        if res.succeed:
            return jsonify(succeded=True), Status.OK
        return jsonify({'error': res.msg}), Status.NotAcceptable
    except:
        return jsonify({'error': 'Missing data'}), Status.BadRequest


@app.route('/remove_discount', methods=['POST'])
def remove_discount():
    try:
        data = request.json
        user_id = int(data['user_id'])
        discount_id = data['discount_id']
        store_name = data['storename']
        res: Result = inventory_handler.remove_discount(user_id, discount_id, store_name)
        if res.succeed:
            return jsonify(succeded=True), Status.OK
        return jsonify({'error': res.msg}), Status.NotAcceptable
    except:
        return jsonify({'error': 'user id should be int/float'}), Status.NotAcceptable


@app.route('/remove_policy', methods=['POST'])
def remove_policy():
    try:
        data = request.json
        user_id = int(data['user_id'])
        policy_id = data['policy_id']
        store_name = data['storename']
        res: Result = inventory_handler.remove_policy(user_id, store_name, policy_id)
        if res.succeed:
            return jsonify(succeded=True), Status.OK
        return jsonify({'error': res.msg}), Status.NotAcceptable
    except:
        return jsonify({'error': 'user id should be int/float'}), Status.NotAcceptable


# End point to fetch list of store owner by user_id
@app.route('/fetch_stores/<user_id>', methods=['GET'])
def fetch_stores(user_id):
    res: Result
    un = Sess.getusername()
    if len(un) == 0:
        return jsonify({'error': 'unlogged user'}), Status.NotAcceptable
    try:
        res: Result = inventory_handler.get_all_stores_of_user(un)
        if res.succeed:
            if len(res.data) == 0:
                return jsonify({'store': []}), Status.OK
            return jsonify(
                {'stores': [{'name': store['name'], 'initial_owner': store['initial_owner'], 'open': store['open'],
                             'creation_date': store['creation_date']} for store in res.data]}), Status.OK
    except:
        return jsonify({'error': 'Server ERROR'}), Status.NotAcceptable
    return jsonify({'error': res.msg}), Status.Unauthorized


@app.route('/fetch_personal_purchases/<user_id>', methods=['GET'])
def fetch_personal_purchases(user_id):
    res: Result
    try:
        res: Result = shopping_handler.watch_user_purchases(int(user_id))
        if res.succeed:
            if len(res.data) == 0:
                return jsonify({'user_id': res.requesting_id, 'purchases': []}), Status.OK
            return jsonify(
                {'user_id': res.requesting_id, 'purchases': res.data}), Status.OK
    except:
        return jsonify({'error': 'Server ERROR'}), Status.NotAcceptable
    return jsonify({'error': res.msg}), Status.Unauthorized


@app.route('/fetch_all_purchases_as_admin/<user_id>', methods=['GET'])
def fetch_all_purchases_as_admin(user_id):
    res: Result
    try:
        res: Result = system_handler.watch_all_purchases(int(user_id))
        if res.succeed:
            if len(res.data) == 0:
                return jsonify({'user_id': res.requesting_id, 'purchases': []}), Status.OK
            return jsonify(
                {'user_id': res.requesting_id, 'purchases': res.data}), Status.OK
    except:
        return jsonify({'error': 'Server ERROR'}), Status.NotAcceptable
    return jsonify({'error': res.msg}), Status.Unauthorized


@app.route('/fetch_store_purchases_as_admin/<user_id>/<store_name>', methods=['GET'])
def fetch_store_purchases_as_admin(user_id, store_name):
    res: Result
    try:
        res: Result = system_handler.watch_store_purchase(int(user_id), store_name)
        if res.succeed:
            if len(res.data) == 0:
                return jsonify({'user_id': res.requesting_id, 'purchases': []}), Status.OK
            return jsonify(
                {'user_id': res.requesting_id, 'purchases': res.data}), Status.OK
    except:
        return jsonify({'error': 'Server ERROR'}), Status.NotAcceptable
    return jsonify({'error': res.msg}), Status.Unauthorized


@app.route('/fetch_user_purchases_as_admin/<user_id>/<user_name>', methods=['GET'])
def fetch_user_purchases_as_admin(user_id, user_name):
    res: Result
    try:
        res: Result = system_handler.watch_user_purchases(int(user_id), user_name)
        if res.succeed:
            if len(res.data) == 0:
                return jsonify({'user_id': res.requesting_id, 'purchases': []}), Status.OK
            return jsonify(
                {'user_id': res.requesting_id, 'purchases': res.data}), Status.OK
    except:
        return jsonify({'error': 'Server ERROR'}), Status.NotAcceptable
    return jsonify({'error': res.msg}), Status.Unauthorized


@app.route('/fetch_store_purchases/<user_id>/<store_name>', methods=['GET'])
def fetch_store_purchases(user_id, store_name):
    res: Result
    try:
        res: Result = inventory_handler.watch_store_purchase(int(user_id), store_name)
        if res.succeed:
            if len(res.data) == 0:
                return jsonify({'user_id': res.requesting_id, 'purchases': []}), Status.OK
            return jsonify(
                {'user_id': res.requesting_id, 'purchases': res.data}), Status.OK
    except:
        return jsonify({'error': 'Server ERROR'}), Status.NotAcceptable
    return jsonify({'error': res.msg}), Status.Unauthorized


@app.route('/fetch_products_of_store', methods=['GET'])
def fetch_products_of_store():
    res: Result
    try:
        user_id: int = request.args.get('user_id')
        store_name: str = request.args.get('storename')
        res: Result = inventory_handler.get_all_products_of_store(int(user_id), store_name)
        if res.succeed:
            if len(res.data) == 0:
                return jsonify({'product': []}), Status.OK
            return jsonify(
                {'products': [{'name': product['product']['name'], 'price': product['price'],
                               'quantity': product['quantity'], 'brand': product['product']['brand'],
                               'categories': product['product']['categories'],
                               'description': product['product']['description']} for product in res.data]}), Status.OK
    except:
        return jsonify({'error': 'Server ERROR'}), Status.NotAcceptable
    return jsonify({'error': res.msg}), Status.Unauthorized


@app.route('/purchase_items', methods=['POST'])
def purchase_items():
    try:
        data = request.json
        user_id = Sess.get_user_id(data.get('rand_number', -1))
        credit_card = data['credit_card']
        country = data['country']
        city = data['city']
        street = data['street']
        house_number = data['house_number']
        apartment = data['apartment']
        if apartment.strip() == "":
            apartment = "0"
        floor = data['floor']
        if floor.strip() == "":
            floor = 0
        expiry_date = data['expiry_date']
        ccv = data['ccv']
        holder = data['holder']
        holder_id = data['holder_id']
        res: Result = shopping_handler.purchase_items(int(user_id), int(credit_card), country, city, street,
                                                      int(house_number), expiry_date, ccv, holder, holder_id, apartment,
                                                      int(floor))
        if res.succeed:
            return jsonify(succeded=True), Status.OK
        return jsonify({'error': res.msg}), Status.NotAcceptable
    except Exception as e:
        log: Log = Log.get_instance()
        log.get_logger().error(f"comm Error:{str(e)}")
        return jsonify({'error': 'user id should be int/float'}), Status.NotAcceptable


@app.route("/logout", methods=['POST'])
def logout():
    data = request.json
    user_name = data['user_name']
    notification_handler.disconnect(user_name)
    user_id = Sess.get_user_id(data.get('rand_number', -1))
    Sess.logout(data.get('rand_number', -1))
    user_handler.logout(user_id)
    return jsonify(success=True), Status.OK


@app.route("/login", methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    user_id = int(Sess.get_user_id(data.get('rand_number', -1)))
    res: Result = user_handler.login(user_id, username, password)
    if res.succeed:
        Sess.logged(res, username, data.get('rand_number', -1))
        return jsonify({'user_id': res.requesting_id, 'username': username, "is_admin": res.data}), Status.OK
    return jsonify({'error': res.msg}), Status.Unauthorized


@app.route("/register", methods=['POST'])
def register():
    data = request.json
    username = data['username']
    email = data['email']
    password = data['password']
    user_id = Sess.get_user_id(data.get('rand_number', -1))
    res: Result = user_handler.register(user_id, username, password, email)
    if res.succeed:
        # Sess.reg()
        return jsonify({'user_id': res.requesting_id, 'username': username}), Status.Created
    return jsonify({'error': res.msg}), Status.NotAcceptable


@app.route("/search_for_stores", methods=['GET'])
def search_stores():
    user_id: int = request.args.get('user_id')
    store_name: str = request.args.get('store_name')
    try:
        res: Result = shopping_handler.search_stores(int(user_id), store_name)
        if res.succeed:
            return jsonify({'user_id': res.requesting_id, 'stores': res.data}), Status.OK
        return jsonify({'error': res.msg}), Status.NotAcceptable
    except Exception as e:
        log: Log = Log.get_instance()
        log.get_logger().error(f"comm Error:{str(e)}")
        return jsonify({'error': str(e)}), Status.NotAcceptable


@app.route("/search_products", methods=['GET'])
def search_products():
    user_id: int = request.args.get('user_id')
    product_name: str = request.args.get('product_name')
    stores_names: str = request.args.get('stores_names')
    categories: str = request.args.get('categories')
    brands: str = request.args.get('brands')
    min_price: int = request.args.get('min_price')
    max_price: int = request.args.get('max_price')
    if stores_names != "":
        stores = stores_names.split(',')
    else:
        stores = None
    if brands != "":
        brands_list = brands.split(',')
    else:
        brands_list = None
    if categories != "":
        categories_list = categories.split(',')
    else:
        categories_list = None
    try:
        res: Result = shopping_handler.search_products(int(user_id), product_name, stores, categories_list,
                                                       brands_list, int(min_price), int(max_price))
        if res.succeed:
            return jsonify({'user_id': res.requesting_id, 'products': res.data}), Status.OK
        return jsonify({'error': res.msg}), Status.NotAcceptable
    except Exception as e:
        log: Log = Log.get_instance()
        log.get_logger().error(f"comm Error:{str(e)}")
        return jsonify({'error': str(e)}), Status.NotAcceptable


@app.route("/get_product_info_view", methods=["GET"])
def get_specific_product():
    user_id: int = request.args.get('user_id')
    product_name: str = request.args.get('product_name')
    store_name: str = request.args.get('store_name')
    try:
        res: Result = shopping_handler.watch_info_on_product(int(user_id), store_name, product_name)
        if res.succeed:
            return jsonify({'user_id': res.requesting_id, 'product_info': res.data}), Status.OK
        return jsonify({'error': res.msg}), Status.NotAcceptable
    except Exception as e:
        log: Log = Log.get_instance()
        log.get_logger().error(f"comm Error:{str(e)}")
        return jsonify({'error': str(e)}), Status.NotAcceptable


@app.route("/add_item_to_shopping_cart", methods=["POST"])
def add_item_to_shopping_cart():
    data = request.json
    user_id: int = Sess.get_user_id(data.get('rand_number', -1))
    product_name: str = data['product_name']
    store_name: str = data['store_name']
    quantity: int = int(data['quantity'])
    res: Result = shopping_handler.saving_product_to_shopping_cart(product_name, store_name, user_id, quantity)
    if res.succeed:
        return jsonify({"user_id": res.requesting_id}), Status.OK
    elif res.data == -2:
        return jsonify({'error': res.msg}), Status.Conflict
    else:
        return jsonify({'error': res.msg}), Status.NotAcceptable


@app.route('/fetch_shopping_cart_by_user/<user_id>', methods=['GET'])
def fetch_shopping_cart_by_user(user_id):
    res: Result
    try:
        res: Result = shopping_handler.watch_shopping_cart(Sess.get_user_id())
        if res.succeed:
            if type(res.data) == str:
                return jsonify(
                    {"user_id": res.requesting_id, "data": {"total_price": 0, "baskets": []}}), Status.OK
            return jsonify(
                {"user_id": res.requesting_id, "data": res.data}), Status.OK
    except:
        return jsonify({'error': 'Server ERROR'}), Status.NotAcceptable
    return jsonify({'error': res.msg}), Status.Unauthorized


@app.route('/fetch_all_sub_staff/<user_id>/<store_name>', methods=['GET'])
def fetch_all_sub_staff(user_id, store_name):
    res: Result
    try:
        res: Result = inventory_handler.get_all_sub_staff_of_user(int(user_id), store_name)
        if res.succeed:
            return jsonify(
                {"user_id": res.requesting_id, "data": res.data}), Status.OK
        return jsonify({'error': res.msg}), Status.Unauthorized
    except Exception as e:
        return jsonify({'error': f'Server ERROR: {str(e)}'}), Status.NotAcceptable


@app.route('/edit_discount', methods=['POST'])
def edit_discount():
    data = request.json
    try:
        user_id = Sess.get_user_id(data.get('rand_number', -1))
        discount_id = int(data['discount_id'])
        store_name = data['storename'].strip()
        product_name = data['product_name'].strip()
        discount_type = data['discount_type'].strip()
        percent = data['percent'].strip()
        category = data['category'].strip()
        free_per_x = data['free_per_x'].strip()
        overall_product_price = data['overall_product_price'].strip()
        overall_category_price = data['overall_category_price'].strip()
        overall_product_quantity = data['overall_product_quantity'].strip()
        overall_category_quantity = data['overall_category_quantity'].strip()
        up_to_date = data['up_to_date'].strip()
        basket_size = data['basket_size'].strip()

        res: Result = inventory_handler.edit_discount(user_id, discount_id, store_name, product_name, discount_type,
                                                      percent, category, free_per_x, overall_product_price,
                                                      overall_category_price, overall_product_quantity,
                                                      overall_category_quantity, up_to_date, basket_size)

        if res.succeed:
            return jsonify(success=True), Status.OK
        return jsonify({'error': res.msg}), Status.NotAcceptable
    except:
        return jsonify({'error': 'Missing fields'}), Status.BadRequest


@app.route('/edit_policy', methods=['POST'])
def edit_policy():
    data = request.json
    try:
        user_id = data['user_id']
        storename = data['storename']
        policy_id = data["policy_id"]
        min_basket_quantity = data['min_basket_quantity']
        max_basket_quantity = data['max_basket_quantity']
        product_name = data['product_name'].strip()
        min_product_quantity = data['min_product_quantity']
        max_product_quantity = data['max_product_quantity']
        category = data['category'].strip()
        min_category_quantity = data['min_category_quantity']
        max_category_quantity = data['max_category_quantity']
        day = data['day']

        res: Result = inventory_handler.add_policy(user_id, storename, min_basket_quantity,
                                                   max_basket_quantity, product_name,
                                                   min_product_quantity, max_product_quantity, category,
                                                   min_category_quantity,
                                                   max_category_quantity, day, int(policy_id))

        if res.succeed:
            return jsonify(success=True), Status.OK
        return jsonify({'error': res.msg}), Status.NotAcceptable
    except Exception as e:
        return jsonify({'error': str(e)}), Status.BadRequest


@app.route('/add_policies', methods=['POST'])
def add_policies():
    data = request.json
    try:
        user_id = Sess.get_user_id(data.get('rand_number', -1))
        storename = data['storename']
        min_basket_quantity = data['min_basket_quantity']
        max_basket_quantity = data['max_basket_quantity']
        product_name = data['product_name'].strip()
        min_product_quantity = data['min_product_quantity']
        max_product_quantity = data['max_product_quantity']
        category = data['category'].strip()
        min_category_quantity = data['min_category_quantity']
        max_category_quantity = data['max_category_quantity']
        day = data['day']
        res: Result = inventory_handler.add_policy(user_id, storename, min_basket_quantity, max_basket_quantity,
                                                   product_name,
                                                   min_product_quantity, max_product_quantity, category,
                                                   min_category_quantity, max_category_quantity, day)
        if res.succeed:
            return jsonify(success=True), Status.OK
        return jsonify({'error': res.msg}), Status.NotAcceptable
    except Exception as e:
        return jsonify({'error': str(e)}), Status.BadRequest


@app.route('/combine_policies', methods=["POST"])
def combine_policies():
    data = request.json
    user_id = data['user_id']
    storename = data['storename']
    policies_id_list = list(map(lambda x: int(x), data['policies_id_list']))
    operator = data['operator']
    try:
        res: Result = inventory_handler.combine_policies_for_store(int(user_id), storename, policies_id_list, operator)
        if res.succeed:
            return jsonify({'success': True, 'data': res.data}), Status.OK,
        else:
            return jsonify({'error': res.msg}), Status.NotAcceptable
    except Exception as e:
        print(str(e))
        return jsonify({'error': f'{str(e)}'}), Status.BadRequest


@app.route('/combine_discounts', methods=["POST"])
def combine_discount():
    data = request.json
    user_id = Sess.get_user_id(data.get('rand_number', -1))
    storename = data['storename']
    discount_id_list = list(map(lambda x: int(x), data['discount_id_list']))
    operator = data['operator']
    try:
        res: Result = inventory_handler.combine_discount(int(user_id), storename, discount_id_list, operator)
        if res.succeed:
            return jsonify({'success': True, 'data': res.data}), Status.OK,
        else:
            return jsonify({'error': res.msg}), Status.NotAcceptable
    except Exception as e:
        print(str(e))
        return jsonify({'error': f'{str(e)}'}), Status.BadRequest


@app.route('/edit_permissions', methods=['POST'])
def edit_permissions():
    res: Result
    data = request.json
    user_id = Sess.get_user_id(data.get('rand_number', -1))
    user_edited = data['edited_user']
    store_name = data['store_name']
    can_manage_inventory = data['can_manage_inventory']
    can_manage_discount = data['can_manage_discount']
    open_and_close_store = data['open_and_close_store']
    watch_purchase_history = data['watch_purchase_history']
    appoint_new_store_manager = data['appoint_new_store_manager']
    appoint_new_store_owner = data['appoint_new_store_owner']
    try:
        res: Result = inventory_handler.editing_permissions_to_store_manager(user_id=user_id,
                                                                             username_edited=user_edited,
                                                                             store_name=store_name,
                                                                             can_manage_inventory=can_manage_inventory,
                                                                             appoint_new_store_owner=appoint_new_store_owner,
                                                                             appoint_new_store_manager=appoint_new_store_manager,
                                                                             watch_purchase_history=watch_purchase_history,
                                                                             open_and_close_store=open_and_close_store,
                                                                             can_manage_discount=can_manage_discount)
        if res.succeed:
            return jsonify(
                {"user_id": res.requesting_id}), Status.OK
        return jsonify({'error': res.msg}), Status.Unauthorized
    except Exception as e:
        return jsonify({'error': f'Server ERROR: {str(e)}'}), Status.NotAcceptable


@app.route('/delete_item_from_shopping_cart/<user_id>/<product_name>/<store_name>', methods=['DELETE'])
def delete_item_from_shopping_cart(user_id, product_name, store_name):
    res: Result
    try:
        res: Result = shopping_handler.removing_item_from_shopping_cart(product_name, store_name, int(user_id))
        if res.succeed:
            return jsonify({"user_id": res.requesting_id})
        else:
            return jsonify({'error': res.msg})
    except Exception as e:
        log: Log = Log.get_instance()
        log.get_logger().error(f"comm Error:{str(e)}")
        return jsonify({'error': str(e)})


@app.route('/update_item_from_shopping_cart/<user_id>/<product_name>/<store_name>/<quantity>', methods=['PUT'])
def update_item_from_shopping_cart(user_id, product_name, store_name, quantity):
    res: Result
    try:
        res: Result = shopping_handler.editing_quantity_shopping_cart_item(product_name, store_name, int(user_id),
                                                                           int(quantity))
        if res.succeed:
            return jsonify({"user_id": res.requesting_id, "updated": res.data}), Status.OK
        else:
            return jsonify({'error': res.msg}), Status.NotAcceptable
    except Exception as e:
        log: Log = Log.get_instance()
        log.get_logger().error(f"comm Error:{str(e)}")
        return jsonify({'error': str(e)}), Status.NotAcceptable


@app.route('/some_fun_stuff', methods=['POST'])
def some_fun_stuff():
    persistency_interface.insert_some_fun()
    return jsonify(success=True), Status.OK


@app.route('/system_admin_stats', methods=['GET'])
def fetch_stats():
    data = request.args
    start_date = data["start_date"]
    end_date = data["end_date"]
    import datetime as dt
    start_date = (dt.datetime.strptime(start_date, '%d/%m/%Y')).date()
    end_date = (dt.datetime.strptime(end_date, '%d/%m/%Y')).date()
    stat_dict = StatManager.get_instance().get_stats_in_range(start_date, end_date)
    dict_to_send = StatManager.get_instance().convert_dict_to_jsonable(stat_dict)
    return jsonify(dict_to_send), Status.OK



@socket_io.on('init', namespace="/accept")
def accept(data):
    user_name = data['data']
    print(f"-------------------incoming connection has username: {user_name}------------------------")
    notification_handler.connect(user_name)
    # msg = "Hello client"
    # socketio.emit('server message', {'data': msg}, namespace=f"/accept")


def redirect_stderr():
    open("error.txt", "w").close()  # Clear the file before
    sys.stderr = open('error.txt', 'w')


def init_app(app, dba):
    dba.init_app(app)
    ses.init_app(app)
    SqlAlchemySessionInterface(app, dba, "sessions", "prefix_", False, False)


def _init():
    global counter
    initializer.start()
    counter = 0
    while initializer.is_alive():
        print(".", end="")
        sleep(1)
        counter += 1
        if counter > 60:
            break


if __name__ == "__main__":
    # Configure session to use filesystem (instead of signed cookies)
    app.config["SESSION_TYPE"] = "sqlalchemy"

    with app.app_context():
        persistency_interface.create_all(lambda db: init_app(app, db))
        persistency_interface.send_db_status_subject(dalSubject)

    log: Log = Log.get_instance()
    log.get_logger().error(f"INITIALIZING DATA IN SERVER")
    _init()
    eventlet.wsgi.server(
        eventlet.wrap_ssl(

            eventlet.listen(("localhost", 443)),
            certfile='keys/cert.pem',
            keyfile='keys/key.pem',
            server_side=True), app)

    # redirect_stderr()
# socketio.run(app, host='localhost', port=443, debug=True, certfile="./keys/cert.pem", keyfile="./keys/key.pem")
# socketio.run(app, host='localhost', port=443, debug=True, keyfile='keys/key.pem', certfile='keys/cert.pem')


# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///session_db.db'
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/signals/
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# To see the queries that are being run
# app.config['SQLALCHEMY_ECHO'] = True
# db: SQLAlchemy = SQLAlchemy()
# db.init_app(app)
#     # db.create_all()
#     #user_handler.register(2, 'avielfedida', 'numerator$4ME', 'avielfedida@gmail.com')
#     #user_handler.login('avielfedida', 'numerator$4ME')
#     socketio.init_app(app)
#     app.run(ssl_context=('keys/cert.pem', 'keys/key.pem'), debug=True, host='localhost', port=443)
# socketio.run(app, host='localhost', port=1000, debug=True)
# __init_db_with_stores_and_products()
