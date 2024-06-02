import traceback
from typing import List, Dict

from metaapi_cloud_sdk import MetaApi, SynchronizationListener
from metaapi_cloud_sdk.metaapi.streaming_metaapi_connection_instance import StreamingMetaApiConnectionInstance

from ficus.mt5.MetatraderStorage import MetatraderSymbolPriceManager
from ficus.mt5.TradingSymbols import TradingSymbols
from ficus.mt5.listeners.BitcoinSyncListener import BitcoinSyncListener
from ficus.mt5.listeners.GoldSyncListener import GoldSyncListener


class Vantage:
    META_API_TOKEN = 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2MzZjN2NiNzgwNmIxMWMyNDU5MWQ3YTE4MmZmOWY2OCIsInBlcm1pc3Npb25zIjpbXSwiYWNjZXNzUnVsZXMiOlt7ImlkIjoidHJhZGluZy1hY2NvdW50LW1hbmFnZW1lbnQtYXBpIiwibWV0aG9kcyI6WyJ0cmFkaW5nLWFjY291bnQtbWFuYWdlbWVudC1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1ycGMtYXBpIiwibWV0aG9kcyI6WyJtZXRhYXBpLWFwaTp3czpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZWFsLXRpbWUtc3RyZWFtaW5nLWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6d3M6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6Im1ldGFzdGF0cy1hcGkiLCJtZXRob2RzIjpbIm1ldGFzdGF0cy1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoicmlzay1tYW5hZ2VtZW50LWFwaSIsIm1ldGhvZHMiOlsicmlzay1tYW5hZ2VtZW50LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJtdC1tYW5hZ2VyLWFwaSIsIm1ldGhvZHMiOlsibXQtbWFuYWdlci1hcGk6cmVzdDpkZWFsaW5nOio6KiIsIm10LW1hbmFnZXItYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6ImJpbGxpbmctYXBpIiwibWV0aG9kcyI6WyJiaWxsaW5nLWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19XSwidG9rZW5JZCI6IjIwMjEwMjEzIiwiaW1wZXJzb25hdGVkIjpmYWxzZSwicmVhbFVzZXJJZCI6IjYzNmM3Y2I3ODA2YjExYzI0NTkxZDdhMTgyZmY5ZjY4IiwiaWF0IjoxNzE2MjE3ODcwLCJleHAiOjE3MjM5OTM4NzB9.h8O0r_-FxYlqNp9rHF44VfN-BGwh9bXyBc7iNj1RTwi0QeVE9WN6IhpBTcUmA09y-VZ_YrAIvwk-zhrUI3X5EY9mZcGY37bmAJPOoFmNRolI6pme5XKKqjb00W3Km6uxFXXFq9Pjbxhk27D6r8AZeubbovI3rGUZZlQWgbVEqUAMHCZyPA2NmxtxKKoOVGKB4SBb2pBMiO45DFZaNN1b4Durt5HOU-my3i4ucQb1xvfQcu_ZTMeYZCP-FPd02svm0h_OpiBL-P4LCXH_-vFYHlhnv9fuuHV5Tjqj3p6KDHE5_92JgR8pVYPp1bjS6Ei5BOflPQriW03gkfoEjJlKtPJ_c2OUXqDyTAiITZMpMJi2K7Uew7cpBCPV6pL--t1At6tgMTzG3r8jBMCMyWvUk50889RPE4EQUztBJjudxAzoayBdIx9rYJgGuoHQwZSJawuF-Vm3CEO7KUzh5dFkG2PeyfZ9t9UlYj474Q-srz5PPI5FhmAJDx3_4wR-2X1huddDenU9hByutd9U70jClYwJcmz6YQJ1zrB0M9Bu5zQ5XFQMmiT-bwri0cQopE28DBlalWRYgYBGEO6O6nWQFbMU5cD2pvdZ2xAL9fki_eVAwbn6yQQniHfxEGVZiWsABVEuhkl0khnp8n-k0FN3RdqPo5L38d4D6eGLFaLEuRY'
    ACCOUNT_ID = 'e97d4e1f-6ee9-46da-b933-91c4c6343d80'

    __sync_listeners: List[SynchronizationListener] = list()
    __api_connection: StreamingMetaApiConnectionInstance
    __price_managers: Dict[TradingSymbols, MetatraderSymbolPriceManager]

    def __init__(self):
        self.__price_managers = {}

    async def connect_account(self):
        api = MetaApi(token=Vantage.META_API_TOKEN)
        account = await api.metatrader_account_api.get_account(account_id=Vantage.ACCOUNT_ID)
        self.__api_connection = account.get_streaming_connection()
        await self.__api_connection.connect()
        await self.__api_connection.wait_synchronized()

    async def prepare_listeners(self, symbols_to_subscribe: List[TradingSymbols]):
        try:
            for symbol in symbols_to_subscribe:
                price_manager = MetatraderSymbolPriceManager(f"meta_symbol_{symbol.name.lower()}.json")

                if symbol is TradingSymbols.BTCUSD:
                    listener = BitcoinSyncListener(price_manager)
                elif symbol is TradingSymbols.XAUUSD:
                    listener = GoldSyncListener(price_manager)
                else:
                    continue  # Skip symbols that are not BTCUSD or XAUUSD

                self.__price_managers[symbol] = price_manager
                self.__sync_listeners.append(listener)
                self.__api_connection.add_synchronization_listener(listener=listener)

                await self.__api_connection.subscribe_to_market_data(symbol=symbol.name)
        except Exception as ex:
            print(''.join(traceback.TracebackException.from_exception(ex).format()))

    async def disconnect(self, symbols_to_unsubscribe: List[TradingSymbols]):
        for symbol in symbols_to_unsubscribe:
            if symbol is TradingSymbols.BTCUSD:
                await self.__api_connection.unsubscribe_from_market_data(symbol="BTCUSD")

        for listener in self.__sync_listeners:
            self.__api_connection.remove_synchronization_listener(listener)

        await self.__api_connection.close()

    def get_ohlcv_for_symbol(self, symbol):
        price_manager = self.__price_managers[symbol]
        return price_manager.generate_ohlcv(1)
