from __future__ import annotations

import json
from typing import TYPE_CHECKING

from sqlalchemy import orm

if TYPE_CHECKING:
    from src.domain.system.data_handler import DataHandler
    from src.domain.system.store_classes import Store

import enum
from datetime import datetime
from logging import Logger

from src.domain.system.cart_purchase_classes import ShoppingCart, PurchaseReport
from src.domain.system.permission_classes import Permission, Role
from src.domain.system.products_classes import ProductInInventory
from src.domain.system.users_classes import User, LoggedInUser
from src.external.payment_interface.payment_system import _PaymentSystem
from src.external.publisher import Publisher
from src.external.supply_interface.supply_system import _ShippingSystem
from src.logger.log import Log
from src.protocol_classes.classes_utils import TypeChecker, Result, TypedList, TypedDict
from src.domain.system.DAL import DAL
from src.domain.system.db_config import db


class StoreAdministration:
    """
    Class for performing administration action regarding store management
    """

    def __init__(self, data_handler: DataHandler):
        self._data_handler: DataHandler = data_handler
        self._dal: DAL = DAL.get_instance()

    # def _get_and_check_login_user_user_id(self, username: str):
    #     """
    #     retrieve a registered in user from data handler.
    #     :param user_id:(int) id of the wanted user
    #     :return: logged in user by with that id. if the user does not exists or it's not registered, return None
    #     """
    #     res: Result = self._data_handler.get_user_by_username_as_loggedInUser(username)
    #     if res.succeed:
    #         return res.data
    #     return res.data

    def _get_and_check_login_user(self, user_id: int):
        """
        retrieve a registered in user from data handler.
        :param user_id:(int) id of the wanted user
        :return: logged in user by with that id. if the user does not exists or it's not registered, return None
        """
        user: User = self._data_handler.get_user_by_id(user_id)
        if user is None or user.user_state is None:  # if not exists or not registered
            return None
        self._dal.add(user.user_state, add_only=True)
        # if not user.user_state.is_connected:  # if not logged id
        #     return None
        return user

    def get_all_stores_of_user(self, username: str):
        """
        get all the stores that the current user have administration permission in
        :param user_id: (int) id of the user
        :return: list of stores that the current user is managing owning
        """
        user: LoggedInUser = self._data_handler.get_user_by_username(username)
        # all stores that the user is part of the staff in, as dictionaries
        self._dal.add(user, add_only=True)
        all_permissions = user.permissions
        self._dal.add_all(list(all_permissions.values()), add_only=True)
        for p in all_permissions.values():
            self._dal.add(p.store)

        all_stores = [all_permissions[p].store.to_dictionary() for p in all_permissions if p != '']
        return Result(True, -1, "All Stores are in data", all_stores)

    def get_all_products_of_store(self, user_id: int, store_name: str):
        """
        get all the products of the current store
        :param user_id: (int) id of the user
        :param store_name: (str) name of store
        :return: list of products of the current store
        """
        if type(user_id) != int or user_id < 0 or not TypeChecker.check_for_non_empty_strings([store_name]):
            return Result(False, user_id if type(user_id) == int else -1, "wrong input types",
                          None)
        else:

            user: User = self._get_and_check_login_user(user_id)
            if user is None:
                return Result(False, user_id,
                              f"user id ({user_id} is not of an existing registered, and logged in user",
                              None)
            res: Result = self._data_handler.get_store_by_name(store_name)
            if not res.succeed:
                return res
            else:
                store: Store = res.data
                items = store.inventory.items()
                all_products = [p.to_dictionary() for k, p in items]
                return Result(True, user_id, "All products in store", all_products)

    # 4.1
    def add_existing_in_inventory_product_to_store(self, user_id: int, store_name: str, product_name: str,
                                                   base_price: float, quantity: int, brand: str = "",
                                                   categories: TypedList = None, description: str = ""):
        """
        adding new product to store system, when you dont need to order it
        :param user_id: (str) username of the user that is adding new product
        :param store_name:(str) name of the store
        :param product_name: (str) name of the product that is adding to the inventory of the store
        :param base_price: (float) base price for the new product
        :param quantity:(int) number of items to add
        :param brand:(str) brand of the product
        :param categories:(TypedList of str) categories of the product
        :param description(str) description of the product
        :return: Result object with information on the process
        """
        if categories is None:
            categories = TypedList(str)
        elif categories is None or (isinstance(categories, list) and len(categories) == 0):
            categories = TypedList(str, categories)
        if brand is None:
            brand = ""
        if not TypeChecker.check_for_non_empty_strings(
                [store_name, product_name]) or not TypeChecker.check_for_positive_number(
            [user_id, base_price, quantity]) or type(description) != str:
            return Result(False, user_id if type(user_id) == int else -1, "Wrong types", None)

        else:
            user: User = self._get_and_check_login_user(user_id)
            if user is None:
                return Result(False, user_id,
                              f"user id ({user_id} is not of an existing registered, and logged in user",
                              None)
            self._dal.add(user.user_state, add_only=True)
            if store_name not in user.user_state.permissions:
                return Result(False, user_id, "user is not a staff member in that store", None)
            else:

                perm = self.adding_acting_permission(store_name, user)
                return perm.add_product_to_store(product_name, base_price, quantity, brand, categories, description)

    def remove_product_from_store(self, user_id: int, store_name: str, product_name: str):
        """
        removing existing product from store
        :param user_id: (str) username of the user that is adding new product
        :param store_name:(str) name of the store
        :param product_name: (str) name of the product that is adding to the inventory of the store
        :return: Result with success, or with fail info
        """
        if not TypeChecker.check_for_non_empty_strings(
                [store_name, product_name]) or not TypeChecker.check_for_positive_number([user_id]):
            return Result(False, user_id if type(user_id) == int else -1, "expected 1 integer and 2 strings", None)
        else:
            user: User = self._get_and_check_login_user(user_id)
            if user is None:
                return Result(False, user_id,
                              f"user id ({user_id} is not of an existing registered, and logged in user",
                              None)
            elif store_name not in user.user_state.permissions:
                return Result(False, user_id, "user is not a staff member in that store", None)
            else:
                perm = self.adding_acting_permission(store_name, user)
                return perm.remove_product(product_name)
        # else:
        #     return self._data_handler.remove_product_from_store(user_id if type(user_id) == int else -1, store_name,
        #                                                         product_name)

    def adding_acting_permission(self, store_name, user):
        perm: Permission = user.user_state.permissions[store_name]
        res = self._dal.add(perm, add_only=True)
        if res:
            user.user_state.permissions[store_name] = res
            return res
        return perm

    def edit_existing_product_in_store(self, user_id: int, store_name: str, product_name: str, brand: str,
                                       new_price: float, quantity: int,
                                       categories: TypedList = None, description: str = ""):
        """
        editing an existing product in store
        :param user_id: (str) username of the user that want to edit the product
        :param store_name: (str) store that the user want to edit in
        :param product_name:(str) name of the product to edit
        :param brand:(str) name of the new brand to edit
        :param new_price:(float) new base price for the product
        :param categories:(list of str) list of new categories to edit by
        :param description: (str) new description of the product
        :return: Result with success, or with fail info
        """
        if categories is None:
            categories = TypedList(str)
        elif isinstance(categories, list):
            categories = TypedList(str, categories)
        if brand is None:
            brand = ""

        if not TypeChecker.check_for_non_empty_strings(
                [store_name, product_name]) or not TypeChecker.check_for_positive_number(
            [new_price, user_id]) or not isinstance(categories, TypedList) or not categories.check_types(str) or (
                type(brand) != str) or type(description) != str:
            return Result(False, user_id if type(user_id) == int else -1,
                          "input error. check for valid names, and positive price and quantity",
                          None)

        else:
            user: User = self._get_and_check_login_user(user_id)
            if user is None:
                return Result(False, user_id,
                              f"user id ({user_id} is not of an existing registered, and logged in user",
                              None)
            elif store_name not in user.user_state.permissions:
                return Result(False, user_id, "user is not a staff member in that store", None)
            else:
                perm = self.adding_acting_permission(store_name, user)
                return perm.edit_existing_product(product_name, brand, new_price, quantity, categories, description)
            # return self._data_handler.edit_product_detail_in_store(user_id, store_name, product_name, brand,
            # new_price, categories)

    # 4.6
    def editing_permissions_to_store_member(self, username_editing_id: id, username_edited: str, store_name: str,
                                            can_manage_inventory: bool = False, appoint_new_store_owner: bool = False,
                                            appoint_new_store_manager: bool = False,
                                            watch_purchase_history: bool = False,
                                            open_and_close_store: bool = False,
                                            can_manage_discount: bool = False):
        """
        editing permission to a staff member
        :param username_editing_id: (int) number of the user to add
        :param username_edited: (str) username of the user to edit
        :param store_name: (str) name of the store
        :param can_manage_inventory: True if user can manage the inventory of the store, False otherwise
        :param appoint_new_store_owner:  True if user can appoint new owner, False otherwise
        :param appoint_new_store_manager:  True if user can appoint new manager, False otherwise
        :param watch_purchase_history:  True if user can watch store purchase history, False otherwise
        :param open_and_close_store:  True if user can open and close the store, False otherwise
        :param can_manage_discount:  True if user can manage discount of the store, False otherwise
        :return:
        """
        if not TypeChecker.check_for_non_empty_strings(
                [username_edited, store_name]) or not TypeChecker.check_for_list_of_bool([
            can_manage_inventory,
            appoint_new_store_owner,
            appoint_new_store_manager,
            can_manage_discount,
            watch_purchase_history,
            open_and_close_store
        ]) or type(username_editing_id) != int or username_editing_id < 0:
            return Result(False, username_editing_id if type(username_editing_id) == int else -1,
                          "username and store must be string, all other parameters must be bool", None)
        else:
            user: User = self._get_and_check_login_user(username_editing_id)
            if user is None:
                return Result(False, username_editing_id,
                              f"user id ({username_editing_id} is not of an existing registered, and logged in user",
                              None)
            self._dal.add(user.user_state, add_only=True)
            if store_name not in user.user_state.permissions:
                return Result(False, username_editing_id, "user is not a staff member in that store", None)

            else:
                perm = self.adding_acting_permission(store_name, user)
                res = self._dal.add(perm, add_only=True)
                if res:
                    perm = res
                    user.user_state.permissions[store_name] = res
                res: Result = perm.edit_permission(username_edited, can_manage_inventory, appoint_new_store_owner,
                                                   appoint_new_store_manager, watch_purchase_history,
                                                   open_and_close_store,
                                                   can_manage_discount)
                if res.succeed:
                    edited_user_obj = res.data
                    updated = self._dal.add(edited_user_obj, add_only=True)
                    if updated:
                        edited_user_obj = updated
                    res1: Result = self._data_handler.get_user_by_username_as_result(username_edited)
                    if res1.requesting_id != -1:
                        self._data_handler.add_or_update_user_state(edited_user_obj, res1.requesting_id)
                    self._dal.add(perm, add_only=True)
                    self._dal.add(edited_user_obj, add_only=True)
                return res
            #
            # return self._data_handler.edit_permissions_to_existing_manager(username_editing_id, username_edited.strip(),
            #                                                                store_name.strip(), can_manage_inventory,
            #                                                                appoint_new_store_owner,
            #                                                                appoint_new_store_manager,
            #                                                                edit_management_options_for_appoints,
            #                                                                remove_appointee_store_manager,
            #                                                                watch_purchase_history, open_and_close_store)

    def __add_or_remove_member(self, acting_member: int, edited_member: str, store_name: str, is_owner: bool,
                               is_added: bool):
        """
        adding or removing staff member
        :param acting_member: (int) id of the user to perform the action
        :param edited_member: (str) name of the user to add or remove
        :param store_name: (str) name of the store to edit
        :param is_owner: (bool) True if to add\remove as owner, False if as manager
        :param is_added: (bool) True if to add member, False if to remove
        :return: Result with info on process
        """
        if not TypeChecker.check_for_non_empty_strings(
                [store_name, edited_member]) or not TypeChecker.check_for_positive_number(
            [acting_member]):
            return Result(False, acting_member if type(acting_member) == int else -1,
                          "type error : expected id(int), username to add(str), and store name(str)", None)
        user: User = self._get_and_check_login_user(acting_member)
        if user is None:
            return Result(False, acting_member,
                          f"user id ({acting_member} is not of an existing registered, and logged in user",
                          None)
        self._dal.add(user.user_state, add_only=True)
        if store_name not in user.user_state.permissions:
            return Result(False, acting_member, "user is not a staff member in that store", None)

        else:
            member_to_work_on: LoggedInUser = self._data_handler.get_user_by_username(edited_member)

            if member_to_work_on is None:  # or member_to_work_on.user_state is None:
                return Result(False, acting_member, f"didnt find a registered user named: {edited_member}",
                              None)
            self._dal.add(member_to_work_on, add_only=True)
            perm = self.adding_acting_permission(store_name, user)
            # # Begin transaction here
            # self._dal.begin_nested() # Init transaction
            # try:
            if is_owner:
                res: Result = perm.add_store_owner(member_to_work_on) if is_added else perm.remove_owner(edited_member)
                if not res.succeed:
                    return res

            else:
                res: Result = perm.add_store_manager(member_to_work_on) if is_added else perm.remove_manager(
                    edited_member)
                if not res.succeed:
                    return res
            self._dal.add(member_to_work_on, add_only=True)
            if not is_added:
                to_delete_perm, to_delete_from_store = res.data
                # self._data_handler.remove_permission_of_user_from_store([p._user_fk for p in to_delete_perm],
                #                                                        store_name)
                store: Store = perm.store
                store.remove_member(to_delete_from_store)
                temp = json.loads(store._permissions_ls)
                self._dal.update_store_permissions_ls(store_name, json.dumps([name for name in temp if
                                                                              name not in to_delete_from_store or name == store._initial_owner_fk]))
                self._dal.add(perm, add_only=True)

                # self._dal._db_session.commit()
                # self._dal.add_all([perm.store, perm])
                to_delete = [(p._user_fk, p._store_fk) for p in to_delete_perm]
                self._dal.delete_permissions_as_query(to_delete)
                to_update = perm._managers_appointed_ls if not is_owner else perm._owners_appointed_ls
                if edited_member in to_update:
                    to_update.remove(edited_member)
                # x = perm.id
                self._dal.update_permission_of_acting_member_after_deletion((perm._user_fk, perm._store_fk), is_owner,
                                                                            to_update)
                # self._dal.commit() # Commit transaction

            return Result(res.succeed, res.requesting_id, res.msg, member_to_work_on.user_name)

            # except Exception as e:
            #     self._dal.rollback() # Rollback transaction
            #     return Result(False, acting_member, "Rollback performed: " + str(e), member_to_work_on.user_id)

    # 4.3
    def adding_new_owner_to_store(self, username_adding: int, username_added: str, store_name: str):
        """
        adding new owner to existing store
        :param username_adding: (str) username that of the user who is exist in the given store as owner
        :param username_added: (str) username to add as owner to the given store
        :param store_name: (str) name of the store to add owner
        :return: Result object with details of the process
        """
        return self.__add_or_remove_member(username_adding, username_added, store_name, is_owner=True, is_added=True)
        # return self._data_handler.add_new_owner_to_store(requesting_user_id=username_adding,
        #                                                  new_user_as_owner=username_added, store_name=store_name)

    def propose_new_owner_to_store(self, proposer_id: int, candidate_name: str, store_name: str):
        """
        adding new owner to existing store
        :param proposer_id: (int) username that of the user who is exist in the given store as owner
        :param candidate_name: (str) username to add as owner to the given store
        :param store_name: (str) name of the store to add owner
        :return: Result object with details of the process
        """

        if not TypeChecker.check_for_non_empty_strings(
                [store_name, candidate_name]):
            return Result(False, proposer_id if type(proposer_id) == int else -1,
                          "type error : expected id(str), username to add(str), and store name(str)", None)
        ret = self._get_and_check_login_user(proposer_id)
        proposer: LoggedInUser = ret.user_state
        self._dal.add(proposer, add_only=True)
        if proposer is None:
            return Result(False, proposer_id,
                          f"user name ({proposer_id} is not of an existing registered, and logged in user",
                          None)
        elif proposer.user_name == candidate_name:
            return Result(False, proposer_id,
                          f"cannot propose yourself as new owner",
                          None)

        elif store_name not in proposer.permissions:
            return Result(False, proposer_id, "user is not a staff member in that store", None)
        else:
            res: Result = self._data_handler.get_store_by_name(store_name)
            store: Store = res.data
            ret = self._dal.add(store, add_only=True)
            if ret:
                store = ret
            if store is None:
                return Result(False, proposer_id, f"didnt find a store named: {store_name}", None)
            member_to_work_on: LoggedInUser = self._data_handler.get_user_by_username(candidate_name)
            # member_to_work_on: LoggedInUser = member_to_work_on_u.user_state
            if member_to_work_on is None:
                return Result(False, proposer_id, f"didnt find a registered user named: {candidate_name}", None)
            self._dal.add(member_to_work_on, add_only=True)
            perm: Permission = proposer.permissions[store_name]
            ret = self._dal.add(perm, add_only=True)
            if ret:
                perm = ret
                proposer.permissions[store_name] = ret
            if perm.role != Role.store_owner.value and perm.role != Role.store_initial_owner.value:
                return Result(False, proposer_id, "user is not an owner in that store", None)

            appointment = store._pending_ownership_proposes.get(candidate_name)
            if appointment is not None:
                self._dal.add(appointment, add_only=True)
                if appointment.active:
                    return Result(False, proposer_id, "Active Appointment Agreement for candidate already exist", None)
            # self._dal.add(proposer)
            # self._dal.add(store)
            # try:
            #     self._dal.add(member_to_work_on)
            # except:
            #     pass
            ag = AppointmentAgreement(store, member_to_work_on, proposer)
            ag._store = store
            ag._candidate = member_to_work_on
            ag._proposer = proposer
            self._dal.add(ag, add_only=True)
            store.add_appointement_agreement(ag)
            ag.respond(proposer.user_name, Approval.approved, self, proposer_id)
            self._dal.add_all([ag, store], add_only=True)
            return Result(True, proposer_id, "Approval Agreement created for ",
                          store._pending_ownership_proposes[candidate_name])

    def fetch_awaiting_approvals(self, user_id: int, store_name: str):
        try:
            user: User = self._get_and_check_login_user(user_id)
            if user is None:
                return Result(False, user_id, "user was not found or it's not connected", None)
            u: LoggedInUser = user.user_state
            result: Result = self._data_handler.get_store_by_name(store_name)
            if not result.succeed:
                raise Exception("Could not find store")
            store: Store = result.data
            res = []
            for (candid, appObj) in store._pending_ownership_proposes.items():
                if u.user_name in appObj.approval_dict:
                    if appObj._active:
                        res.append({
                            'username': appObj._candidate_fk,
                            'suggested_by': appObj._proposer_fk,
                            'approved': len(
                                list(filter(lambda x: x == Approval.approved, appObj._approval_dict.values()))),
                            'pending': len(
                                list(filter(lambda x: x == Approval.pending, appObj._approval_dict.values())))
                        })
            return Result(True, user_id, "Obtained awaiting approvals", res)
        except:
            pass
        return Result(False, user_id, "Failed to obtain awaiting approvals", None)

    def respond_new_owner_to_store(self, responder_id: int, candidate_name: str, store_name: str, response: int):
        """
        adding new owner to existing store
        :param responder_name: (str) username that of the user who is exist in the given store as owner
        :param candidate_name: (str) username to add as owner to the given store
        :param store_name: (str) name of the store to add owner
        :param response: enum representing responder's respons
        :return: Result object with details of the process
        """
        if not TypeChecker.check_for_non_empty_strings([store_name, candidate_name]):
            return Result(False, responder_id if type(responder_id) == int else -1,
                          "type error : expected id(int), username to add(str), and store name(str)", None)
        ret = self._get_and_check_login_user(responder_id)
        proposer: LoggedInUser = ret.user_state

        responder_name = proposer.user_name
        if proposer is None:
            return Result(False, -1,
                          f"user id ({responder_name} is not of an existing registered, and logged in user",
                          None)
        elif store_name not in proposer.permissions:
            return Result(False, -1, "user is not a staff member in that store", None)
        else:
            # self._dal.add(proposer)
            res: Result = self._data_handler.get_store_by_name(store_name)
            store: Store = res.data
            if store is None:
                return Result(False, responder_id, f"didnt find a store named: {store_name}", None)
            res_store = self._dal.add(store, add_only=True)
            if res_store:
                store = res_store
            member_to_work_on: LoggedInUser = self._data_handler.get_user_by_username(candidate_name)
            if member_to_work_on is None:
                return Result(False, -1, f"didnt find a registered user named: {candidate_name}", None)
            self._dal.add(member_to_work_on, add_only=True)
            perm: Permission = proposer.permissions[store_name]
            res_perm = self._dal.add(perm, add_only=True)
            if res_perm:
                perm = res_perm
                proposer.permissions[store_name] = perm
            if perm.role != Role.store_owner.value and perm.role != Role.store_initial_owner.value:
                return Result(False, -1, "user is not an owner in that store", None)

            agreement: AppointmentAgreement = store._pending_ownership_proposes.get(candidate_name)

            if agreement is None:
                return Result(False, -1, f"didnt find Approval agreement for {candidate_name}", None)
            self._dal.add(agreement, add_only=True)
            if not agreement.active:
                return Result(False, -1, f"Approval agreement for {candidate_name} is inactive", None)

            # self._dal.add(proposer)
            # self._dal.add(store)
            # self._dal.add(member_to_work_on)
            # ag = AppointmentAgreement(store, member_to_work_on, proposer)
            # ag._store = store
            # ag._candidate = member_to_work_on
            # ag._proposer = proposer
            # # ag.respond(responder_name, response)
            # self._dal.add(ag)
            # # store.add_appointement_agreement(ag)
            # self._dal.add_all([ag, store])
            agreement.respond(proposer.user_name, Approval(response), self, responder_id)
            self._dal.add(store, add_only=True)
            self._dal.add(agreement, add_only=True)
            return Result(True, responder_id, "Responded created for ",
                          store._pending_ownership_proposes[candidate_name])

    # 4.5
    def adding_new_manager_to_store(self, username_adding: int, username_added: str, store_name: str):

        """
        adding new manager to existing store
        :param username_adding: (int) username that of the user who is exist in the given store as owner
        :param username_added: (str) username to add as manager to the given store
        :param store_name: (str) name of the store to add owner
        :return: True if successful, False otherwise
        """
        return self.__add_or_remove_member(username_adding, username_added, store_name, is_owner=False, is_added=True)
        # if not TypeChecker.check_for_non_empty_strings(
        #         [store_name, username_added]) or not TypeChecker.check_for_positive_number(
        #     [username_adding]):
        #     return Result(False, username_adding if type(username_adding) == int else -1,
        #                   "type error : expected id(int), username to add(str), and store name(str)", None)
        # return self._data_handler.add_new_manager_to_store(requesting_user_id=username_adding,
        #                                                    new_user_as_manager=username_added, store_name=store_name)

    # 4.7
    def removing_store_manager(self, user_id: int, username_removed: str, store_name: str):
        """

        :param user_id: (int) username of the user who removes the another owner
        :param username_removed: (str) username of the user that needs to be removed
        :param store_name: (str) name of the store to remove user from as owner
        :return: Result object with info on process
        """
        return self.__add_or_remove_member(user_id, username_removed, store_name, is_owner=False,
                                           is_added=False)

    # 4.4
    def removing_store_owner(self, username_removing_id: int, username_removed: str, store_name: str):
        """

        :param username_removing_id: (str) username of the user who removes the another owner
        :param username_removed: (str) username of the user that needs to be removed
        :param store_name: (str) name of the store to remove user from as owner
        :return: Result object with info on process
        """
        return self.__add_or_remove_member(username_removing_id, username_removed, store_name, is_owner=True,
                                           is_added=False)

    def get_all_sub_staff_of_user(self, user_id, store_name):
        """
        get all sub managers and all sub owners of the given user id with the given store, if possible
        :param user_id: (int) user to get sub stuff to
        :param store_name:(str) name of the store
        :return: list of all sub suff of that user. if the user is not part of the staff of the store -> will return error
        """
        if not TypeChecker.check_for_non_empty_strings(
                [store_name]) or not TypeChecker.check_for_positive_number(
            [user_id]):
            return Result(False, user_id if type(user_id) == int else -1,
                          "type error : user_id(int) and store name(str)", None)
        user: User = self._get_and_check_login_user(user_id)
        if user is None:
            return Result(False, user_id,
                          f"user id ({user_id} is not of an existing registered, and logged in user",
                          None)
        elif store_name not in user.user_state.permissions:
            return Result(False, user_id, "user is not a staff member in that store", None)

        else:
            perm: Permission = user.user_state.permissions[store_name]
            self._dal.add(perm, add_only=True)
            output_before_dictionaries = perm.get_all_sub_permissions(direct_staff_only=True)
            output = []
            for name, perm in output_before_dictionaries.items():
                if name != user.user_state.user_name and perm.role == Role.store_manager.value:
                    output.append(perm.to_dictionary())
            return Result(True, user_id,
                          f"User({user_id}) got all sub staff from store({store_name}), total of {len(output)}" if len(
                              output) > 0 else f"User({user_id}) has no sub-staff from store({store_name})", output)

    def watch_store_purchase_history(self, requesting_user_id: int, store_name: str):
        """
        watch all the purchases made in the given store
        :param requesting_user_id: (int) username of the user who want to watch to purchase history
        :param store_name:(str) store name to watch purchase history of
        :return: Result object containing a list of requested purchases
        """
        if type(requesting_user_id) != int or requesting_user_id < 0 or not TypeChecker.check_for_non_empty_strings(
                [store_name]):
            return Result(False, requesting_user_id if type(requesting_user_id) == int else -1, "wrong input types",
                          None)
        else:

            user: User = self._get_and_check_login_user(requesting_user_id)
            if user is None:
                return Result(False, requesting_user_id,
                              f"user id ({requesting_user_id} is not of an existing registered, and logged in user",
                              None)
            res: Result = self._data_handler.get_store_by_name(store_name)
            if not res.succeed:
                return res
            else:
                store: Store = res.data
                return store.watch_purchase_history(user)

            # return self._data_handler.watch_all_purchases_from_store(requesting_user_id, store_name)

    def _open_or_close_existing_store(self, requesting_user_id: int, store_name: str, to_open: bool):
        """
        open an existing store
        :param requesting_user_id: (int) id of the user who wants to open the store
        :param store_name: (str) name of the store to open
        :param to_open:(bool) True if to open store, False if to close
        :return: Result object with reasons for failures, or success
        """
        if not (TypeChecker.check_for_non_empty_strings([store_name]) and TypeChecker.check_for_positive_number(
                [requesting_user_id])):
            return Result(False, requesting_user_id if type(requesting_user_id) == int else -1, "wrong types", None)
        else:
            user: User = self._get_and_check_login_user(requesting_user_id)
            if user is None:
                return Result(False, requesting_user_id,
                              f"user id ({requesting_user_id} is not of an existing registered, and logged in user",
                              None)
            elif store_name not in user.user_state.permissions:
                return Result(False, requesting_user_id, "user is not a staff member in that store", None)
            else:
                perm: Permission = user.user_state.permissions[store_name]
                self._dal.add(perm, add_only=True)
                return perm.open_store() if to_open else perm.close_store()

    def open_existing_store(self, requesting_user_id: int, store_name: str):
        """
        open an existing store
        :param requesting_user_id: (int) id of the user who wants to open the store
        :param store_name: (str) name of the store to open
        :return: Result object with reasons for failures, or success
        """
        return self._open_or_close_existing_store(requesting_user_id, store_name, to_open=True)

        # return Result(False, requesting_user_id if type(requesting_user_id) == int else -1, "wrong types", None)

    def close_existing_store(self, requesting_user_id: int, store_name: str):
        """
        close an existing store
        :param requesting_user_id: (int) id of the user who wants to open the store
        :param store_name: (str) name of the store to open
        :return: Result object with reasons for failures, or success
        """
        return self._open_or_close_existing_store(requesting_user_id, store_name, to_open=False)

        # if TypeChecker.check_for_non_empty_strings([store_name]) and TypeChecker.check_for_positive_number(
        #         [requesting_user_id]):
        #     return self._data_handler.close_store(user_id=requesting_user_id, store_name=store_name)
        # else:
        #     return Result(False, requesting_user_id if type(requesting_user_id) == int else -1, "wrong types", None)

    def open_a_new_store(self, initial_owner_user_id: int, store_name: str):
        """
        opening a new store for a logged in user
        :param handler:
        :param initial_owner_user_id: user that want to open a new store
        :param store_name: the name of the store to be opened
        :return: Result Object with details of the process
        """

        if not TypeChecker.check_for_non_empty_strings([store_name]) or not TypeChecker.check_for_positive_number(
                [initial_owner_user_id]):
            return Result(False, initial_owner_user_id if type(initial_owner_user_id) == int else -1, "Types error",
                          None)
        else:
            user: User = self._get_and_check_login_user(initial_owner_user_id)
            if user is None:
                return Result(False, initial_owner_user_id,
                              f"user id ({initial_owner_user_id} is not of an existing registered, and logged in user",
                              None)
            self._dal.add(user.user_state, add_only=True)

            res: Result = self._data_handler.get_store_by_name(store_name)
            if res.data is not None:
                return Result(False, initial_owner_user_id, "Store name is already taken", None)

            else:
                from src.domain.system.store_classes import Store
                new_store: Store = Store(store_name, user.user_state.user_name, initial_owner_obj=user.user_state)
                initial_permission: Permission = Permission.define_permissions_for_init(Role.store_initial_owner,
                                                                                        user.user_state.user_name,
                                                                                        new_store.name, None,
                                                                                        user.user_state, new_store)
                new_store.add_store_member(initial_permission)
                username: str = user.user_state.user_name
                user.user_state.add_permission(initial_permission)
                self._dal.add_new_store(new_store, initial_permission)
                # new_store.add_store_member(initial_permission)
                # user.user_state.add_permission(initial_permission)
                # self._data_handler.add_store(new_store)
                res: Result = Result(True, initial_owner_user_id,
                                     f"new store named {store_name} opened successfully by {initial_owner_user_id}",
                                     None)
                if res.succeed:
                    self._dal.commit()
                    self._data_handler.update_stats_counter_for_user(1, username, 3)
                return res

    def add_policy_to_store(self, requesting_user_id: int, store_name: str, min_basket_quantity: int,
                            max_basket_quantity: int, product_name: str, min_product_quantity: int,
                            max_product_quantity: int, category: str, min_category_quantity: int,
                            max_category_quantity: int, day: str, policy_id: int = -1):
        if not (TypeChecker.check_for_non_empty_strings([store_name]) and
                TypeChecker.check_for_positive_number([requesting_user_id])):
            return Result(False, requesting_user_id if type(requesting_user_id) == int else -1, "wrong types", None)
        else:
            user: User = self._get_and_check_login_user(requesting_user_id)
            if user is None:
                return Result(False, requesting_user_id,
                              f"user id ({requesting_user_id} is not of an existing registered, and logged in user",
                              None)
            elif store_name not in user.user_state.permissions:
                return Result(False, requesting_user_id, "user is not a staff member in that store", None)
            else:
                perm: Permission = self.adding_acting_permission(store_name, user)
                return perm.add_policy(min_basket_quantity, max_basket_quantity, product_name,
                                       min_product_quantity, max_product_quantity, category,
                                       min_category_quantity, max_category_quantity, day, policy_id)

    def remove_policy_to_store(self, requesting_user_id: int, store_name: str, to_remove: int):
        if not (TypeChecker.check_for_non_empty_strings([store_name]) and
                TypeChecker.check_for_positive_number([requesting_user_id])):
            return Result(False, requesting_user_id if type(requesting_user_id) == int else -1, "wrong types", None)
        else:
            user: User = self._get_and_check_login_user(requesting_user_id)
            if user is None:
                return Result(False, requesting_user_id,
                              f"user id ({requesting_user_id} is not of an existing registered, and logged in user",
                              None)
            elif store_name not in user.user_state.permissions:
                return Result(False, requesting_user_id, "user is not a staff member in that store", None)
            else:
                perm: Permission = self.adding_acting_permission(store_name, user)
                return perm.remove_policy(to_remove)

    def combine_policies_for_store(self, requesting_user_id: int, store_name: str, policies_id_list: list,
                                   operator: str):
        if not (TypeChecker.check_for_non_empty_strings([store_name]) and
                TypeChecker.check_for_positive_number([requesting_user_id])):
            return Result(False, requesting_user_id if type(requesting_user_id) == int else -1, "wrong types", None)
        else:
            user: User = self._get_and_check_login_user(requesting_user_id)
            if user is None:
                return Result(False, requesting_user_id,
                              f"user id ({requesting_user_id} is not of an existing registered, and logged in user",
                              None)
            elif store_name not in user.user_state.permissions:
                return Result(False, requesting_user_id, "user is not a staff member in that store", None)
            else:
                perm: Permission = self.adding_acting_permission(store_name, user)
                return perm.combine_policies(policies_id_list, operator)

    def combine_discounts(self, requesting_user_id: int, store_name: str, discounts_id_list: list, operator: str):
        if not (TypeChecker.check_for_non_empty_strings([store_name]) and
                TypeChecker.check_for_positive_number([requesting_user_id])):
            return Result(False, requesting_user_id if type(requesting_user_id) == int else -1, "wrong types", None)
        else:
            user: User = self._get_and_check_login_user(requesting_user_id)
            if user is None:
                return Result(False, requesting_user_id,
                              f"user id ({requesting_user_id} is not of an existing registered, and logged in user",
                              None)
            elif store_name not in user.user_state.permissions:
                return Result(False, requesting_user_id, "user is not a staff member in that store", None)
            else:
                perm: Permission = self.adding_acting_permission(store_name, user)
                discounts_id_list = [int(i) for i in discounts_id_list]
                return perm.combine_discounts(discounts_id_list, operator)

    def fetch_policies_for_store(self, requesting_user_id: int, store_name: str):
        if not (TypeChecker.check_for_non_empty_strings([store_name]) and
                TypeChecker.check_for_positive_number([requesting_user_id])):
            return Result(False, requesting_user_id if type(requesting_user_id) == int else -1, "wrong types", None)
        else:
            user: User = self._get_and_check_login_user(requesting_user_id)
            if user is None:
                return Result(False, requesting_user_id,
                              f"user id ({requesting_user_id} is not of an existing registered, and logged in user",
                              None)
            elif store_name not in user.user_state.permissions:
                return Result(False, requesting_user_id, "user is not a staff member in that store", None)
            else:
                perm: Permission = self.adding_acting_permission(store_name, user)
                return perm.fetch_policies()

    def add_simple_product_discount(self, user_id: int, store_name: str, end_time: datetime, discount_percent: float,
                                    discounted_product: str,
                                    size_of_basket_cond: int = None,
                                    over_all_price_category_cond: list = None,
                                    over_all_price_product_cond: list = None, product_list_cond: list = None,
                                    overall_category_quantity: list = None, discount_id: int = -1):
        """
        adding simple product discount, according to given conditions, if possible
        :param user_id: (int) user id of the requesting user
        :param store_name(str) name of the store
        :param end_time: the expiration date of the discount
        :param discount_percent: the discount percent to deduce from the price of the product
        :param discounted_product: name of the product to give discount to
        :param size_of_basket_cond: optional condition on the minimum size of the baskets
        :param over_all_price_category_cond: optional condition on the price payed on certain categories
        :param over_all_price_product_cond: optional condition on the price
        :param product_list_cond: optional condition on minimum quantity of each given product in the list
        :param overall_category_quantity: optional condition on
        :return: Result with info on process
        """
        if not (TypeChecker.check_for_non_empty_strings([store_name]) and TypeChecker.check_for_positive_number(
                [user_id])):
            return Result(False, user_id if type(user_id) == int else -1, "wrong types", None)
        elif discount_percent == 0 or discount_percent == 0.0 or discount_percent >= 100:
            return Result(False, user_id, "discount percent cannot be equal or greater than 100, or zero", None)
        else:
            user: User = self._get_and_check_login_user(user_id)
            if user is None:
                return Result(False, user_id,
                              f"user id ({user_id} is not of an existing registered, and logged in user",
                              None)
            elif store_name not in user.user_state.permissions:
                return Result(False, user_id, "user is not a staff member in that store", None)
            else:
                perm: Permission = self.adding_acting_permission(store_name, user)
                return perm.add_simple_product_discount(end_time, discount_percent, discounted_product,
                                                        size_of_basket_cond,
                                                        over_all_price_category_cond,
                                                        over_all_price_product_cond, product_list_cond,
                                                        overall_category_quantity, discount_id)

    def add_free_per_x_product_discount_discount(self, user_id: int, store_name: str, end_time: datetime,
                                                 product_name: str, free_amount: int,
                                                 per_x_amount: int, is_duplicate: bool = True,
                                                 size_of_basket_cond: int = None,
                                                 over_all_price_category_cond: list = None,
                                                 over_all_price_product_cond: list = None,
                                                 product_list_cond: list = None,
                                                 overall_category_quantity: list = None, discount_id: int = -1):
        """
        adding Free Per X kind of discount on a given product, if possible
        :param user_id: (int) user id of the requesting user
        :param store_name(str) name of the store
        :param end_time: (datetime) the expiration date of the discount
        :param product_name: name of the product to do discount on
        :param free_amount: (int)number of items to get free on each x items you bought
        :param per_x_amount:(int) number of items to buy to get the free ones
        :param is_duplicate:(bool) is to perform this discount until there are no more of the given product, or just 1 time (default True)
        :param size_of_basket_cond: optional condition on the minimum size of the baskets
        :param over_all_price_category_cond: optional condition on the price payed on certain categories
        :param over_all_price_product_cond: optional condition on the price
        :param product_list_cond: optional condition on minimum quantity of each given product in the list
        :param overall_category_quantity: optional condition on amount of products in each category
        :return: Result with info on process
        """
        if not (TypeChecker.check_for_non_empty_strings([store_name]) and TypeChecker.check_for_positive_number(
                [user_id])):
            return Result(False, user_id if type(user_id) == int else -1, "wrong types", None)
        else:
            user: User = self._get_and_check_login_user(user_id)
            if user is None:
                return Result(False, user_id,
                              f"user id ({user_id} is not of an existing registered, and logged in user",
                              None)
            elif store_name not in user.user_state.permissions:
                return Result(False, user_id, "user is not a staff member in that store", None)
            else:
                perm: Permission = self.adding_acting_permission(store_name, user)
                return perm.add_free_per_x_product_discount_discount(end_time, product_name, free_amount,
                                                                     per_x_amount,
                                                                     is_duplicate,
                                                                     size_of_basket_cond,
                                                                     over_all_price_category_cond,
                                                                     over_all_price_product_cond,
                                                                     product_list_cond,
                                                                     overall_category_quantity, discount_id)

    def add_simple_category_discount(self, user_id: int, store_name: str, end_time: datetime, discount_percent: float,
                                     discounted_category: str,
                                     size_of_basket_cond: int = None,
                                     over_all_price_category_cond: list = None,
                                     over_all_price_product_cond: list = None, product_list_cond: list = None,
                                     overall_category_quantity: list = None, discount_id: int = -1):
        """
        adding simple category discount, according to given conditions, if possible
        :param user_id: (int) user id of the requesting user
        :param store_name(str) name of the store
        :param end_time: the expiration date of the discount
        :param discount_percent: the discount percent to deduce from the price of the product
        :param discounted_category: name of the category to give discount to
        :param size_of_basket_cond: optional condition on the minimum size of the baskets
        :param over_all_price_category_cond: optional condition on the price payed on certain categories
        :param over_all_price_product_cond: optional condition on the price
        :param product_list_cond: optional condition on minimum quantity of each given product in the list
        :param overall_category_quantity: optional condition on
        :return: Result with info on process
        """
        if not (TypeChecker.check_for_non_empty_strings([store_name]) and TypeChecker.check_for_positive_number(
                [user_id])):
            return Result(False, user_id if type(user_id) == int else -1, "wrong types", None)
        elif discount_percent == 0 or discount_percent == 0.0 or discount_percent >= 100:
            return Result(False, user_id, "discount percent cannot be equal or greater than 100, or zero", None)
        else:
            user: User = self._get_and_check_login_user(user_id)
            if user is None:
                return Result(False, user_id,
                              f"user id ({user_id} is not of an existing registered, and logged in user",
                              None)
            elif store_name not in user.user_state.permissions:
                return Result(False, user_id, "user is not a staff member in that store", None)
            else:
                perm: Permission = self.adding_acting_permission(store_name, user)
                return perm.add_simple_category_discount(end_time, discount_percent, discounted_category,
                                                         size_of_basket_cond,
                                                         over_all_price_category_cond,
                                                         over_all_price_product_cond, product_list_cond,
                                                         overall_category_quantity, discount_id)

    def add_free_per_x_category_discount(self, user_id: int, store_name: str, end_time: datetime,
                                         category_name: str, free_amount: int,
                                         per_x_amount: int, is_duplicate: bool = True,
                                         size_of_basket_cond: int = None,
                                         over_all_price_category_cond: list = None,
                                         over_all_price_product_cond: list = None,
                                         product_list_cond: list = None,
                                         overall_category_quantity: list = None, discount_id: int = -1):
        """
        adding Free Per X kind of discount on a given category, if possible
        :param user_id: (int) user id of the requesting user
        :param store_name(str) name of the store
        :param end_time: (datetime) the expiration date of the discount
        :param category_name: name of the category to do discount on
        :param free_amount: (int)number of items to get free on each x items you bought
        :param per_x_amount:(int) number of items to buy to get the free ones
        :param is_duplicate:(bool) is to perform this discount until there are no more of the given product, or just 1 time (default True)
        :param size_of_basket_cond: optional condition on the minimum size of the baskets
        :param over_all_price_category_cond: optional condition on the price payed on certain categories
        :param over_all_price_product_cond: optional condition on the price
        :param product_list_cond: optional condition on minimum quantity of each given product in the list
        :param overall_category_quantity: optional condition on amount of products in each category
        :return: Result with info on process
        """
        if not (TypeChecker.check_for_non_empty_strings([store_name]) and TypeChecker.check_for_positive_number(
                [user_id])):
            return Result(False, user_id if type(user_id) == int else -1, "wrong types", None)
        else:
            user: User = self._get_and_check_login_user(user_id)
            if user is None:
                return Result(False, user_id,
                              f"user id ({user_id} is not of an existing registered, and logged in user",
                              None)
            elif store_name not in user.user_state.permissions:
                return Result(False, user_id, "user is not a staff member in that store", None)
            else:
                perm: Permission = self.adding_acting_permission(store_name, user)
                return perm.add_free_per_x_category_discount(end_time, category_name, free_amount,
                                                             per_x_amount,
                                                             is_duplicate,
                                                             size_of_basket_cond,
                                                             over_all_price_category_cond,
                                                             over_all_price_product_cond,
                                                             product_list_cond,
                                                             overall_category_quantity, discount_id)

    def add_basket_discount(self, user_id: int, store_name: str, end_time: datetime, discount_percent: float,
                            size_of_basket_cond: int = None,
                            over_all_price_category_cond: list = None,
                            over_all_price_product_cond: list = None, product_list_cond: list = None,
                            overall_category_quantity: list = None, discount_id: int = -1):
        """
        add discount to the entire basket
        :param user_id: (int) user id of the requesting user
        :param store_name(str) name of the store
         :param end_time: the expiration date of the discount
        :param discount_percent: the discount percent to deduce from the price of the product
        :param size_of_basket_cond: optional condition on the minimum size of the baskets
        :param over_all_price_category_cond: optional condition on the price payed on certain categories
        :param over_all_price_product_cond: optional condition on the price
        :param product_list_cond: optional condition on minimum quantity of each given product in the list
        :param overall_category_quantity: optional condition on category quantity
        :param discount_id: optional discount
        :return: Result with info on process
        """
        if not (TypeChecker.check_for_non_empty_strings([store_name]) and TypeChecker.check_for_positive_number(
                [user_id])):
            return Result(False, user_id if type(user_id) == int else -1, "wrong types", None)
        else:
            user: User = self._get_and_check_login_user(user_id)
            if user is None:
                return Result(False, user_id,
                              f"user id ({user_id} is not of an existing registered, and logged in user",
                              None)
            elif store_name not in user.user_state.permissions:
                return Result(False, user_id, "user is not a staff member in that store", None)
            else:
                perm: Permission = self.adding_acting_permission(store_name, user)
                return perm.add_basket_discount(end_time, discount_percent,
                                                size_of_basket_cond,
                                                over_all_price_category_cond,
                                                over_all_price_product_cond, product_list_cond,
                                                overall_category_quantity, discount_id)

    def get_all_discount_in_store(self, user_id: int, store_name: str):
        """
        get all discounts of store
        :param user_id: if of requesting user
        :param store_name: name of the store
        :return: collection of discounts id to descriptions
        """
        if not (TypeChecker.check_for_non_empty_strings([store_name]) and TypeChecker.check_for_positive_number(
                [user_id])):
            return Result(False, user_id if type(user_id) == int else -1, "wrong types", None)
        else:
            user: User = self._get_and_check_login_user(user_id)
            if user is None:
                return Result(False, user_id,
                              f"user id ({user_id} is not of an existing registered, and logged in user",
                              None)
            elif store_name not in user.user_state.permissions:
                return Result(False, user_id, "user is not a staff member in that store", None)
            else:
                perm: Permission = self.adding_acting_permission(store_name, user)
                return perm.get_all_discount()

    def remove_discount(self, user_id: int, store_name: str, discount_id: int):
        """
        removing given discount from
        :param user_id: (int) id of the user
        :param store_name: (str) name of the store
        :param discount_id: (int) id of the discount
        :return: Result with info on process
        """
        if not (TypeChecker.check_for_non_empty_strings([store_name]) and TypeChecker.check_for_positive_number(
                [user_id])):
            return Result(False, user_id if type(user_id) == int else -1, "wrong types", None)
        else:
            user: User = self._get_and_check_login_user(user_id)
            if user is None:
                return Result(False, user_id,
                              f"user id ({user_id} is not of an existing registered, and logged in user",
                              None)
            elif store_name not in user.user_state.permissions:
                return Result(False, user_id, "user is not a staff member in that store", None)
            else:
                perm = self.adding_acting_permission(store_name, user)

                return perm.remove_discount(discount_id)


