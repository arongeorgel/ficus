import os
import traceback
from datetime import datetime
from typing import List, Dict

from metaapi_cloud_sdk import SynchronizationListener
from metaapi_cloud_sdk.metaapi.streaming_metaapi_connection_instance import StreamingMetaApiConnectionInstance

from ficus.mt5.MetatraderStorage import MetatraderSymbolPriceManager
from ficus.mt5.TradingManager import TradingManager, FicusTrade
from ficus.mt5.listeners.BitcoinSyncListener import BitcoinSyncListener
from ficus.mt5.listeners.ITradingCallback import ITradingCallback
from ficus.mt5.models import TradingSymbol, TradeDirection


class VantageSim(ITradingCallback):

    __sync_listener: SynchronizationListener
    __price_managers: Dict[TradingSymbol, MetatraderSymbolPriceManager]

    def __init__(self):
        self.__price_managers = {}
        self.__trade_manager = TradingManager(self)

    async def connect_account(self):
        pass

    async def prepare_listeners(self, symbols_to_subscribe: List[TradingSymbol]):
        try:
            for symbol in symbols_to_subscribe:
                timestamp = datetime.now().strftime("%Y_%m_%d")
                file_name = f"meta_symbol_{symbol.name.lower()}_{timestamp}.json"
                file_name_copy = f"meta_symbol_{symbol.name.lower()}_{timestamp}_copy.json"

                # first copy the file
                os.system(f"cp {file_name} {file_name_copy}")
                manager = MetatraderSymbolPriceManager(file_name_copy)
                self.__price_managers[symbol] = manager
                # delete it after

                os.system(f'rm {file_name_copy}')

            self.__sync_listener = BitcoinSyncListener(self.__price_managers, self.__trade_manager)

        except Exception as ex:
            print(''.join(traceback.TracebackException.from_exception(ex).format()))

    async def disconnect(self, symbols_to_unsubscribe: List[TradingSymbol]):
        pass

    def get_ohlcv_for_symbol(self, symbol):
        price_manager = self.__price_managers[symbol]
        return price_manager.generate_ohlcv(1)

    async def open_trade(self, symbol: TradingSymbol, direction: TradeDirection, volume: float):
        pass

    async def close_trade(self, trade: FicusTrade, trading_symbol):
        pass

    async def on_ohlcv(self, last_ohlcv, symbol):
        pass
