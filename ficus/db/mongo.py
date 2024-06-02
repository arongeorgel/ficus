from datetime import datetime
from typing import List, Any

from metaapi_cloud_sdk import HistoryStorage
from metaapi_cloud_sdk.metaapi.models import MetatraderSymbolPrice, MetatraderOrder, MetatraderDeal
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


class MongoDatabase:
    mongo_client = None
    # keep in memory also the data for faster access
    xauusd_list: list[MetatraderSymbolPrice] = []

    def prepare_mongo(self):
        uri = ("mongodb+srv://arongeorgel:SXEgl2Rf6BNNXLYJ@mainficus.nnmqn3d.mongodb.net/"
               "?retryWrites=true&w=majority&appName=MainFicus")

        # Create a new client and connect to the server
        self.mongo_client = MongoClient(uri, server_api=ServerApi('1'))

    def get_database(self):
        return self.mongo_client['MainFicus']

    def write(self, collection_name, data):
        test_collection = self.get_database()[collection_name]
        test_collection.insert_one(data)
