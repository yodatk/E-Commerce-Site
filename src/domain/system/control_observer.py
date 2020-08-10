from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from random import randrange
from typing import List


class DBStatus(Enum):
    DBDown = 1
    DBUp = 2

class Subject(ABC):
    """
    The Subject interface declares a set of methods for managing subscribers.
    """

    @abstractmethod
    def attach(self, observer: Observer) -> None:
        """
        Attach an observer to the subject.
        """
        pass

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        """
        Detach an observer from the subject.
        """
        pass

    @abstractmethod
    def notify(self, msg: DBStatus) -> None:
        """
        Notify all observers about an event.
        """
        pass


class DalStatus(Subject):
    """
    The Subject owns some important state and notifies observers when the state
    changes.
    """

    _state: int = None
    """
    For the sake of simplicity, the Subject's state, essential to all
    subscribers, is stored in this variable.
    """

    _observers: List[Observer] = []
    """
    List of subscribers. In real life, the list of subscribers can be stored
    more comprehensively (categorized by event type, etc.).
    """

    def attach(self, observer: Observer) -> None:
        print("Subject: Attached an observer.")
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    """
    The subscription management methods.
    """

    def notify(self, msg) -> None:
        """
        Trigger an update in each subscriber.
        """

        for observer in self._observers:
            observer.update(msg)


class Observer(ABC):
    """
    The Observer interface declares the update method, used by subjects.
    """

    @abstractmethod
    def __init__(self, fun: callable(DBStatus)):
        pass

    @abstractmethod
    def update(self, msg: DBStatus) -> None:
        """
        Receive update from subject.
        """
        pass


class AppServer(Observer):
    def __init__(self, fun: callable(DBStatus)):
        super().__init__(fun)
        self.fun = fun

    def update(self, msg: DBStatus) -> None:
        self.fun(msg)