class ShoppingHandler:
    """
        Class for actions regarding shopping interface
        """

    _dal: DAL = DAL.get_instance()

    def __init__(self, data_handler: DataHandler, payment_system: _PaymentSystem, shipping_system: _ShippingSystem):
        self._data_handler: DataHandler = data_handler
        self._payment_system = payment_system
        self._shipping_system = shipping_system
        # self._log: Logger = Log.get_instance().get_logger()
        if not self._payment_system.check_connection():
            # doesn't have connection toto supply system - close system immidiatly
            raise SystemExit("lost connection to PaymentSystem system")
        if not self._shipping_system.check_connection():
            raise SystemExit("lost connection to Shipping System")

    def _check_and_handle_new_user(self, user_id):
        if user_id <= 0:
            # creating user and save it to the database
            new_user: User = User.create_new_user_for_guest(user_id)
            user_id = new_user.user_id
            self._data_handler.add_or_update_user(user_id, new_user)
        return user_id

    def _get_user_or_create_one(self, user_id):
        user_id = self._check_and_handle_new_user(user_id)

        # user: User = getUserfrom LIU
        # if user == None:
        return self._data_handler.get_user_by_id(user_id)

    # 2.4.1
    def watch_info_on_store(self, username: str, store_name: str):
        """
            :param user_id: (int) id of requesting user
            :param store_name: (str) name of the store
            :return: Result with info on the process
        """
        # user_id = self._check_and_handle_new_user(user_id)
        return self._data_handler.get_store_by_name_as_dictionary(username, store_name)

    # 2.4.2
    def watch_info_on_product(self, user_id: int, product_name: str, store_name: str):
        """
        watch info on a given product
        :param user_id: (int) id of the user
        :param product_name: (str) name of the product
        :param store_name: (str) name of the store
        :return: Result with info on process. if successful, the product info will be in data field of result
        """
        if not TypeChecker.check_for_non_empty_strings([product_name, store_name]) or type(user_id) != int:
            return Result(False, user_id if type(user_id) == int else -1, "wrong types", None)
        # user_id = self._check_and_handle_new_user(user_id)

        res_store: Result = self._data_handler.get_store_by_name(store_name)
        if not res_store.succeed:
            return res_store
        else:
            store: Store = res_store.data
            product: ProductInInventory = store.inventory[product_name] if product_name in store.inventory else None
            if product is None:
                return Result(False, user_id, "requested product was not found in store", None)
            else:
                return Result(True, user_id, 'found product', product.to_dictionary())

    def search_stores(self, user_id: int, store_search_name: str):
        """
        searching all stores that contains the given name
        :param user_id:(int) user searching
        :param store_search_name:(str) name to search
        :return: all the stores that contains this prefix as dictionaries
        """
        if type(user_id) != int:
            return Result(False, -1, "wrong type input", None)
        # user_id = self._check_and_handle_new_user(user_id)
        data = self._data_handler.get_store_that_contains_name(store_search_name)
        # get store as dictionary, if store name contain the store_search_name
        matched_stores = [s.to_dictionary() for s in data] if data is not None else []
        return Result(True, user_id, "store search result", matched_stores)

    # 2.5
    def search_products(self, user_id: int, product_name: str, stores_names: TypedList = None,
                        categories: TypedList = None,
                        brands: TypedList = None, min_price: float = None, max_price: float = None):
        """
            search products by different criteria
            :param user_id: (int) id of the requesting user
            :param product_name:(str) name of the product / key word to search by
            :param stores_names: (TypedList of str) list of store name to search by
            :param categories: (TypedList of str) list of categories to search by
            :param brands: (TypedList of str) list of brands to search by
            :param min_price:(float) minimum price to search by
            :param max_price: (float)
            :return: TypeList of Products
            """
        from src.domain.system.store_classes import Store
        if not (type(user_id) == int and TypeChecker.check_for_non_empty_strings([product_name])):
            return Result(False, user_id if type(user_id) == int else -1, "invalid id or product name", None)
        # user_id = self._check_and_handle_new_user(user_id)
        if stores_names is None:
            stores_names = TypedList(Store)
        # list_of_stores: Result = self._data_handler.get_stores_by_names(stores_names)
        list_of_stores = self._data_handler.get_stores_according_to_list(stores_names)
        # if list_of_stores:
        #     return Result(True, user_id, "search result", TypedList(dict))
        # else:
        search_result = TypedList(dict)
        if list_of_stores is None:
            return Result(True, user_id, "search result", {})
        for store in list_of_stores:
            store: Store = store
            search_result.extend(store.search_product(product_name, categories, brands, min_price, max_price))
        return Result(True, user_id, "search result", search_result)

    def display_products_in_shopping_cart(self, user_id: int):
        """
            :param user_id: input user id of user
            :return: string that includes of the information of products in cart.
            """
        if type(user_id) != int:
            return Result(False, user_id if type(user_id) == int else -1, "wrong types", None)
        user: User = self._get_user_or_create_one(user_id)
        if user is None:
            return Result(False, -1, f'user does not exists: {user_id}', None)
        shopping_cart: ShoppingCart = user.shopping_cart
        # self._dal.add(shopping_cart, add_only=True)
        shopping_cart.calc_updated_price_of_all_baskets()
        if shopping_cart.is_empty():
            return Result(True, user.user_id, "empty cart", "your cart is Empty")
        else:
            return Result(True, user.user_id, "shopping cart ready", shopping_cart.to_dictionary())

    def saving_product_to_shopping_cart(self, product_name: str, store_name: str, user_id: int,
                                        quantity: int):
        """
            saving the given product in shopping cart
            :param product_name: (str) name of the desired product
            :param store_name: (str) name of the store that have the product
            :param user_id: (str) user id of the user who wants to add the item
            :param quantity: (int) quantity of the product
            :return: Result obj: True,empty message if succeeded, otherwise: False, indicative messages about
                        the errors.
            """
        if not TypeChecker.check_for_non_empty_strings([product_name, store_name]) or type(user_id) != int or \
                not TypeChecker.check_for_positive_number([quantity]):
            return Result(False, user_id if type(user_id) == int else -1, "wrong types", None)
        if quantity <= 0:
            return Result(False, user_id, "quantity value can't be zero or negative", None)

        user: User = self._get_user_or_create_one(user_id)
        if user is None:
            return Result(False, -1, f'user does not exists: {user_id}', None)
        if user.user_state:
            self._dal.add(user.user_state, add_only=True)
        store_result: Result = self._data_handler.get_store_by_name(store_name)
        if not store_result.succeed:
            return Result(False, user.user_id, "wanted store does not exists", None)
        else:
            # self._dal.add(user.shopping_cart, add_only=True)

            res: Result = user.shopping_cart.add_product(store_result.data, product_name, quantity,
                                                         user.user_state.user_name if user.user_state else str(
                                                             user.user_id))
            # user.update_shopping_cart()  # TODO: how did that?
            return Result(res.succeed, user.user_id, res.msg, res.data)

    def removing_item_from_shopping_cart(self, product_name: str, store_name: str, user_id: int):
        """
            removing a given item from shopping item
            :param product_name: (str) name of product to remove
            :param store_name: (str) name of store
            :param user_id: (int) id of the user that want to remove the product
            :return: Result with True, empty message if Succeeded, Result with False, error message otherwise
            """
        if not TypeChecker.check_for_non_empty_strings([product_name, store_name]) or type(user_id) != int:
            return Result(False, user_id if type(user_id) == int else -1, "wrong types", None)
        user: User = self._get_user_or_create_one(user_id)
        if user is None:
            return Result(False, -1, f'user does not exists: {user_id}', None)
        res: Result = user.shopping_cart.remove_product(store_name, product_name)
        return Result(res.succeed, user.user_id, res.msg, res.data)

    def editing_quantity_shopping_cart_item(self, product_name: str, store_name: str,
                                            user_id: int, new_quantity: int):
        """
        editing quantity of item in shopping cart
        :param product_name: (str) product name to edit
        :param store_name: (str) store name where the product belong
        :param user_id: (int) user id of the user that want to edit the quantity
        :param new_quantity:(int) new quantity of the product
        :return: True if succeeded , False otherwise
        """
        if not TypeChecker.check_for_non_empty_strings([product_name, store_name]) or type(user_id) != int or \
                not TypeChecker.check_for_positive_number([new_quantity]):
            return Result(False, user_id if type(user_id) == int else -1, "wrong types", None)
        if new_quantity == 0:
            return self.removing_item_from_shopping_cart(product_name, store_name, user_id)
        user: User = self._get_user_or_create_one(user_id)
        if user is None:
            return Result(False, -1, f'user does not exists: {user_id}', None)
        # self._dal.add(user.shopping_cart, add_only=True)
        res: Result = user.shopping_cart.edit_product(store_name, product_name, new_quantity)
        return Result(res.succeed, user.user_id, res.msg, res.data)

        # result = self._data_handler.get_shopping_cart(user_id)
        # if not result.succeed:
        #     return result
        #
        # shopping_cart = result.data
        # # check if product exist in shopping cart
        # if store_name not in shopping_cart:
        #     return Result(False, user_id, "store basket wasn't found in shopping cart", None)
        # elif product_name not in shopping_cart[store_name]:
        #     return Result(False, user_id, "product wasn't found in shopping cart", None)
        # return self.saving_product_to_shopping_cart(product_name, store_name, user_id, new_quantity)

    def make_purchase_of_all_shopping_cart(self, user_id: int, credit_card_number: int, country: str, city: str,
                                           street: str, house_number: int, expiry_date: str, ccv: str, holder: str,
                                           holder_id: str,
                                           apartment: str = "0", floor: int = 0):
        """
        purchasing all the items in the shopping cart
        :param expiry_date:
        :param user_id:(int) id of the purchasing user
        :param credit_card_number: (int) credit card number to pay with
        :param country: country to send to
        :param city: city in country to send to
        :param street: street in city to send to
        :param house_number: house number in street
        :param holder_id:
        :param holder:
        :param ccv: 3 numbers behind the credit card
        :param apartment: apartment identifier in house
        :param floor: floor of the apartment
        :return: Result object for purchasing result
        """
        if type(user_id) != int or user_id < 0:
            return Result(False, -1, "expected a valid user_id", None)
        validate_address_msg: str = self._shipping_system.check_address_details(country, city, street, house_number,
                                                                                apartment, floor)
        if validate_address_msg != "OK":
            return Result(False, -1, f"can't preform purchase: {validate_address_msg}", None)
        user: User = self._get_user_or_create_one(user_id)
        if user is None:
            return Result(False, -1, f'user does not exists: {user_id}', None)
        if user.shopping_cart.is_empty():
            return Result(False, user.user_id, "Shopping cart is empty", None)

        self._dal.begin_nested()
        try:
            res: Result = user.shopping_cart.pre_purchase()
            if not res.succeed:
                self._dal.rollback()
                return Result(False, user.user_id, res.msg, res.data)
            else:
                month_and_year = expiry_date.split('/')
                if self._payment_system.pay(str(credit_card_number), month_and_year[0], month_and_year[1], ccv, holder,
                                            holder_id):
                    self._shipping_system.ship(country, city, street, house_number, apartment, floor)
                    shopping_cart = user.shopping_cart
                    if user.user_state is not None:
                        self._dal.add(user.user_state, add_only=True)
                    purchase_report, stores_to_check = user.shopping_cart.after_purchase(user_id,
                                                                                         user.user_state.user_name if user.user_state is not None else None)
                    # Log purchase
                    # self._log.info(LogRec(purchase_report.to_dictionary()))
                    if user.user_state is not None:
                        # user.user_state.add_purchases(purchase_report.purchase_list)
                        # self._data_handler.save_purchases(purchase_report.purchase_list)
                        ret = Result(True, user.user_id, "Purchase was successful", purchase_report.to_dictionary())
                    else:
                        ret = Result(True, user.user_id, "Purchase was successful", None)
                    self._dal.commit()
                    user._shopping_cart = shopping_cart
                    for s in stores_to_check:
                        s.clear_empty_products_from_inventory()
                    return ret
                else:
                    self._dal.rollback()
                    return Result(False, user.user_id, "Payment failed", None)
        except Exception as e:
            self._dal.rollback()
            return Result(False, user.user_id, f"Purchase failed, Rollback made ({str(e)})")

    def watch_user_purchases(self, requesting_user_id: int, requested_user: str = None):
        """
            Returns specific user purchases history
            :param requesting_user_id: The user who requests this view(some manager or the user itself)
            :param requested_user: The user, that his/she purchases is requested
            :return: Result object containing a list of requested purchases
            """
        user: User = self._get_user_or_create_one(requesting_user_id)
        if user is None:
            return Result(False, -1, f'requesting user does not exists: {requesting_user_id}', None)
        elif requested_user is None or requested_user == "":
            if user.user_state is None:
                return Result(False, requesting_user_id, "only registered users have purchase history in the store", [])
            else:
                self._dal.add(user.user_state, add_only=True)
                return Result(True, user.user_id, "purchase results:", user.user_state.view_all_purchases())
        self._dal.add(user.user_state, add_only=True)
        if user.is_admin():
            wanted_user: LoggedInUser = self._data_handler.get_user_by_username(requested_user)
            self._dal.add(wanted_user, add_only=True)
            if wanted_user is None:
                return Result(False, -1, f'wanted user does not exists: {requested_user}', None)

            else:
                return Result(True, user.user_id, "purchase results:", wanted_user.view_all_purchases())
        else:
            return Result(False, requesting_user_id, "permission denied", None)


