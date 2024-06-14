import os
import traceback
from datetime import datetime
from typing import List, Dict

from metaapi_cloud_sdk import SynchronizationListener
from metaapi_cloud_sdk.metaapi.models import MetatraderTradeResponse

from ficus.mt5.MetatraderStorage import MetatraderSymbolPriceManager
from ficus.mt5.TradingManager import TradingManager, FicusTrade
from ficus.mt5.listeners.MetaSynchronizationListener import MetaSynchronizationListener
from ficus.mt5.listeners.ITradingCallback import ITradingCallback
from ficus.mt5.models import TradeDirection


class VantageSim(ITradingCallback):

    async def partially_close_trade(self, trade: FicusTrade, symbol: str) -> MetatraderTradeResponse:
        pass

    async def modify_trade(self, trade: FicusTrade) -> MetatraderTradeResponse:
        pass

    __sync_listener: SynchronizationListener
    __price_managers: Dict[str, MetatraderSymbolPriceManager]

    def __init__(self):
        self.__price_managers = {}
        self.__trade_manager = TradingManager(self)

    async def connect_account(self):
        pass

    async def prepare_listeners(self, symbols_to_subscribe: List[str]):
        try:
            for symbol in symbols_to_subscribe:
                timestamp = datetime.now().strftime("%Y_%m_%d")
                file_name = f"meta_symbol_{symbol.lower()}_{timestamp}.json"
                file_name_copy = f"meta_symbol_{symbol.lower()}_{timestamp}_copy.json"

                # first copy the file
                os.system(f"cp {file_name} {file_name_copy}")
                manager = MetatraderSymbolPriceManager(symbol)
                self.__price_managers[symbol] = manager
                # delete it after

                os.system(f'rm {file_name_copy}')

            self.__sync_listener = MetaSynchronizationListener(self.__price_managers, self.__trade_manager)

        except Exception as ex:
            print(''.join(traceback.TracebackException.from_exception(ex).format()))

    async def disconnect(self, symbols_to_unsubscribe: List[str]):
        pass

    def get_ohlcv_for_symbol(self, symbol):
        price_manager = self.__price_managers[symbol]
        return price_manager.generate_ohlcv(1)

    async def open_trade(self, symbol: str, direction: TradeDirection, volume: float,
                         stop_loss: float):
        return {'positionId': '12345'}

    async def close_trade(self, trade: FicusTrade, trading_symbol):
        pass

    async def on_ohlcv(self, last_ohlcv, symbol):
        pass
