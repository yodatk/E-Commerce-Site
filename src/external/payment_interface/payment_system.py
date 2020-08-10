import requests


class _PaymentSystem:
    """
    Interface of Payment System.
    """

    def pay(self, card_number: str, month: str, year: str, holder: str, ccv: str, holder_id: str):
        """
        Attempt to pay with parameters.
        :param: card_number, amount
        :return: Whether card holder has enough to pay amount.
        """
        pass

    def cancel_pay(self, transaction_id: str):
        """
        Attempt to cancel payment associated with transaction id
        :param transaction_id: ID of payment trying to cancel
        :return: Whether successful
        """
        pass

    def check_connection(self):
        """
        check that the connection is valid
        :return:
        """
        pass


class RealPaymentSystem(_PaymentSystem):
    """
    Actual implementation of Payment System.
    """

    url = "https://cs-bgu-wsep.herokuapp.com/"

    def __init__(self):
        pass

    def pay(self, card_number: str, month: str, year: str, holder: str, ccv: str, holder_id: str):
        """
        Attempt to pay with parameters.
        :param: card_number, amount
        :return: Whether card holder has enough to pay amount.
        """
        if not self.check_connection():
            return False

        post_content = {
            "action_type": "pay",
            "card_number": card_number,
            "month": month,
            "year": year,
            "holder": holder,
            "ccv": ccv,
            "id": holder_id
        }
        response = requests.post(self.url, data=post_content)
        transaction_id = response.text
        if transaction_id == "-1":
            return False
        else:
            return transaction_id

    def cancel_pay(self, transaction_id: str):
        """
        Attempt to cancel payment associated with transaction id
        :param transaction_id: ID of payment trying to cancel
        :return: Whether successful
        """
        post_content = {
            "action_type": "cancel_pay",
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


class MockPaymentSystem(_PaymentSystem):
    """
    Temporary fake implementation of Payment System.
    """

    # Class attribute: dictionary of <product name, number of products available>
    accounts = {"1234123412341234": 2000000.0, "1111111111111111": 200000.0, "2222222222222222": 30000000.0,
                "3333333333333333": 4000000.0, "4444444444444444": 5000000.0}

    def cancel_pay(self, transaction_id: str):
        """
        Attempt to cancel payment associated with transaction id
        :param transaction_id: ID of payment trying to cancel
        :return: Whether successful
        """
        pass

    def pay(self, card_number: str, month: str, year: str, holder: str, ccv: str, holder_id: str):
        """
        Attempt to pay with parameters.
        :param: card_number, amount
        :return: Whether card holder has enough to pay amount.
        """
        # if amount < 0:
        #     return False
        if self.__check_payment_method(card_number):
            # return self.__charge(card_number, amount)
            return True
        else:
            return False

    @staticmethod
    def __check_payment_method(card_number: str):
        """
        check if card number is legit. This is a private method
        :param: card_number
        :return: Bool.
        """
        return len(str(card_number)) == 16

    def __charge(self, card_number: str, amount: float):
        """
        Charge account with amount. This is a private method.
        pre-condition: card_number exists in accounts.
        :param: card_number, amount
        :return: Bool.
        """
        if card_number not in self.accounts:
            return False
        elif self.accounts[card_number] - amount >= 0:
            self.accounts[card_number] -= amount
            return True
        else:
            return False

    def check_connection(self):
        return True

    def add_account(self, card_number: str, amount: float):
        if card_number in self.accounts:
            print("Account already exist!")
        else:
            self.accounts[card_number] = amount
