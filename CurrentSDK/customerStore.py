from dotenv import load_dotenv, dotenv_values
import os
import json
import web3

from db import MongoDB
from connector import Connector
from decimal import Decimal



load_dotenv()

token = os.getenv('INFURA_KEY')
addresses = dotenv_values("../.env.addresses")

COORDABI = "../out/Coordinator.sol/Coordinator.json"
COORDADDRESS = web3.Web3.toChecksumAddress(addresses['COORDINATORADDRESS'])

REGISTRAR = web3.Web3.toChecksumAddress(addresses['REGISTRAR'])
REGISTRARPK = addresses['REGISTRARPK']

CONTROLLER = web3.Web3.toChecksumAddress(addresses['CONTROLLER'])
CONTROLLERPK = addresses['CONTROLLERPK']

CUSTODIAL = web3.Web3.toChecksumAddress(addresses['CUSTODIAL'])
CUSTODIALPK = addresses['CUSTODIALPK']


# Connector class will be designed to connect everything to Web3.
class CustomerStore():

    def __init__(
            self, 
            database='CurrentSDK', 
            collection='Customers'
        ):
        """Initialize for the coordinator."""

        # DB
        self.client = MongoDB()
        self.databaseName = database
        self.collectionName = collection
        self.db = self.client.setDatabase(database)
        self.collection = self.client.setCollection(collection)

    def storeCustomer(self, invoiceAddress):
        recs = self.client.getRecord({'invoiceAddress': invoiceAddress}, db=self.databaseName, collection=self.collectionName)
        if len(recs) > 0:
            self.client.kill()
            return 
        # acc = self.w3.eth.account.create()
        obj = {
            'invoiceAddress': invoiceAddress,
        }
        self.client.storeRecord(obj, self.databaseName, self.collectionName)

        
customerStore = CustomerStore()