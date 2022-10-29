# Imported from https://github.com/eucliss/BasinSDK/blob/master/BasinSDK/db.py
# I wrote that file to help with a different discord bot
# Provides basic functionality for using a mongoDB
# Using that file as a bootstrap for MongoDB

import web3
import json
import time
import random
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from typing import Dict, Any

load_dotenv()

token = os.getenv('INFURA_KEY')
MONGO_URI = os.getenv('MONGO_URI')

# MongoDB 
class MongoDB():

    def __init__(self, URI=MONGO_URI):
        try:
            self.client = MongoClient(MONGO_URI)
        except Exception as e:
            print(f'Error connecting to mongodb: {e}')
        
    # Set the current Database
    def setDatabase(self, db: str):
        self.db = self.client[db]
        return self.db

    # Set current Collection
    def setCollection(self, collection: str):
        self.collection = self.db[collection]
        return self.collection

    # Store a record in the DB
    def storeRecord(self, record:Dict[Any, Any], db:str = None, collection:str = None):
        res = None
        try:
            if db == None and collection == None:
                res = self.collection.insert_one(record)
            else:
                res = self.client[db][collection].insert_one(record)
        except Exception as e:
                print(f'Exception adding record to collection: {e}')
        return res

    # Get all records from the DB
    def getAllRecords(self, db:str = None, collection:str = None):
        records = []
        if db == None and collection == None:
            for doc in self.collection.find():
                records.append(doc)
        else:
            for doc in self.client[db][collection].find():
                records.append(doc)
        return records

    # Get a single record from the dB
    def getRecord(self, record:Dict[Any, Any], db:str = None, collection:str = None):
        records = []
        if db == None and collection == None:
            for doc in self.collection.find(record):
                records.append(doc)
        else:
            for doc in self.client[db][collection].find(record):
                records.append(doc)
        return records
    
    # Update a record from the DB
    def updateRecord(
        self, 
        oldRecord:Dict[Any, Any], 
        newRecord:Dict[Any, Any], 
        db:str = None, 
        collection:str = None
    ):
        res = ''
        newRecord = {"$set" : newRecord}
        if db == None and collection == None:
            res = self.collection.update_one(oldRecord, newRecord)
        else:
            res = self.client[db][collection].update_one(oldRecord, newRecord)
        return res

    def kill(self, d, c):
        self.setDatabase(d)
        self.setCollection(c)
        self.collection.drop()


db = MongoDB()