from dotenv import load_dotenv, dotenv_values
import os
import json
import web3

from db import MongoDB
from connector import Connector
from assetStore import AssetStore

from decimal import Decimal



load_dotenv()

token = os.getenv('INFURA_KEY')
STAGE = os.getenv('STAGE')
addresses = ''
if STAGE == 'dev':
    PROVIDER = os.getenv('LOCAL_RPC')
    addresses = addresses = dotenv_values("../.env.addresses")
if STAGE == 'goerli':
    PROVIDER = os.getenv('GOERLI_RPC_URL')
    addresses = dotenv_values("../.env.goerli.addresses")

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
    """
    Database connector for storing customers and their assets.

        [Customers]
        identifier
        invoiceAddress
        assets - assetIdentifier[]

    """

    def __init__(
            self, 
            database='CurrentSDK', 
            collection='Customers',
        ):
        """Initialize for the coordinator."""

        # DB
        self.client = MongoDB()
        self.databaseName = database
        self.collectionName = collection
        self.db = self.client.setDatabase(database)
        self.collection = self.client.setCollection(collection)
        
        self.nextCustomerIdentifier = 1
        self.customerIDPrefix = 'CUST'
    
    def getCustomerIdFromInvoiceAddress(self, invoiceAddress):
        recs = self.client.getRecord(
            {
                'invoiceAddress': invoiceAddress
            }, 
            db=self.databaseName, 
            collection=self.collectionName
        )
        if len(recs) == 0:
            return 0, False, "Invoice address does not exist"
        return recs[0]['customerIdentifier']
    
    def getCustomerInvoiceAddress(self, customerId):
        recs = self.client.getRecord(
            {
                'customerIdentifier': customerId
            }, 
            db=self.databaseName, 
            collection=self.collectionName
        )
        if len(recs) == 0:
            return 0, False, f'Customer does not exist: {customerId}'
        return recs[0]['invoiceAddress']

    # Need to setup all the functionality that is required now in the coordinator.py
    # So DB connection functionality for 
    # Registering a customer
    def addNewCustomer(self, invoiceAddress):
        """
            [Customers]
            identifier
            invoiceAddress
            assets - assetIdentifier[]

        """
        recs = self.client.getRecord(
            {
                'invoiceAddress': invoiceAddress
            }, 
            db=self.databaseName, 
            collection=self.collectionName
        )
        if len(recs) > 0:
            return 0, False, "Invoice address already a customer"
        obj = {
                'customerIdentifier': f'{self.customerIDPrefix}{self.nextCustomerIdentifier}',
                'invoiceAddress': invoiceAddress
            }
        self.client.storeRecord(obj, self.databaseName, self.collectionName)
        self.nextCustomerIdentifier += 1
        return f'{self.customerIDPrefix}{self.nextCustomerIdentifier - 1}', True, "Successfully stored new customer"

    # Registering with assets
    def addCustomerWithAssets(self, invoiceAddress, assetAddresses, itemTypes, assetStore=None):
        """
            [Asset]
            assetIdentifier
            customerIdentifier
            address
            itemtype
        """
        customerIdentifier, success, msg = self.addNewCustomer(invoiceAddress)
        if not success:
            return 0, success, msg 
        
        if assetStore == None:
            assetStore = AssetStore()
        res, success, msg = assetStore.addAssets(customerIdentifier, assetAddresses, itemTypes)

        if not success:
            return None, success, msg

        resObj = {
            'customerIdentifier': customerIdentifier,
            'assetsAdded': res
        }

        return resObj, success, "Successfully created new customer and added assets."

    # minting assets

    # Gotta do the minting and the exporting next ^^ Then its bot shit time

    # Once this is done I think we may be ready to move forward with more of the bot stuff
    # I need a way to re-deploy the contracts and stuff as well
    # So that will probably be a script of some sort that deploys everything

    # I'll also need like an export assets functionality somehow
    # And a register users functionality in the SDK

    # That way the demo can be:
    # Enter discord
    # Register as a user  x 
    # Play the game
    # Win NFT or something from game
    # see that it is allocated to you from discord
    # export the assets when you want to

    # Customer gets billed, user doesnt have to care

        
customerStore = CustomerStore()