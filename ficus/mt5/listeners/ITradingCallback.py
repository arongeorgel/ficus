from abc import ABC, abstractmethod

from ficus.mt5.models import TradingSymbol, TradeDirection, FicusTrade


class ITradingCallback(ABC):
    @abstractmethod
    async def close_trade(self, trade: FicusTrade, trading_symbol: TradingSymbol):
        pass

    @abstractmethod
    async def open_trade(self, symbol: TradingSymbol, direction: TradeDirection, volume: float):
        pass
