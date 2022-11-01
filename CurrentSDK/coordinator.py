from dotenv import load_dotenv, dotenv_values
import os
import json
import web3

from db import MongoDB
from connector import Connector
from decimal import Decimal
from customerStore import CustomerStore
from assetStore import AssetStore
from userStore import UserStore



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
            customerCollection='Customers',
            assetCollection='Assets',
            userCollection='Users'
        ):
        """Initialize for the coordinator."""
        if connector == None:
            connector = Connector(COORDADDRESS)
        self.connector = connector
        self.coord = connector.contract
        self.w3 = connector.w3
        self.customerStore = CustomerStore(database=database, collection=customerCollection)
        self.assetStore = AssetStore(database=database, collection=assetCollection)
        self.userStore = UserStore(database=database, collection=userCollection)

        # DB
        self.client = MongoDB()
        self.databaseName = database
        self.assetCollection = assetCollection
        self.userCollection = userCollection
        self.customerCollection = customerCollection
        self.db = self.client.setDatabase(database)
        self.collection = self.client.setCollection(customerCollection)

    def restart(self):
        self.customerStore.client.kill(self.customerStore.databaseName, self.customerStore.collectionName)
        self.assetStore.client.kill(self.assetStore.databaseName, self.assetStore.collectionName)
        self.userStore.client.kill(self.userStore.databaseName, self.userStore.collectionName)
        print(self.customerStore.client.getAllRecords())
        print(self.assetStore.client.getAllRecords())
        print(self.userStore.client.getAllRecords())

        
    # Register as a customer

    def registerCustomer(self):
        """
        $$ CONTRACT INTERACTION $$

        Calls the contract and registers a new customer

        TODO:
        Return the customer Identifier and other userful info to fix shit code

        Returns a dictionary:
        {
            'customer': address, new created contract
            'controller': address, controller of the contract
        }
        """
        # Create a new customer invoice address on the contract, send 0.1 ether
        value = self.w3.toWei(Decimal(0.1), 'ether')
        tx_hash = self.coord.functions.registerCustomer(
            CONTROLLER
        ).transact({'from': REGISTRAR, 'value': value})
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        # Log the data in the mongoDB
        customerId, success, _ = self.customerStore.addNewCustomer(tx_receipt.logs[0].address)

        # Return the parsed event object from the contract
        event = self.coord.events.CustomerRegistered().processReceipt(tx_receipt)
        event = event[0]['args']
        return event

    def registerAssets(self, customerInvoice, assetAddresses, assetItemTypes):
        """
        $$ CONTRACT INTERACTION $$

        Takes assets and registers them to a customerInvoice address location

        Returns a dictionary:
        {
            'customer': address, new created contract
            'additionalContracts': address[] new contracts added
            'updatedContracts': address[] updated list of contracts 
        }
        """
        # Check for existing records for the invoice address
        recs = self.customerStore.client.getRecord(
            {
                'invoiceAddress': customerInvoice
            }, 
            db=self.databaseName, 
            collection=self.customerCollection
        )

        # if the invoice record does not exist, not a valid customer
        if len(recs) == 0:
            return 0, False, "Customer invoice not registered"
        
        customerIdentifier = recs[0]['customerIdentifier']

        # Register those assets on chain for the customer
        # Asset controller is the CONTROLLER address
        tx_hash = self.coord.functions.registerAssets(
            CONTROLLER,
            customerInvoice,
            assetAddresses,
            assetItemTypes
        ).transact({'from': CONTROLLER})
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        # Parse the event object for the return later
        event = self.coord.events.AddedAssetsToCustomer().processReceipt(tx_receipt)
        event = event[0]['args']

        # Log the addresses into the asset store
        res = self.assetStore.addAssets(customerIdentifier, assetAddresses, assetItemTypes)

        return event
    
    def getCustomerBill(self, customerId=None, invoiceAddress=None):
        if customerId == None and invoiceAddress == None:
            return "ERR NO CUSTOMER TO SEARCH FOR"
        
        if invoiceAddress == None:
            invoiceAddress = self.customerStore.getCustomerInvoiceAddress(customerId)

        res = self.coord.functions.customers(
            invoiceAddress
        ).call({'from': REGISTRAR})
        return res[0]


    def mintAssets(self, packages, recipientUsernames):
        """
        $$ CONTRACT INTERACTION $$

        Mint a set of assets to recipients in the DB.
        Recipients must be registered, using their username for confirmation

        Returns a dictionary:
        {
            'packages': PackageItem[] packages minted to customers
                - {
                    'itemType' : itemtype (0-5)
                    'token': Address of the token
                    'identifier': NFT identifiers
                    'amount': amount of tokens
                }
            'recipients': address[] addresses the items were minted to
        }
        """
        # Check the DB for each of the users in the input
        # Add their addresses and identifiers to a list for use later
        userAddresses = []
        userIdentifiers = []
        for user in recipientUsernames:
            recs = self.userStore.client.getRecord(
                {
                    'username': user
                }, 
                db=self.databaseName, 
                collection=self.userCollection
            )
            if len(recs) == 0:
                return 0, False, "User not registered"
            userAddresses.append(recs[0]['address'])
            userIdentifiers.append(recs[0]['userIdentifier'])
        
        # Check the DB for assets, add IDs to a list for later
        assetIdentifiers = []
        for item in packages:
            recs = self.assetStore.client.getRecord(
                {
                    'assetAddress': item['token']
                }, 
                db=self.databaseName, 
                collection=self.assetCollection
            )

            if len(recs) == 0:
                return 0, False, "Asset not registered"
            assetIdentifiers.append(recs[0]['assetIdentifier'])

        # Contract call: Mint the assets to the users
        tx_hash = self.coord.functions.mintAssets(
            packages,
            userAddresses
        ).transact({'from': CONTROLLER})
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        # Parse the event back for confirmation
        event = self.coord.events.MintedAssets().processReceipt(tx_receipt)
        event = event[0]['args']

        # Log user updates into the DB now
        for i  in range(0, len(packages)):
            obj = {
                'assetIdentifier': assetIdentifiers[i],
                'amount': packages[i]['amount'],
                'id': packages[i]['identifier']
            }
            self.userStore.addAssetItemToUser(userIdentifiers[i], obj, self.assetStore)

        return event

    # Register with assets
    def registerWithAssets(self, assetAddresses, assetItemTypes):
        """
        $$ CONTRACT INTERACTION $$

        Creates a new customer and also registers assets to their invoice

        Returns a dictionary:
        {
            'additionalContracts': address[] new contracts added
            'updatedContracts': address[] updated list of contracts 
        }
        """
        # Register a new customer with the assets
        value = self.w3.toWei(Decimal(0.1), 'ether')
        tx_hash = self.coord.functions.registerWithAssets(
            CONTROLLER,
            assetAddresses,
            assetItemTypes
        ).transact({'from': CONTROLLER, 'value': value})
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        # Parse the event for details
        event = self.coord.events.AddedAssetsToCustomer().processReceipt(tx_receipt)
        event = event[0]['args']
        
        # Add new customer to customer store
        customerId, success, _ = self.customerStore.addNewCustomer(event['customer'])
        # Add assets to that customer
        res = self.assetStore.addAssets(customerId, assetAddresses, assetItemTypes)
        return event


coordinator = Coordinator()