

class Publisher:
    __instance = None

    def __init__(self):
        self._notification_handler = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if Publisher.__instance is None:
            Publisher.__instance = Publisher()
        return Publisher.__instance

    def set_communication_handler(self, notification_handler) -> None:
        self._notification_handler = notification_handler

    def publish(self, msg_type: str, msg, user_name: str = None) -> None:
        # print(f"should send message {msg}")
        self._notification_handler.send_to_client(msg_type, msg, user_name)
