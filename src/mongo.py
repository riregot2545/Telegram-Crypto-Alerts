from dotenv import find_dotenv, load_dotenv
from pymongo import MongoClient

from .config import MONGODB_CONNECTION_STRING, MONGODB_DATABASE, MONGODB_COLLECTION


class MongoDBConnection(MongoClient):
    """LOADS CONNECTION VARIABLES FROM .ENV FILE - STORE CREDENTIALS THERE"""
    def __init__(self):
        cxn_string = MONGODB_CONNECTION_STRING
        if cxn_string is None:
            raise ValueError(f"Missing MongoDB connection string environment variable (MONGODB_CONNECTION_STRING)")
        database = MONGODB_DATABASE
        if database is None:
            raise ValueError(f"Missing MongoDB database environment variable (MONGODB_DATABASE)")
        collection = MONGODB_COLLECTION
        if collection is None:
            raise ValueError(f"Missing MongoDB database collection environment variable (MONGODB_COLLECTION)")

        super().__init__(cxn_string)
        self.uri = cxn_string
        self.database = self[database]
        self.collection = self.database[collection]

    def ping(self):
        self.admin.command('ping')
        print(f"Pinged your deployment. You successfully connected to MongoDB at {self.uri}!")
