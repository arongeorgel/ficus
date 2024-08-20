import unittest
from unittest.mock import MagicMock, patch, call
import asyncio

# Import the FicusTrader and FicusTrade from their respective modules
from ficus.metatrader.FicusTrader import FicusTrader
from ficus.models.models import FicusTrade


class TestFicusTrader(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        # Mock the Terminal and MemoryStorage classes
        self.mock_terminal = MagicMock()
        self.mock_storage = MagicMock()

        # Create an instance of FicusTrader with mocked dependencies
        self.ficus_trader = FicusTrader(self.mock_terminal, self.mock_storage)

    def test_validate_price_on_buy_take_profit_1_hit(self):
        # Create an instance of FicusTrade with take profit conditions
        trade = FicusTrade(
            stop_loss_price=1.1800,
            entry_price=1.1900,
            trade_direction='buy',
            take_profits=[1.2000, 1.2100, 1.2200],
            take_profits_hit=[False, False, False],
            start_volume=1.0,
            volume=1.0,
            position_id='12345',
            message_id='msg-001',
            symbol="EURUSD"
        )

        # Call _validate_price_on_buy with a price that should hit TP1
        current_price = 1.201  # This should trigger take profit 1
        self.ficus_trader._validate_price_on_buy(current_price, trade)

        # Assert that the appropriate methods were called
        self.mock_terminal.close_trade.assert_called_once()
        self.mock_storage.update_trade.assert_called_once()
        self.assertTrue(trade['take_profits_hit'][0])

    def test_validate_price_on_buy_take_profit_2_hit(self):
        # Create an instance of FicusTrade with take profit conditions
        trade = FicusTrade(
            stop_loss_price=1.1800,
            entry_price=1.1900,
            trade_direction='buy',
            take_profits=[1.2000, 1.2100, 1.2200],
            take_profits_hit=[False, False, False],
            start_volume=1.0,
            volume=1.0,
            position_id='12345',
            message_id='msg-001',
            symbol="EURUSD"
        )

        # Call _validate_price_on_buy with a price that should hit TP1
        current_price = 1.211  # This should trigger take profit 1
        self.ficus_trader._validate_price_on_buy(current_price, trade)

        # Assert that the appropriate methods were called
        self.mock_terminal.close_trade.assert_called_once()
        self.mock_terminal.update_stop_loss.asset_called_once()
        self.mock_storage.update_trade.assert_called_once()
        self.assertTrue(trade['take_profits_hit'][1])

    def test_validate_price_on_sell_take_profit_2_hit(self):
        # Create an instance of FicusTrade with take profit conditions
        trade = FicusTrade(
            stop_loss_price=1.3100,
            entry_price=1.3000,
            trade_direction='sell',
            take_profits=[1.2900, 1.2900, 1.2700],
            take_profits_hit=[True, False, False],
            start_volume=1.0,
            volume=1.0,
            position_id='12345',
            message_id='msg-002',
            symbol="EURUSD"
        )

        # Call _validate_price_on_sell with a price that should hit TP2
        price = 1.289999  # This should trigger take profit 2
        self.ficus_trader._validate_price_on_sell(price, trade)

        # Assert that the appropriate methods were called
        self.mock_terminal.close_trade.assert_called_once()
        self.mock_storage.update_trade.assert_called_once()
        self.assertTrue(trade['take_profits_hit'][1])

    async def test_monitor_active_trades_with_mock_positions(self):
        # Set up a mock return value for get_open_positions
        mock_positions = [
            MagicMock(ticket='12345', symbol="EURUSD", trade_direction="buy"),
            MagicMock(ticket='67890', symbol="USDJPY", trade_direction="sell")
        ]
        self.mock_terminal.get_open_positions.return_value = mock_positions

        # Create an instance of FicusTrade for the mock return value
        mock_trade = FicusTrade(
            stop_loss_price=1.1800,
            entry_price=1.1900,
            trade_direction='buy',
            take_profits=[1.2000, 1.2100, 1.2200],
            take_profits_hit=[False, False, False],
            start_volume=1.0,
            volume=1.0,
            position_id='12345',
            message_id='msg-001',
            symbol="EURUSD"
        )

        def get_trade_side_effect(ticket):
            if ticket == '12345':
                return mock_trade
            return None

        self.mock_storage.get_trade.side_effect = get_trade_side_effect

        # Mock the current price to hit TP1
        self.mock_terminal.get_current_price.return_value = 1.201

        async def cancel_after_delay(task, delay):
            """Cancel the task after the specified delay."""
            await asyncio.sleep(delay)
            task.cancel()

        # Run monitor_active_trades in a separate task
        task = asyncio.create_task(self.ficus_trader.monitor_active_trades())

        # Start a task to cancel the monitor task after a short delay
        cancel_task = asyncio.create_task(cancel_after_delay(task, 1))

        # Wait for the monitor task to complete (cancelled)
        try:
            await task
        except asyncio.CancelledError:
            pass

        # Ensure cancel_task is complete
        await cancel_task

        # Assert that the appropriate methods were called
        self.mock_terminal.get_open_positions.assert_called()
        self.mock_storage.get_trade.assert_has_calls([call('12345'), call('67890')])
        self.mock_terminal.get_current_price.assert_called_with("EURUSD", "buy")
        self.mock_terminal.close_trade.assert_called()
        self.mock_storage.update_trade.assert_called()
        self.assertTrue(mock_trade['take_profits_hit'][0])


if __name__ == '__main__':
    unittest.main()