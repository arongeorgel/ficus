# type: ignore
import logging
from typing import List

from metaapi_cloud_sdk import SynchronizationListener
from metaapi_cloud_sdk.clients.metaapi.synchronization_listener import HealthStatus
from metaapi_cloud_sdk.metaapi.models import MarketDataSubscription, MarketDataUnsubscription, \
    MetatraderTick, MetatraderSymbolPrice, MetatraderSymbolSpecification, MetatraderDeal, \
    MetatraderOrder, MetatraderPosition, MetatraderAccountInformation

from ficus.mt5.MetatraderStorage import MetatraderSymbolPriceManager
from ficus.mt5.TradingManager import TradingManager

logger = logging.getLogger('ficus_logger')


class MetaSynchronizationListener(SynchronizationListener):
    def __init__(self, price_managers: dict[str, MetatraderSymbolPriceManager],
                 trading_manager: TradingManager):
        self.price_managers = price_managers
        self.trading_manager = trading_manager

    async def on_connected(self, instance_index: str, replicas: int):
        logger.info("meta > Connected")
        return await super().on_connected(instance_index, replicas)

    async def on_health_status(self, instance_index: str, status: HealthStatus):
        return await super().on_health_status(instance_index, status)

    async def on_disconnected(self, instance_index: str):
        logger.info("meta > Disconnected")
        return await super().on_disconnected(instance_index)

    async def on_broker_connection_status_changed(self, instance_index: str, connected: bool):
        return await super().on_broker_connection_status_changed(instance_index, connected)

    async def on_synchronization_started(self, instance_index: str, specifications_hash: str = None,
                                         positions_hash: str = None, orders_hash: str = None,
                                         synchronization_id: str = None):
        logger.info("meta > Sync started")
        return await super().on_synchronization_started(instance_index, specifications_hash, positions_hash,
                                                        orders_hash, synchronization_id)

    async def on_account_information_updated(self, instance_index: str,
                                             account_information: MetatraderAccountInformation):
        logger.info(f"meta > Account info updated {account_information}")
        return await super().on_account_information_updated(instance_index, account_information)

    async def on_positions_replaced(self, instance_index: str, positions: List[MetatraderPosition]):
        return await super().on_positions_replaced(instance_index, positions)

    async def on_positions_synchronized(self, instance_index: str, synchronization_id: str):
        logger.info("meta > positions synced")
        return await super().on_positions_synchronized(instance_index, synchronization_id)

    async def on_positions_updated(self, instance_index: str, positions: MetatraderPosition,
                                   removed_positions_ids: List[str]):
        return await super().on_positions_updated(instance_index, positions, removed_positions_ids)

    async def on_position_updated(self, instance_index: str, position: MetatraderPosition):
        logger.info(f"Position updated: {position}")
        return await super().on_position_updated(instance_index, position)

    async def on_position_removed(self, instance_index: str, position_id: str):
        logger.info(f"Position removed by broker: {position_id}")
        await self.trading_manager.on_closed_by_broker(position_id)
        return await super().on_position_removed(instance_index, position_id)

    async def on_pending_orders_replaced(self, instance_index: str, orders: List[MetatraderOrder]):
        return await super().on_pending_orders_replaced(instance_index, orders)

    async def on_pending_orders_updated(self, instance_index: str, orders: List[MetatraderOrder],
                                        completed_order_ids: List[str]):
        return await super().on_pending_orders_updated(instance_index, orders, completed_order_ids)

    async def on_pending_order_updated(self, instance_index: str, order: MetatraderOrder):
        return await super().on_pending_order_updated(instance_index, order)

    async def on_pending_order_completed(self, instance_index: str, order_id: str):
        return await super().on_pending_order_completed(instance_index, order_id)

    async def on_pending_orders_synchronized(self, instance_index: str, synchronization_id: str):
        return await super().on_pending_orders_synchronized(instance_index, synchronization_id)

    async def on_history_order_added(self, instance_index: str, history_order: MetatraderOrder):
        return await super().on_history_order_added(instance_index, history_order)

    async def on_history_orders_synchronized(self, instance_index: str, synchronization_id: str):
        return await super().on_history_orders_synchronized(instance_index, synchronization_id)

    async def on_deal_added(self, instance_index: str, deal: MetatraderDeal):
        return await super().on_deal_added(instance_index, deal)

    async def on_deals_synchronized(self, instance_index: str, synchronization_id: str):
        return await super().on_deals_synchronized(instance_index, synchronization_id)

    async def on_symbol_specification_updated(self, instance_index: str, specification: MetatraderSymbolSpecification):
        return await super().on_symbol_specification_updated(instance_index, specification)

    async def on_symbol_specification_removed(self, instance_index: str, symbol: str):
        return await super().on_symbol_specification_removed(instance_index, symbol)

    async def on_symbol_specifications_updated(self, instance_index: str,
                                               specifications: List[MetatraderSymbolSpecification],
                                               removed_symbols: List[str]):
        return await super().on_symbol_specifications_updated(instance_index, specifications, removed_symbols)

    async def on_symbol_prices_updated(self, instance_index: str, prices: List[MetatraderSymbolPrice],
                                       equity: float = None, margin: float = None, free_margin: float = None,
                                       margin_level: float = None, account_currency_exchange_rate: float = None):
        return await super().on_symbol_prices_updated(instance_index, prices, equity, margin, free_margin, margin_level,
                                                      account_currency_exchange_rate)

    async def on_ticks_updated(self, instance_index: str, ticks: List[MetatraderTick], equity: float = None,
                               margin: float = None, free_margin: float = None, margin_level: float = None,
                               account_currency_exchange_rate: float = None):
        return await super().on_ticks_updated(instance_index, ticks, equity, margin, free_margin, margin_level,
                                              account_currency_exchange_rate)

    async def on_subscription_downgraded(self, instance_index: str, symbol: str,
                                         updates: List[MarketDataSubscription] or None = None,
                                         unsubscriptions: List[MarketDataUnsubscription] or None = None):
        return await super().on_subscription_downgraded(instance_index, symbol, updates, unsubscriptions)

    async def on_stream_closed(self, instance_index: str):
        logger.info("meta > Stream closed.")
        return await super().on_stream_closed(instance_index)

    async def on_unsubscribe_region(self, region: str):
        return await super().on_unsubscribe_region(region)

    ######
    async def on_symbol_price_updated(self, instance_index: str, price: MetatraderSymbolPrice):
        # save data
        symbol_updated = price['symbol']
        if symbol_updated in self.price_managers:
            self.price_managers[symbol_updated].add_symbol_price(price)
            # validate price
            await self.trading_manager.validate_price(price['bid'], symbol_updated)

        return await super().on_symbol_price_updated(instance_index, price)
