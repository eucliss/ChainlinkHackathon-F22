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
        """
        Returns a dictionary:
        {
            'customer': address, new created contract
            'controller': address, controller of the contract
        }
        """

        # Create a new customer invoice address
        value = self.w3.toWei(Decimal(0.1), 'ether')
        tx_hash = self.coord.functions.registerCustomer(
            CONTROLLER
        ).transact({'from': REGISTRAR, 'value': value})
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        # Need to log this into the mongoDB now
        self.customerStore.addNewCustomer(tx_receipt.logs[0].address)

        event = self.coord.events.CustomerRegistered().processReceipt(tx_receipt)
        event = event[0]['args']

        return event

    def registerAssets(self, customerInvoice, assetAddresses, assetItemTypes):
        """
        Returns a dictionary:
        {
            'customer': address, new created contract
            'additionalContracts': address[] new contracts added
            'updatedContracts': address[] updated list of contracts 
        }
        """

        # Create a new customer invoice address
        tx_hash = self.coord.functions.registerAssets(
            CONTROLLER,
            customerInvoice,
            assetAddresses,
            assetItemTypes
        ).transact({'from': CONTROLLER})
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        event = self.coord.events.AddedAssetsToCustomer().processReceipt(tx_receipt)
        event = event[0]['args']
        # Need to log this into the mongoDB now

        return event

    def mintAssets(self, packages, recipients):
        """
        Returns a dictionary:
        {
            'packages': PackageItem[] packages minted to customers
            'recipients': address[] addresses the items were minted to
        }
        """
        tx_hash = self.coord.functions.mintAssets(
            packages,
            recipients
        ).transact({'from': CONTROLLER})
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        event = self.coord.events.MintedAssets().processReceipt(tx_receipt)
        event = event[0]['args']

        # Need to log this into the mongoDB now

        return event

    # Register with assets
    def registerWithAssets(self, assetAddresses, assetItemTypes):
        """
        Returns a dictionary:
        {
            'customer': address, new created contract
            'additionalContracts': address[] new contracts added
            'updatedContracts': address[] updated list of contracts 
        }
        """
                # Create a new customer invoice address
        value = self.w3.toWei(Decimal(0.1), 'ether')
        tx_hash = self.coord.functions.registerWithAssets(
            CONTROLLER,
            assetAddresses,
            assetItemTypes
        ).transact({'from': CONTROLLER, 'value': value})
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        event = self.coord.events.AddedAssetsToCustomer().processReceipt(tx_receipt)
        event = event[0]['args']
        # Need to log this into the mongoDB now

        return event


coordinator = Coordinator()