import abc


class AbstractAutoban(metaclass=abc.ABCMeta):
    """
    Declare common interface for all checkers.
    Strategy pattern
    """
    @staticmethod
    @abc.abstractmethod
    def make_complaint(url: str, quantity: int) -> tuple:
        pass
