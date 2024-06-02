from metaapi_cloud_sdk import HistoryStorage
from datetime import datetime
from typing import List

from metaapi_cloud_sdk.metaapi.models import MetatraderOrder, MetatraderDeal


class MongodbHistoryStorage(HistoryStorage):

    def __init__(self):
        """Initializes the in-memory history store instance"""
        super().__init__()
        # self._history_database = FilesystemHistoryDatabase.get_instance()
        self._max_history_order_time = None
        self._max_deal_time = None
        self._flush_promise = None
        self._flush_running = None
        self._flush_timeout = None
        self._reset()

    async def initialize(self, account_id: str, application: str = 'MetaApi'):
        """Initializes the storage and loads required data from a persistent storage."""
        await super(MongodbHistoryStorage, self).initialize(account_id, application)
        history = await self._history_database.load_history(account_id, application)

        for deal in history['deals']:
            await self._add_deal(deal, True)

        for history_order in history['historyOrders']:
            await self._add_history_order(history_order, True)

    async def clear(self):
        pass

    async def last_history_order_time(self, instance_index: str = None) -> datetime:
        return self._max_history_order_time

    async def last_deal_time(self, instance_index: str = None) -> datetime:
        return self._max_deal_time

    async def on_history_order_added(self, instance_index: str, history_order: MetatraderOrder):
        pass

    async def on_deal_added(self, instance_index: str, deal: MetatraderDeal):
        pass

    @property
    def deals(self) -> List[MetatraderDeal]:
        pass

    def get_deals_by_ticket(self, id: str) -> List[MetatraderDeal]:
        pass

    def get_deals_by_position(self, position_id: str) -> List[MetatraderDeal]:
        pass

    def get_deals_by_time_range(self, start_time: datetime, end_time: datetime) -> List[MetatraderDeal]:
        pass

    @property
    def history_orders(self):
        pass

    def get_history_orders_by_ticket(self, id: str) -> List[MetatraderOrder]:
        pass

    def get_history_orders_by_position(self, position_id: str) -> List[MetatraderOrder]:
        pass

    def get_history_orders_by_time_range(self, start_time: datetime, end_time: datetime) -> List[MetatraderOrder]:
        pass