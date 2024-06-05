import datetime
import json
from typing import List

import pandas as pd
from metaapi_cloud_sdk.metaapi.models import MetatraderSymbolPrice


class MetatraderSymbolPriceManager:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data: List[MetatraderSymbolPrice] = []
        self.load_data()

    def load_data(self):
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
                self.data = [self._convert_str_to_datetime(item) for item in data]
        except FileNotFoundError:
            self.data = []

    def save_data(self):
        json_data = [self._convert_datetime_to_str(item) for item in self.data]
        with open(self.file_path, 'w') as file:
            json.dump(json_data, file, indent=4)

    def add_symbol_price(self, symbol_price: MetatraderSymbolPrice):
        self.data.append(symbol_price)
        self.save_data()

    def _convert_datetime_to_str(self, obj):
        if isinstance(obj, datetime.datetime):
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
                return datetime.datetime.fromisoformat(obj)
            except ValueError:
                return obj
        elif isinstance(obj, dict):
            return {k: self._convert_str_to_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_str_to_datetime(item) for item in obj]
        else:
            return obj

    def generate_ohlcv(self, interval: int):
        """

        :param interval: interval in minutes
        :return:
        """
        df = pd.DataFrame(self.data.copy())
        df['time'] = pd.to_datetime(df['time'])
        df['brokerTime'] = pd.to_datetime(df['brokerTime'])
        df.set_index('brokerTime', inplace=True)

        resampled = df['bid'].resample(f'{interval}min').ohlc()

        # Rename columns to capitalize them
        resampled.columns = ['Open', 'High', 'Low', 'Close']

        # Reset index to have 'Datetime' as a column
        resampled = resampled.reset_index()
        resampled.rename(columns={'brokerTime': 'Datetime'}, inplace=True)

        return resampled.dropna()
