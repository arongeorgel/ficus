import asyncio
import traceback
from typing import List, Dict

from metaapi_cloud_sdk import MetaApi, SynchronizationListener
from metaapi_cloud_sdk.metaapi.models import MetatraderTradeResponse
from metaapi_cloud_sdk.metaapi.streaming_metaapi_connection_instance import StreamingMetaApiConnectionInstance

from ficus.mt5.MetatraderStorage import MetatraderSymbolPriceManager
from ficus.mt5.TradingManager import TradingManager, FicusTrade
from ficus.mt5.listeners.ITradingCallback import ITradingCallback
from ficus.mt5.listeners.MetaSynchronizationListener import MetaSynchronizationListener
from ficus.mt5.models import TradingSymbol, TradeDirection


class Vantage(ITradingCallback):
    META_API_TOKEN = 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2MzZjN2NiNzgwNmIxMWMyNDU5MWQ3YTE4MmZmOWY2OCIsInBlcm1pc3Npb25zIjpbXSwiYWNjZXNzUnVsZXMiOlt7ImlkIjoidHJhZGluZy1hY2NvdW50LW1hbmFnZW1lbnQtYXBpIiwibWV0aG9kcyI6WyJ0cmFkaW5nLWFjY291bnQtbWFuYWdlbWVudC1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1ycGMtYXBpIiwibWV0aG9kcyI6WyJtZXRhYXBpLWFwaTp3czpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZWFsLXRpbWUtc3RyZWFtaW5nLWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6d3M6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6Im1ldGFzdGF0cy1hcGkiLCJtZXRob2RzIjpbIm1ldGFzdGF0cy1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoicmlzay1tYW5hZ2VtZW50LWFwaSIsIm1ldGhvZHMiOlsicmlzay1tYW5hZ2VtZW50LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJtdC1tYW5hZ2VyLWFwaSIsIm1ldGhvZHMiOlsibXQtbWFuYWdlci1hcGk6cmVzdDpkZWFsaW5nOio6KiIsIm10LW1hbmFnZXItYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6ImJpbGxpbmctYXBpIiwibWV0aG9kcyI6WyJiaWxsaW5nLWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19XSwidG9rZW5JZCI6IjIwMjEwMjEzIiwiaW1wZXJzb25hdGVkIjpmYWxzZSwicmVhbFVzZXJJZCI6IjYzNmM3Y2I3ODA2YjExYzI0NTkxZDdhMTgyZmY5ZjY4IiwiaWF0IjoxNzE2MjE3ODcwLCJleHAiOjE3MjM5OTM4NzB9.h8O0r_-FxYlqNp9rHF44VfN-BGwh9bXyBc7iNj1RTwi0QeVE9WN6IhpBTcUmA09y-VZ_YrAIvwk-zhrUI3X5EY9mZcGY37bmAJPOoFmNRolI6pme5XKKqjb00W3Km6uxFXXFq9Pjbxhk27D6r8AZeubbovI3rGUZZlQWgbVEqUAMHCZyPA2NmxtxKKoOVGKB4SBb2pBMiO45DFZaNN1b4Durt5HOU-my3i4ucQb1xvfQcu_ZTMeYZCP-FPd02svm0h_OpiBL-P4LCXH_-vFYHlhnv9fuuHV5Tjqj3p6KDHE5_92JgR8pVYPp1bjS6Ei5BOflPQriW03gkfoEjJlKtPJ_c2OUXqDyTAiITZMpMJi2K7Uew7cpBCPV6pL--t1At6tgMTzG3r8jBMCMyWvUk50889RPE4EQUztBJjudxAzoayBdIx9rYJgGuoHQwZSJawuF-Vm3CEO7KUzh5dFkG2PeyfZ9t9UlYj474Q-srz5PPI5FhmAJDx3_4wR-2X1huddDenU9hByutd9U70jClYwJcmz6YQJ1zrB0M9Bu5zQ5XFQMmiT-bwri0cQopE28DBlalWRYgYBGEO6O6nWQFbMU5cD2pvdZ2xAL9fki_eVAwbn6yQQniHfxEGVZiWsABVEuhkl0khnp8n-k0FN3RdqPo5L38d4D6eGLFaLEuRY'
    # ACCOUNT_ID = 'b307f81c-2e72-4047-81a3-b7a022189f5a'
    ACCOUNT_ID = 'a423babb-9e17-40cd-8c70-02ddc677da0b'
    CLIENT_ID = 'Ficus_iePEnzfporIaweKvm'

    __sync_listener: SynchronizationListener
    __api_connection: StreamingMetaApiConnectionInstance
    __price_managers: Dict[TradingSymbol, MetatraderSymbolPriceManager]

    def __init__(self):
        self.__price_managers = {}
        self.__trade_manager = TradingManager(self)

    async def connect_account(self):
        api = MetaApi(token=Vantage.META_API_TOKEN)
        account = await api.metatrader_account_api.get_account(account_id=Vantage.ACCOUNT_ID)

        initial_state = account.state
        deployed_states = ['DEPLOYING', 'DEPLOYED']

        if initial_state not in deployed_states:
            #  wait until account is deployed and connected to broker
            print('Deploying account')
            await account.deploy()

        print('Waiting for API server to connect to broker (may take couple of minutes)')
        await account.wait_connected()

        self.__api_connection = account.get_streaming_connection()
        await self.__api_connection.connect()
        await self.__api_connection.wait_synchronized()

    async def prepare_listeners(self, symbols_to_subscribe: List[TradingSymbol]):
        try:
            for symbol in symbols_to_subscribe:
                manager = MetatraderSymbolPriceManager(symbol)
                self.__price_managers[symbol] = manager
                await self.__api_connection.subscribe_to_market_data(symbol=symbol.name)

            self.__sync_listener = MetaSynchronizationListener(self.__price_managers, self.__trade_manager)
            self.__api_connection.add_synchronization_listener(self.__sync_listener)
        except Exception as ex:
            print(''.join(traceback.TracebackException.from_exception(ex).format()))

    async def disconnect(self, symbols_to_unsubscribe: List[TradingSymbol]):
        print("Disconnecting...")
        for symbol in symbols_to_unsubscribe:
            await self.__api_connection.unsubscribe_from_market_data(symbol=symbol.name)

        self.__api_connection.remove_synchronization_listener(self.__sync_listener)

        # await self.__api_connection.account.undeploy()
        await self.__api_connection.close()

    def get_ohlcv_for_symbol(self, symbol):
        price_manager = self.__price_managers[symbol]
        return price_manager.generate_ohlcv(5)

    async def open_trade(self, symbol: TradingSymbol, direction: TradeDirection,
                         volume: float, stop_loss: float) -> MetatraderTradeResponse:
        if direction is TradeDirection.BUY:
            return await (self.__api_connection
                          .create_market_buy_order(symbol=symbol.name, volume=volume, stop_loss=stop_loss))
        elif direction is TradeDirection.SELL:
            return await (self.__api_connection
                          .create_market_sell_order(symbol=symbol.name, volume=volume, stop_loss=stop_loss))

    async def close_trade(self, trade: FicusTrade, trading_symbol) -> MetatraderTradeResponse:
        try:
            return await self.__api_connection.close_position(trade['position_id'])
        except Exception as e:
            print(f"Failed to close position for {trade}: {e}")

    async def partially_close_trade(self, trade: FicusTrade, symbol: TradingSymbol) -> MetatraderTradeResponse:
        try:
            return await self.__api_connection.close_position_partially(
                position_id=trade['position_id'], volume=trade['volume'])
        except Exception as e:
            print(f"Failed to partially close position for {trade}: {e}")

    async def modify_trade(self, trade: FicusTrade) -> MetatraderTradeResponse:
        try:
            return await self.__api_connection.modify_position(
                position_id=trade['position_id'], stop_loss=trade['stop_loss_price'])
        except Exception as e:
            print(f"Failed to modify trade {trade}: {e}")

    # called from main file [x] minutes, as configured
    async def on_ohlcv(self, last_ohlcv, symbol):
        await self.__trade_manager.on_ohclv(last_ohlcv, symbol)
