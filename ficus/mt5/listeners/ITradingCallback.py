from abc import ABC, abstractmethod

from metaapi_cloud_sdk.metaapi.models import MetatraderTradeResponse

from ficus.mt5.models import TradingSymbol, TradeDirection, FicusTrade


class ITradingCallback(ABC):
    @abstractmethod
    async def close_trade(self, trade: FicusTrade, trading_symbol: TradingSymbol) -> MetatraderTradeResponse:
        pass

    @abstractmethod
    async def open_trade(self, symbol: TradingSymbol, direction: TradeDirection,
                         volume: float, stop_loss: float) -> MetatraderTradeResponse:
        pass

    @abstractmethod
    async def partially_close_trade(self, trade: FicusTrade, symbol: TradingSymbol) -> MetatraderTradeResponse:
        pass

    @abstractmethod
    async def modify_trade(self, trade: FicusTrade) -> MetatraderTradeResponse:
        pass
