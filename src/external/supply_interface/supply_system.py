import requests

from src.protocol_classes.classes_utils import TypeChecker


class _ShippingSystem:
    """
    Interface of Supply System.
    """

    def supply(self, name: str, address: str, city: str, country: str, zip_code: str):
        """
        ship a purchase to the customer given address
        :param name: customer name
        :param address: customer address
        :param city: city to ship to
        :param country: country to ship to
        :param zip_code: customer zip code
        :return: str with info message on process
        """

    def cancel_supply(self, transaction_id: str):
        """
        Attempt to cancel supply associated with transaction id
        :param transaction_id: ID of supply trying to cancel
        :return: Whether successful
        """
        pass

    def check_connection(self):
        """
        check that there is a connection with the supply system
        :return: True if connection is valid, false other wise
        """


class RealShippingSystem(_ShippingSystem):
    """
    Actual implementation of supply system.
    """
    url = "https://cs-bgu-wsep.herokuapp.com/"

    def supply(self, name: str, address: str, city: str, country: str, zip_code: str):
        """
        ship a purchase to the customer given address
        :param name: customer name
        :param address: customer address
        :param city: city to ship to
        :param country: country to ship to
        :param zip_code: customer zip code
        :return: str with info message on process
        """
        if not self.check_connection():
            return False

        post_content = {
            "action_type": "supply",
            "name": name,
            "address": address,
            "city": city,
            "country": country,
            "zip": zip_code
        }
        response = requests.post(self.url, data=post_content)
        transaction_id = response.text
        if transaction_id == "-1":
            return False
        else:
            return transaction_id

    def cancel_supply(self, transaction_id: str):
        """
        Attempt to cancel supply associated with transaction id
        :param transaction_id: ID of supply trying to cancel
        :return: Whether successful
        """
        post_content = {
            "action_type": "cancel_supply",
            "transaction_id": transaction_id
        }
        response = requests.post(self.url, data=post_content)
        if response.text == "1":
            return True
        else:
            return False

    def check_connection(self):
        post_content = {
            "action_type": "handshake"
        }
        response = requests.post(url=self.url, data=post_content)
        if response.text == "OK":
            return True
        else:
            return False


class MockShippingSystem(_ShippingSystem):
    VALID_COUNTRIES = {"USA", "China", "Israel", "Russia"}

    def ship(self, country: str, city: str, street: str, house_number: int, apartment: str = "0",
             floor: int = 0):
        """
        ship a purchase to the customer given address
        :param country: country to ship to
        :param city: city to ship to
        :param street: street in the city to ship to
        :param house_number: house number at that street
        :param apartment: apartment identifier if there is one
        :param floor: floor of the apartment
        :return: str with info message on process
        """
        output: str = self.check_address_details(country, city, street, house_number, apartment, floor)
        return output

    def check_connection(self):
        """
        check that there is a connection with the supply system
        :return: True if connection is valid, false other wise
        """
        return True

    def check_address_details(self, country: str, city: str, street: str, house_number: int, apartment: str = "0",
                              floor: int = 0):
        """
        ship a purchase to the customer given address
        :param country: country to ship to
        :param city: city to ship to
        :param street: street in the city to ship to
        :param house_number: house number at that street
        :param apartment: apartment identifier if there is one
        :param floor: floor of the apartment
        :return: str with info message on process
        """
        if not TypeChecker.check_for_non_empty_strings(
                [country, city, street, apartment]) or not TypeChecker.check_for_positive_ints([house_number]):
            return "Not a Valid address"
        if country not in self.VALID_COUNTRIES:
            return "Cannot ship to Country"
        return "OK"
