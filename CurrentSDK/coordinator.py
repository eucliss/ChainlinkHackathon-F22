from dotenv import load_dotenv, dotenv_values
import os
import json
import web3

from db import MongoDB
from connector import Connector
from decimal import Decimal
from customerStore import CustomerStore



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
class Coordinator():

    def __init__(
            self, 
            connector:Connector=None, 
            database='CurrentSDK', 
            collection='Customers'
        ):
        """Initialize for the coordinator."""
        if connector == None:
            connector = Connector(COORDADDRESS)
        self.coord = connector.contract
        self.w3 = connector.w3
        self.customerStore = CustomerStore(database=database, collection=collection)

        # DB
        self.client = MongoDB()
        self.databaseName = database
        self.collectionName = collection
        self.db = self.client.setDatabase(database)
        self.collection = self.client.setCollection(collection)
        
    # Register as a customer

    def registerCustomer(self):

        # Create a new customer invoice address
        value = self.w3.toWei(Decimal(0.1), 'ether')
        tx_hash = self.coord.functions.registerCustomer(
            CONTROLLER
        ).transact({'from': REGISTRAR, 'value': value})
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        # Need to log this into the mongoDB now
        self.customerStore.storeCustomer(tx_receipt.logs[0].address)

        return tx_receipt.logs[0].address

    def registerAssets(self, customerInvoice, assetAddresses, assetItemTypes):

        # Create a new customer invoice address
        value = self.w3.toWei(Decimal(0.1), 'ether')
        tx_hash = self.coord.functions.registerAssets(
            CONTROLLER,
            customerInvoice,
            assetAddresses,
            assetItemTypes
        ).transact({'from': CONTROLLER})
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        # tx_receipt.logs[0].data
        rich_logs = self.coord.events.AddedAssetsToCustomer().processReceipt(tx_receipt)
        # rich_logs = contract.events.myEvent().processReceipt(tx_receipt)
        #  >>> rich_logs[0]['args']
        rich_logs = rich_logs[0]['args']
        # print(rich_logs['customer'])
        # print(rich_logs['additionalContracts'])
        # print(rich_logs['updatedContracts'])

        # Need to log this into the mongoDB now


        return rich_logs

    def mintAssets(self, packages, recipients):
                # Create a new customer invoice address
        tx_hash = self.coord.functions.mintAsets(
            packages,
            recipients
        ).transact({'from': CONTROLLER})
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        # Need to log this into the mongoDB now

        return tx_receipt

    # Register assets

    # Register with assets

    # Distribute Assets

coordinator = Coordinator()