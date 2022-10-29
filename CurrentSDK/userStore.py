from dotenv import load_dotenv, dotenv_values
import os
import json
import web3

from db import MongoDB
from connector import Connector
from decimal import Decimal

load_dotenv()

addresses = dotenv_values("../.env.addresses")

CUSTODIAL = web3.Web3.toChecksumAddress(addresses['CUSTODIAL'])
CUSTODIALPK = addresses['CUSTODIALPK']


# Connector class will be designed to connect everything to Web3.
class UserStore():
    """
    Database connector for storing customers and their assets.

        [Users]
        identifier - Set Here
        username - from registrar
        custodial - True, False
        address (optional) - defaults to custodial address
        assets - {
            assetIdentifier,
            ammount
            nftIdentifiers
            }

    """

    def __init__(
            self, 
            database='CurrentSDK', 
            collection='Users',
        ):
        """Initialize for the coordinator."""

        # DB
        self.client = MongoDB()
        self.databaseName = database
        self.collectionName = collection
        self.db = self.client.setDatabase(database)
        self.collection = self.client.setCollection(collection)
        
        self.nextUserIdentifier = 1
        self.userIDPrefix = 'USE'

    # Registering assets
    def addUser(self, username, custodial=True, address=CUSTODIAL, assets=None):
        """
            [Users]
            identifier - Set Here
            username - from registrar
            custodial - True, False
            address (optional) - defaults to custodial address
            assets - {
                assetIdentifier,
                ammount
                nftIdentifiers
                }
        """
        recs = self.client.getRecord(
            {
                'username': username
            }, 
            db=self.databaseName, 
            collection=self.collectionName
        )
        if len(recs) > 0:
            return 0, False, "Username already registerd"

        obj = {
            'userIdentifier': f'{self.userIDPrefix}{self.nextUserIdentifier}',
            'username': username,
            'custodial': custodial,
            'address': address,
            'assets': None
        }

        self.client.storeRecord(obj, self.databaseName, self.collectionName)
        self.nextUserIdentifier += 1

        return f'{self.userIDPrefix}{self.nextUserIdentifier - 1}', True, "Successfully stored new user."

        
userStore = UserStore()