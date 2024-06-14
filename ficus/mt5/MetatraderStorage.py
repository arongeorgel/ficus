import json
from datetime import datetime, timedelta
from typing import List

import pandas as pd
from metaapi_cloud_sdk.metaapi.models import MetatraderSymbolPrice


class MetatraderSymbolPriceManager:
    __MINUTES_FILE_SAVE = 10

    def __init__(self, trading_symbol: str):
        self.__trading_symbol = trading_symbol
        self.data: List[MetatraderSymbolPrice] = []
        self.__load_data_for_today_and_yesterday()
        self.__last_write = datetime.now()

    def __load_data_for_today_and_yesterday(self):
        today_file_path = self.__generate_file_path(datetime.now())
        yesterday_file_path = self.__generate_file_path(datetime.now() - timedelta(days=1))
        self.data = []
        self.__load_data(yesterday_file_path)
        self.__load_data(today_file_path)

    def __generate_file_path(self, date):
        timestamp = date.strftime("%Y_%m_%d")
        return f"meta_symbol_{self.__trading_symbol.lower()}_{timestamp}.json"

    def __load_data(self, file_path):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                self.data.extend([self._convert_str_to_datetime(item) for item in data])
        except FileNotFoundError:
            pass  # If the file is not found, just pass

    def save_data(self):
        # validate file to save into.
        today = datetime.now().strftime("%Y_%m_%d")
        file_path = f"meta_symbol_{self.__trading_symbol.lower()}_{today}.json"

        json_data = [self._convert_datetime_to_str(item) for item in self.data]
        with open(file_path, 'w') as file:
            json.dump(json_data, file, indent=4)

    def add_symbol_price(self, symbol_price: MetatraderSymbolPrice):
        self.data.append(symbol_price)
        current_time = datetime.now()
        if (current_time - self.__last_write) > timedelta(minutes=self.__MINUTES_FILE_SAVE):
            self.save_data()
            self.__last_write = current_time

    def _convert_datetime_to_str(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._convert_datetime_to_str(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_datetime_to_str(item) for item in obj]
        else:
            return obj

    def _convert_str_to_datetime(self, obj):
        if isinstance(obj, str):
            try:
                return datetime.fromisoformat(obj)
            except ValueError:
                return obj
        elif isinstance(obj, dict):
            return {k: self._convert_str_to_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_str_to_datetime(item) for item in obj]
        else:
            return obj

    def remove_old_data(self):
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=48)
        self.data = [entry for entry in self.data if entry['time'] > cutoff_time]

    def generate_ohlcv(self, interval: int):
        """

        :param interval: interval in minutes
        :return:
        """
        df = pd.DataFrame(self.data.copy())
        df['time'] = pd.to_datetime(df['time'])
        df['brokerTime'] = pd.to_datetime(df['brokerTime'])
        df.set_index('brokerTime', inplace=True)

        # Calculate the average of ask and bid prices
        df['average_price'] = (df['ask'] + df['bid']) / 2

        # Resample based on the average price
        resampled = df['average_price'].resample(f'{interval}min').ohlc()

        # Rename columns to capitalize them
        resampled.columns = ['Open', 'High', 'Low', 'Close']

        # Reset index to have 'Datetime' as a column
        resampled = resampled.reset_index()
        resampled.rename(columns={'brokerTime': 'Datetime'}, inplace=True)

        return resampled