class Approval(enum.Enum):
    approved = 1
    declined = 2
    pending = 3

    def to_string(self):
        if self == Approval.approved:
            return "Approved"
        elif self == Approval.declined:
            return "Declined"
        else:
            return "Pending"


class AppointmentAgreement(db.Model):
    """
    Object with current store owners of the store and their answer ab_new_candidate_fkout the new appointment
    """
    __tablename__ = 'appointment_agreement'
    id = db.Column(db.Integer, primary_key=True)

    _dal: DAL = DAL.get_instance()
    _active = db.Column(db.Boolean)

    _candidate_fk = db.Column(db.String(50), db.ForeignKey('loggedInUsers._user_name'))
    _candidate = db.relationship("LoggedInUser", lazy="joined", foreign_keys=[_candidate_fk])

    _proposer_fk = db.Column(db.String(50), db.ForeignKey('loggedInUsers._user_name'))
    _proposer = db.relationship("LoggedInUser", lazy="joined", foreign_keys=[_proposer_fk])

    _store_fk = db.Column(db.String(50), db.ForeignKey('store._name'))
    _store = db.relationship("Store", lazy="joined")

    _approval_dict_db_dict = db.Column(db.JSON)

    def __init__(self, store: Store, new_candidate: LoggedInUser, new_proposer: LoggedInUser):
        self._active = True
        self._candidate_fk = new_candidate.user_name
        self._proposer_fk = new_proposer.user_name
        self._proposer = new_proposer
        self._candidate = new_candidate
        self._store_fk = store._name
        self._store = store
        self._log: Logger = Log.get_instance().get_logger()

        permissions = list(store.get_permissions().values())
        permissions_filtered = list(filter(lambda perm: perm.role == Role.store_owner.value
                                                        or perm.role == Role.store_initial_owner.value, permissions))
        owners = list(map(lambda perm: perm.user._user_name, permissions_filtered))
        self._approval_dict = TypedDict(str, Approval)
        for owner in owners:
            if owner != self._proposer_fk:
                self.approval_dict[owner] = Approval.pending
                Publisher.get_instance().publish('store_update', f"Date: {datetime.today()}: New Owner candidacy pending your approval.\n"
                                                                 f"Store {store._name}, User: {new_candidate.user_name}",
                                                 owner)
        self._approval_dict_db_dict = json.dumps({u: v.value for (u, v) in self._approval_dict.items()})

    @orm.reconstructor
    def loaded(self):
        self._approval_dict = TypedDict(str, Approval)
        for username, approval_enum_val in json.loads(self._approval_dict_db_dict).items():
            self._approval_dict[username] = Approval(approval_enum_val)

    @property
    def candidate(self):
        return self._candidate

    @property
    def proposer(self):
        return self._proposer

    @property
    def store_name(self):
        return self._store_fk

    @property
    def approval_dict(self):
        return self._approval_dict

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self._active = value

    def respond(self, responder_username: str, approval: enum, store_admin, pid):
        self.approval_dict[responder_username] = approval
        if approval == Approval.declined:
            self.decline_proposal()
            self._approval_dict_db_dict = json.dumps({u: v.value for (u, v) in self._approval_dict.items()})
            return
        for response in self.approval_dict.values():
            if response == Approval.pending:
                self._approval_dict_db_dict = json.dumps({u: v.value for (u, v) in self._approval_dict.items()})
                return
        self._approval_dict_db_dict = json.dumps({u: v.value for (u, v) in self._approval_dict.items()})
        self.approve_proposal(store_admin, pid)

    def decline_proposal(self):
        self.active = False

    def approve_proposal(self, store_admin, pid):
        permission: Permission = self.proposer.permissions[self.store_name]
        self._dal.add(permission, add_only=True)
        self.active = False
        u: LoggedInUser = self._dal.get_user_by_name(self._proposer_fk)
        self._dal.add(u, add_only=True)
        # store_admin.adding_new_owner_to_store(u.user_id, self._candidate_fk, self.store_name)
        # __add_or_remove_member
        res: Result = permission.add_store_owner(self._dal.get_user_by_name(self._candidate.user_name))
        if res.succeed:
            from src.domain.system.data_handler import DataHandler
            d_handler: DataHandler = DataHandler.get_instance()
            d_handler.update_stats_counter_for_user(1, u.user_name, 3)
