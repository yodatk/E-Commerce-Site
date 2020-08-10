import random
import string
import uuid
import threading

from locust import HttpUser, task, between

registered_users = []
stores = []
products = ['apple', 'banana', 'chocolate', 'candy', 'tomato', 'carrot']


# Here we define a class for the users that we will be simulating.
# It inherits from HttpUser which gives each user a client attribute, which is an instance of HttpSession,
# that can be used to make HTTP requests to the target system that we want to load test. When a test starts,
# locust will create an instance of this class for every user that it simulates, and each of these users will
# start running within their own thread.

def random_string(string_length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))


def random_int():
    return random.randint(1, 100000000)


def random_for_init():
    return str(uuid.uuid4()).replace('-', '')


def find_user_id_according_to_name(name):
    for dic in registered_users:
        if dic['user_name'] == name:
            return dic['user_id']
        # print(dic)
        # for key, value in dic.items():
        #     print(f'id = {user_id}, name = {user_name}')
        #     if user_name == name:
        #         return user_id
    return -1


class StartUser(HttpUser):
    # determine for how long a simulated user will wait between executing tasks
    # Our class defines a wait_time function that will make the simulated users wait
    # random time between 5 and 9 seconds after each task is executed.

    wait_time = between(3, 25)

    # # method when user starts running - register & login
    # def on_start(self):
    #     """ on_start is called when a Locust start before
    #         any task is scheduled
    #     """
    #     pass
    #     # global registered_users
    #     # self.client.verify = False
    #     #
    #     # # create 100 users in order to have 10,000 registered users
    #     # for i in range(100):
    #     #     rand_number = random_for_init()
    #     #     user_name = f'user-{rand_number}'
    #     #     email = f'{user_name}@mail.com'
    #     #     self.register(user_name, email, rand_number)
    #     #     registered_users.append(user_name)
    #     #     # create 10 stores in order to have 1,000 stores
    #     #     if i > 90:
    #     #         self.login(user_name, rand_number)
    #     #         store_name = self.open_store(rand_number)
    #     #         # add 1,000 products for each store that created
    #     #         for j in range(1000):
    #     #             self.add_product_to_store(store_name, rand_number)
    #     #         self.logout(user_name, rand_number)
    #     #

    # When a load test is started, an instance of a HttpUser class will be created for each simulated user
    # and they will start running within their own thread.When these users run they pick tasks that they
    # execute, sleeps for awhile, and then picks a new task and so on.

    # @task takes an optional weight argument that can be used to specify the task’s execution ratio.
    # In the following example index will have twice the chance of being picked as profile:

    # ------------ Helper Functions ------------------

    def register(self, user_name, email, rand_number):
        self.client.post("/register",
                         json={
                             "username": user_name,
                             "password": "Parker51!",
                             "email": email,
                             "rand_number": rand_number
                         })

    def login(self, user_name, rand_number):

        response = self.client.post("/login",
                                    json={
                                        "username": user_name,
                                        "password": "Parker51!",
                                        "rand_number": rand_number
                                    })
        json_response_dict = response.json()
        # print(json_response_dict)
        request_id = json_response_dict['user_id']
        return request_id

    def logout(self, user_name, rand_number):
        self.client.post("/logout", json={"user_name": user_name, "rand_number": rand_number})

    def open_store(self, rand_number):
        store_name = random_string(20)
        self.client.post("/new_store",
                         json={"storename": store_name, "rand_number": rand_number})
        stores.append(store_name)
        return store_name

    def close_store(self, store_name, rand_number):
        self.client.post("/close_store",
                         json={"store_name": store_name, "rand_number": rand_number})

    def search_product(self, user_id):
        stores_names = ""
        categories = ""
        brands = ""
        response = self.client.get(f"/search_products?user_id={user_id}&product_name={random.choice(products)}&"
                                   f"stores_names={stores_names}&categories={categories}&brands={brands}&min_price={'0'}"
                                   f"&max_price={'50'}")
        json_response_dict = response.json()
        if 'error' not in json_response_dict and len(json_response_dict['products']) > 0:
            res_products = json_response_dict['products'][0]
            if len(res_products) > 0:
                name = res_products['product']['product']['name']
                store_name = res_products['product']['store_name']
                print(f'product name = {name}, store name = {store_name}')
                return name, store_name
        else:
            return "", ""

    def search_stores(self, user_id, store_name=None):
        if store_name is None and len(stores) == 0:
            return "", ""
        if store_name is None:
            store_name = random.choice(stores)
        response = self.client.get(f"/search_for_stores?user_id={user_id}&store_name={store_name}")
        json_response_dict = response.json()
        if 'error' not in json_response_dict and len(json_response_dict['stores']) > 0:
            res_stores = json_response_dict['stores'][0]
            if len(res_stores) > 0:
                initial_owner = res_stores['initial_owner']
                return initial_owner, store_name
        return "", ""

    def purcase_products(self, rand_number):
        self.client.post("/purchase_items",
                         json={"credit_card": "4444444444444444", "country": "Israel",
                               "city": "Eilat", "street": "Ella", "house_number": "5", "apartment": "",
                               "floor": "", "expiry_date": "08/20", "ccv": "123", "holder": "fdsfd",
                               "holder_id": "236564123", "rand_number": rand_number})

    def add_product_to_store(self, store_name, rand_number):
        product_name = random.choice(products)
        self.client.post("/add_product_to_store",
                         json={
                             "storename": store_name,
                             "product_name": product_name,
                             "base_price": 10.0,
                             "quantity": 100,
                             "categories": "food",
                             "brand": "brand_shani",
                             "description": "",
                             "rand_number": rand_number
                         })
        return product_name

    def add_store_owner(self, store_name, owner_name, rand_number):
        self.client.post("/add_store_owner",
                         json={
                             "store_name": store_name,
                             "added_username": owner_name,
                             "rand_number": rand_number
                         })

    def add_store_manager(self, store_name, manager_name, rand_number):
        self.client.post("/add_store_manager",
                         json={
                             "store_name": store_name,
                             "added_username": manager_name,
                             "rand_number": rand_number
                         })

    def delete_store_manager(self, store_name, manager_to_delete, rand_number):
        self.client.post("/delete_manager_from_store",
                         json={
                             "store_name": store_name,
                             "removed_username": manager_to_delete,
                             "rand_number": rand_number
                         })

    def add_item_to_shopping_cart(self, product_name, store_name, quantity, rand_number):
        with self.client.post("/add_item_to_shopping_cart",
                              json={
                                  "product_name": product_name,
                                  "store_name": store_name,
                                  "quantity": quantity,
                                  "rand_number": rand_number
                              }, catch_response=True) as response:
            if response.status_code == 409:
                response.success()

    def add_policies(self, store_name, min_basket_quantity, max_basket_quantity, product_name, min_product_quantity,
                     max_product_quantity, category, min_category_quantity, max_category_quantity, day, rand_number):
        self.client.post("/add_policies",
                         json={
                             "storename": store_name,
                             "min_basket_quantity": min_basket_quantity,
                             "max_basket_quantity": max_basket_quantity,
                             "product_name": product_name,
                             "min_product_quantity": min_product_quantity,
                             "max_product_quantity": max_product_quantity,
                             "category": category,
                             "min_category_quantity": min_category_quantity,
                             "max_category_quantity": max_category_quantity,
                             "day": day,
                             "rand_number": rand_number
                         })

    def add_discount_free_per_x(self, product_name, store_name, rand_number):
        response = self.client.post("/new_discount",
                                    json={
                                        "product_name": product_name,
                                        "storename": store_name,
                                        "discount_type": "2",
                                        "percent": "",
                                        "category": "",
                                        "free_per_x": "1/3",
                                        "overall_product_price": f"{product_name}:20",
                                        "overall_category_price": "",
                                        "overall_product_quantity": "",
                                        "overall_category_quantity": "",
                                        "up_to_date": "14/06/2021",
                                        "basket_size": "",
                                        "rand_number": rand_number
                                    })
        json_response_dict = response.json()
        return json_response_dict['discount_id']

    def add_discount_product_basket(self, product_name, store_name, discount_type, present, rand_number):
        response = self.client.post("/new_discount",
                                    json={
                                        "product_name": product_name,
                                        "storename": store_name,
                                        "discount_type": discount_type,
                                        "percent": present,
                                        "category": "",
                                        "free_per_x": "",
                                        "overall_product_price": "",
                                        "overall_category_price": "",
                                        "overall_product_quantity": "",
                                        "overall_category_quantity": "",
                                        "up_to_date": "14/06/2021",
                                        "basket_size": "",
                                        "rand_number": rand_number
                                    })
        json_response_dict = response.json()
        return json_response_dict['discount_id']

    def edit_discount(self, discount_id, product_name, store_name, rand_number):
        self.client.post("/edit_discount",
                         json={
                             "discount_id": discount_id,
                             "product_name": product_name,
                             "storename": store_name,
                             "discount_type": "2",
                             "percent": "",
                             "category": "",
                             "free_per_x": "1/5",
                             "overall_product_price": f"{product_name}:20",
                             "overall_category_price": "",
                             "overall_product_quantity": "",
                             "overall_category_quantity": "",
                             "up_to_date": "14/06/2021",
                             "basket_size": "",
                             "rand_number": rand_number
                         })

    def edit_permissions(self, to_edit_manager, store_name, rand_number):
        self.client.post("/edit_permissions",
                         json={
                             "edited_user": to_edit_manager,
                             "store_name": store_name,
                             "can_manage_inventory": True,
                             "can_manage_discount": True,
                             "open_and_close_store": False,
                             "watch_purchase_history": True,
                             "appoint_new_store_manager": False,
                             "appoint_new_store_owner": False,
                             "rand_number": rand_number
                         })

    # -------------- Tasks -------------------

    @task(5)
    def open_store_and_add_products(self):
        rand_number = random_int()
        user_name = str(rand_number)
        email = f'{user_name}@mail.com'
        self.register(user_name, email, rand_number)
        user_id = self.login(user_name, rand_number)
        store_name = self.open_store(rand_number)
        stores.append(store_name)
        # for i in range(5):
        self.add_product_to_store(store_name, rand_number)
        self.logout(user_name, rand_number)

    @task(5)
    def open_store_and_add_owner_and_manager(self):
        rand_number_1 = random_int()
        rand_number_2 = random_int()
        rand_number_3 = random_int()
        user_name = str(rand_number_1)
        email = f'{user_name}@mail.com'
        # register new initial owner
        self.register(user_name, email, rand_number_1)

        owner_name = random_string(6)
        manager_name = random_string(5)
        mail_owner = owner_name + "@mail.com"
        mail_manager = manager_name + "@mail.com"

        # register owner and manager
        self.register(owner_name, mail_owner, rand_number_2)
        self.register(manager_name, mail_manager, rand_number_3)

        # login new initial owner
        self.login(user_name, rand_number_1)

        store_name = self.open_store(rand_number_1)
        stores.append(store_name)
        self.add_store_owner(store_name, owner_name, rand_number_1)
        self.add_store_manager(store_name, manager_name, rand_number_1)

        self.logout(user_name, rand_number_1)

    @task(5)
    def search_products_and_stores(self):
        rand_number = random_int()
        user_name = str(rand_number)
        email = f'{user_name}@mail.com'
        self.register(user_name, email, rand_number)
        user_id = self.login(user_name, rand_number)
        if len(stores) > 0:
            self.search_stores(user_id)
        if len(products) > 0:
            self.search_product(user_id)
        self.logout(user_name, rand_number)

    @task(10)
    def add_item_to_cart_and_purchase(self):
        rand_number = random_int()
        user_name = str(rand_number)
        email = f'{user_name}@mail.com'
        self.register(user_name, email, rand_number)
        user_id = self.login(user_name, rand_number)
        # for i in range(10):
        product_name, store_name = self.search_product(user_id)
        if product_name != "":  # product exist
            self.add_item_to_shopping_cart(product_name, store_name, "5", rand_number)
            self.purcase_products(rand_number)
        self.logout(user_name, rand_number)

    @task(3)
    def search_store_and_fetch_guest(self):
        initial_owner, store_name = self.search_stores(-1)
        if store_name != "":
            self.client.get(f"/fetch_store_personal_view/{store_name}")

    @task(3)
    def open_and_close_store(self):
        rand_number = random_int()
        user_name = str(rand_number)
        email = f'{user_name}@mail.com'
        self.register(user_name, email, rand_number)
        self.login(user_name, rand_number)
        store_name = self.open_store(rand_number)
        self.close_store(store_name, rand_number)
        self.logout(user_name, rand_number)

    @task(3)
    def add_second_owner(self):
        # create store and add 2 more owner - > aggrement shtut..
        rand_number_1 = random_int()
        rand_number_2 = random_int()
        rand_number_3 = random_int()

        # register initial owner
        init_owner = str(rand_number_1)
        email = f'{init_owner}@mail.com'
        self.register(init_owner, email, rand_number_1)

        # register the future owners
        owner_1 = random_string(7)
        owner_2 = random_string(7)
        mail_owner_1 = owner_1 + "@mail.com"
        mail_owner_2 = owner_2 + "@mail.com"
        self.register(owner_1, mail_owner_1, rand_number_2)
        self.register(owner_2, mail_owner_2, rand_number_3)

        # login the initial owner and open store
        self.login(init_owner, rand_number_1)
        store_name = self.open_store(rand_number_1)

        # add first owner
        self.add_store_owner(store_name, owner_1, rand_number_1)
        # add second owner
        self.add_store_owner(store_name, owner_2, rand_number_1)

        self.logout(init_owner, rand_number_1)

        # login owner_1 for approve owner_2
        self.login(owner_1, rand_number_2)
        self.client.post("/approve_new_owner",
                         json={
                             "storename": store_name,
                             "username": owner_2,
                             "rand_number": rand_number_2
                         })
        self.logout(owner_1, rand_number_2)

    @task(4)
    def add_policy(self):
        rand_number = random_int()
        user_name = str(rand_number)
        email = f'{user_name}@mail.com'
        self.register(user_name, email, rand_number)
        self.login(user_name, rand_number)
        store_name = self.open_store(rand_number)
        self.add_policies(store_name, "2", "", "", "", "", "", "", "", "", rand_number)
        self.add_policies(store_name, "", "", random.choice(products), "2", "", "", "", "", "", rand_number)
        self.logout(user_name, rand_number)

    @task(5)
    def create_edit_delete_products(self):
        rand_number = random_int()
        user_name = str(rand_number)
        email = f'{user_name}@mail.com'
        self.register(user_name, email, rand_number)
        self.login(user_name, rand_number)
        # open store and add 3 new products
        store_name = self.open_store(rand_number)
        stores.append(store_name)
        products_to_update = [0] * 2
        for i in range(2):
            products_to_update[i] = self.add_product_to_store(store_name, rand_number)
        print(f'products in store {store_name} are {products_to_update}')
        # edit first product
        self.client.post("/edit_product",
                         json={
                             "storename": store_name,
                             "product_name": products_to_update[0],
                             "brand": "avi_brand",
                             "new_price": 20.0,
                             "categories": "food_1",
                             "quantity": 50,
                             "description": "the best",
                             "rand_number": rand_number
                         })
        # delete second product
        self.client.post("/remove_product",
                         json={
                             "storename": store_name,
                             "product_name": products_to_update[1],
                             "rand_number": rand_number
                         })

        # try to add to cart - FAIL
        self.add_item_to_shopping_cart(products_to_update[1], store_name, "6", rand_number)
        self.logout(user_name, rand_number)

    @task(4)
    def add_discount_edit_discount(self):
        rand_number = random_int()
        user_name = str(rand_number)
        email = f'{user_name}@mail.com'
        self.register(user_name, email, rand_number)
        self.login(user_name, rand_number)
        store_name = self.open_store(rand_number)
        stores.append(store_name)
        for i in range(5):
            product_name = self.add_product_to_store(store_name, rand_number)
            discount_id = self.add_discount_free_per_x(product_name, store_name, rand_number)
            self.edit_discount(discount_id, product_name, store_name, rand_number)

    @task(4)
    def add_combo_discounts(self):
        rand_number = random_int()

        # create new owner and store
        user_name = str(rand_number)
        email = f'{user_name}@mail.com'
        self.register(user_name, email, rand_number)
        self.login(user_name, rand_number)

        store_name = self.open_store(rand_number)
        product_name = self.add_product_to_store(store_name, rand_number)

        # create discount for product
        discount_product_id = self.add_discount_product_basket(product_name, store_name, "1", "10", rand_number)
        # create discount for basket
        discount_basket_id = self.add_discount_product_basket("", store_name, "5", "5", rand_number)
        # combine discounts
        self.client.post("/combine_discounts",
                         json={
                             "storename": store_name,
                             "discount_id_list": [discount_product_id, discount_basket_id],
                             "operator": "OR",
                             "rand_number": rand_number
                         })

    @task(4)
    def add_manager_edit_stuff_remove(self):
        rand_number_1 = random_int()
        rand_number_2 = random_int()
        # register initial owner
        init_owner = str(rand_number_1)
        email = f'{init_owner}@mail.com'
        self.register(init_owner, email, rand_number_1)

        # register future manager
        manager = random_string(7)
        mail_manager = manager + "@mail.com"
        self.register(manager, mail_manager, rand_number_2)

        # login init owner
        self.login(init_owner, rand_number_1)
        store_name = self.open_store(rand_number_1)
        self.add_store_manager(store_name, manager, rand_number_1)

        # edit permissions
        self.edit_permissions(manager, store_name, rand_number_1)

        # remove manager
        self.delete_store_manager(store_name, manager, rand_number_1)
        self.logout(init_owner, rand_number_1)

# todo
# locust -f src\communication\client\src\locustfile.py --host=http://localhost:3000
