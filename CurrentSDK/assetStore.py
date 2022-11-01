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
class AssetStore():
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
            collection='Assets',
        ):
        """Initialize for the coordinator."""

        # DB
        self.client = MongoDB()
        self.databaseName = database
        self.collectionName = collection
        self.db = self.client.setDatabase(database)
        self.collection = self.client.setCollection(collection)
        
        self.nextAssetIdentifier = 1
        self.assetIDPrefix = 'ASS'

    def getAssetIdentifier(self, assetAddress):
        recs = self.client.getRecord(
            {
                'assetAddress': assetAddress
            }, 
            db=self.databaseName, 
            collection=self.collectionName
        )
        if len(recs) == 0:
            return "NO ASSET"
        return recs[0]['assetIdentifier']
    

    # Registering assets
    def addAssets(self, customerIdentifier, assetAddresses, itemTypes):
        """
            [Asset]
            assetIdentifier
            customerIdentifier
            address
            itemType
        """
        res = []
        for i in range(0, len(assetAddresses)):
            recs = self.client.getRecord(
                {
                    'assetAddress': assetAddresses[i]
                }, 
                db=self.databaseName, 
                collection=self.collectionName
            )
            if len(recs) > 0:
                return 0, False, "Asset already registered"

            obj = {
                'assetIdentifier': f'{self.assetIDPrefix}{self.nextAssetIdentifier}',
                'customerIdentifier': customerIdentifier,
                'assetAddress': assetAddresses[i],
                'itemType': itemTypes[i]
            }
            res.append(obj)
            self.client.storeRecord(obj, self.databaseName, self.collectionName)
            self.nextAssetIdentifier += 1

        return res, True, "Successfully stored new assets"

            
    # minting assets
    # Registering with assets

    # I think it may be best to just create a function that takes an object then
    # sets up the customer store stuff

    # Once this is done I think we may be ready to move forward with more of the bot stuff
    # I need a way to re-deploy the contracts and stuff as well
    # So that will probably be a script of some sort that deploys everything

    # I'll also need like an export assets functionality somehow
    # And a register users functionality in the SDK

    # That way the demo can be:
    # Enter discord
    # Register as a user
    # Play the game
    # Win NFT or something from game
    # see that it is allocated to you from discord
    # export the assets when you want to

    # Customer gets billed, user doesnt have to care

        
assetStore = AssetStore()