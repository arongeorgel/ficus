from abc import ABC, abstractmethod


class ITradingCallback(ABC):
    @abstractmethod
    def close_trade(self):
        pass