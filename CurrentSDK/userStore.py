from re import L
from dotenv import load_dotenv, dotenv_values
import os
import json
import web3

from db import MongoDB
from connector import Connector
from assetStore import AssetStore

from decimal import Decimal

load_dotenv()

addresses = dotenv_values("../.env.addresses")

CUSTODIAL = web3.Web3.toChecksumAddress(addresses['CUSTODIAL'])
CUSTODIALPK = addresses['CUSTODIALPK']

ItemTypes = {
    'NATIVE': 0,
    'ERC20': 1,
    'ERC721': 2,
    'ERC1155': 3,
    'NONE': 4
}


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
    
    def getUserId(self, username):
        recs = self.client.getRecord(
            {
                'username': username
            }, 
            db=self.databaseName, 
            collection=self.collectionName
        )
        
        if len(recs) == 0:
            return "NO USER"

        return recs[0]['userIdentifier']
    
    def getUserAssets(self, username):
        recs = self.client.getRecord(
            {
                'username': username
            }, 
            db=self.databaseName, 
            collection=self.collectionName
        )
        
        if len(recs) == 0:
            return "NO USER"

        return recs[0]['assets']

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
    
    def addAssetItemToUser(self, userIdentifier, asset_object=None, assetStore=None):
        """
        [Asset]
        assetIdentifier
        customerIdentifier
        address
        itemtype

        [Users]
        identifier - Set Here
        username - from registrar
        custodial - True, False
        address (optional) - defaults to custodial address
        assets - {
            assetIdentifier - {
                    itemTypeObject
                }
            }
        }

        asset_object = {
            assetIdentifier
            amount
            id
        }


        [ERC20]
        amount

        [ERC721]
        amount
        ids[]

        [ERC1155]
        ids {
            id {
                amount
            } 
        }
        """
        recs = self.client.getRecord(
            {
                'userIdentifier': userIdentifier
            }, 
            db=self.databaseName, 
            collection=self.collectionName
        )
        if len(recs) == 0:
            return 0, False, "User does not exist"
        
        if assetStore == None:
            assetStore = AssetStore()

        try:
            assetType = assetStore.client.getRecord(
                {
                    'assetIdentifier': asset_object['assetIdentifier']
                }, 
                db=assetStore.databaseName, 
                collection=assetStore.collectionName
            )
            assetType = assetType[0]['itemType']
            
        except:
            return 0, False, "Asset does not exist."

        assetId = asset_object['assetIdentifier']
        try:
            newObject = {
                str(asset_object['assetIdentifier']): {
                    'amount': asset_object['amount'],
                    'ids': [asset_object['id']]
                }
            }
        except:
            print("IN EXCEPT")
            newObject = {
                str(asset_object['assetIdentifier']): {
                    'amount': asset_object['amount'],
                }
            }
        try:
            currentAssets = recs[0]['assets'][assetId]
            if assetType == ItemTypes['ERC20']:
                newObject[assetId]['amount'] += currentAssets['amount']
            elif assetType == ItemTypes['ERC721']:
                newIds = currentAssets['ids']
                newIds.append(newObject[assetId]['ids'][0])
                newObject[assetId]['ids'] = newIds
                newObject[assetId]['amount'] += currentAssets['amount']
            # Need ERC721 now
            else:
                return 0, False, "Asset type invalid."
            

        except:
            newObject = {}
            if assetType == ItemTypes['ERC20']:
                newObject[assetId] = {}
                newObject[assetId]['amount'] = asset_object['amount']
            elif assetType == ItemTypes['ERC721']:
                newObject[assetId] = {}
                newObject[assetId]['ids'] = []
                newObject[assetId]['ids'].append(asset_object['id'])
                newObject[assetId]['amount'] = 1
        

        if recs[0]['assets'] != None:
            currentAssets = recs[0]['assets']
            currentAssets[assetId] = newObject[assetId]
        else:
            currentAssets = newObject

        # Store new obj
        self.client.updateRecord(
            {
                'userIdentifier': userIdentifier
            },
            {'assets': currentAssets},
            db=self.databaseName,
            collection=self.collectionName
        )
        return newObject, True, "Items added to user"
        

        
userStore = UserStore()