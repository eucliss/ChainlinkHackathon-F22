from dataclasses import dataclass
from os import kill
from sqlite3 import connect
from typing import Collection
import pytest
import web3
from unittest.mock import patch
from unittest.mock import Mock
from customerStore import CustomerStore
from assetStore import AssetStore
from userStore import UserStore

from dotenv import load_dotenv, dotenv_values

load_dotenv()

addresses = dotenv_values("../.env.addresses")

TOKEN = web3.Web3.toChecksumAddress('0x101000000000000000000000000000000001dEaD')
NFT = web3.Web3.toChecksumAddress('0x202000000000000000000000000000000001dEaD')
CUSTODIAL = web3.Web3.toChecksumAddress(addresses['CUSTODIAL'])

ItemTypes = {
    'NATIVE': 0,
    'ERC20': 1,
    'ERC721': 2,
    'ERC1155': 3,
    'NONE': 4
}

DATABASE = 'TestingDB'
COLLECTION = 'TestingCustomers'
ASSETCOLLECTION = 'TestingAssets'
USERCOLLECTION = 'TestingUsers'

TESTINGADDRESS = '0x101000000000000000000000000000000001dEaD'
TESTINGUSERNAME = '0xTesting'

@pytest.fixture
def store():
    return CustomerStore(
        database=DATABASE,
        collection=COLLECTION
        )

@pytest.fixture
def assetStore():
    return AssetStore(
        database=DATABASE,
        collection=ASSETCOLLECTION
        )

@pytest.fixture
def userStore():
    return UserStore(
        database=DATABASE,
        collection=USERCOLLECTION
        )

@pytest.fixture
def assets():
    return [TOKEN, NFT]

@pytest.fixture
def itemTypes():
    return [ItemTypes['ERC20'], ItemTypes['ERC721']]

def killDB(store):
    store.client.kill(DATABASE, COLLECTION)

def killAssets(assetStore):
    assetStore.client.kill(DATABASE, ASSETCOLLECTION)

def killUsers(userStore):
    userStore.client.kill(DATABASE, USERCOLLECTION)

def testKillDB(store):
    killDB(store)
    customerId, success, mes = store.addNewCustomer(TESTINGADDRESS)
    assert(success)
    customerId, success, mes = store.addNewCustomer(TESTINGADDRESS)
    assert(not success)
    assert(mes == "Invoice address already a customer")
    killDB(store)
    customerId, success, mes = store.addNewCustomer(TESTINGADDRESS)
    assert(success)
    assert(mes == "Successfully stored new customer")

def objectsInCustomerStore(store, obj):
    recs = store.client.getRecord(
            obj, 
            db=store.databaseName, 
            collection=store.collectionName
        )
    assert(len(recs) == 1)

def objectsInAssetStore(store, obj):
    recs = store.client.getRecord(
            obj,
            db=store.databaseName, 
            collection=store.collectionName
        )
    assert(len(recs) == 1)

def objectsInUserStore(store, obj):
    recs = store.client.getRecord(
            obj,
            db=store.databaseName, 
            collection=store.collectionName
        )
    assert(len(recs) == 1)

def assetInUserStore(userStore, userId, assetId):
    recs = userStore.client.getRecord(
            {'userIdentifier': userId},
            db=userStore.databaseName, 
            collection=userStore.collectionName
        )
    assert(recs[0]['assets'][assetId]['amount'] > 0)    

def test_add_new_customer(store):
    killDB(store)
    prevNumber = store.nextCustomerIdentifier
    nextId = store.nextCustomerIdentifier
    customerId, success, mes = store.addNewCustomer(TESTINGADDRESS)
    assert(success)
    assert(f'CUST{nextId}' == customerId)
    assert(prevNumber + 1 == store.nextCustomerIdentifier)
    assert(mes == "Successfully stored new customer")
    objectsInCustomerStore(store, {'customerIdentifier': customerId})

def test_get_id_from_address(store):
    killDB(store)
    customerId, success, mes = store.addNewCustomer(TESTINGADDRESS)
    res = store.getCustomerIdFromInvoiceAddress(TESTINGADDRESS)
    assert(res == customerId)

def test_get_address_from_id(store):
    killDB(store)
    customerId, success, mes = store.addNewCustomer(TESTINGADDRESS)
    print(customerId)
    res = store.getCustomerInvoiceAddress(customerId)
    assert(res == TESTINGADDRESS)
    
def test_add_new_assets(store, assetStore, assets, itemTypes):
    killDB(store)
    killAssets(assetStore)
    identifier, success, _ = store.addNewCustomer(TESTINGADDRESS)
    assert(success)
    resObj, success, mes = assetStore.addAssets(
        identifier,
        assets,
        itemTypes
    )
    assert(success)
    assert(mes == "Successfully stored new assets")

    for i in range(0, len(resObj)):
        t = resObj[i]
        assert(t['assetIdentifier'] == f'ASS{i + 1}')
        assert(t['customerIdentifier'] == identifier)
        assert(t['assetAddress'] == assets[i])
        assert(t['itemType'] == itemTypes[i])
        objectsInAssetStore(assetStore, {'assetIdentifier': f'ASS{i + 1}'})

    
def test_add_with_assets(store, assetStore, assets, itemTypes):
    killDB(store)
    killAssets(assetStore)

    resObj, success, mes = store.addCustomerWithAssets(
        TESTINGADDRESS,
        assets,
        itemTypes,
        assetStore
    )
    assert(resObj['customerIdentifier'] == 'CUST1')
    assert(success)
    assert(mes == "Successfully created new customer and added assets.")

    for i in range(0, len(resObj['assetsAdded'])):
        t = resObj['assetsAdded'][i]
        assert(t['assetIdentifier'] == f'ASS{i + 1}')
        assert(t['customerIdentifier'] == resObj['customerIdentifier'])
        assert(t['assetAddress'] == assets[i])
        assert(t['itemType'] == itemTypes[i])
        objectsInAssetStore(assetStore, {'assetIdentifier': f'ASS{i + 1}'})

    objectsInCustomerStore(store, {'customerIdentifier': resObj['customerIdentifier']})

def test_add_user(userStore):
    killUsers(userStore)

    userIdentifier, success, mes = userStore.addUser(
        TESTINGUSERNAME
    )
    assert(userIdentifier == 'USE1')
    assert(success)
    assert(mes == "Successfully stored new user.")
    objectsInUserStore(userStore, {'userIdentifier': 'USE1'})
    recs = userStore.client.getRecord(
        {'userIdentifier': 'USE1'},
        db=userStore.databaseName, 
        collection=userStore.collectionName
    )
    assert(recs[0]['username'] == TESTINGUSERNAME)
    assert(recs[0]['custodial'] == True)
    assert(recs[0]['address'] == CUSTODIAL)
    assert(recs[0]['assets'] == None)
    

def test_add_asset_to_user(store, userStore, assetStore, assets, itemTypes):
    killDB(store)
    killAssets(assetStore)
    killUsers(userStore)

    resObj, success, mes = store.addCustomerWithAssets(
        TESTINGADDRESS,
        assets,
        itemTypes,
        assetStore
    )
    userIdentifier, success, mes = userStore.addUser(
        TESTINGUSERNAME
    )

    for item in resObj['assetsAdded']:
        assetId = item['assetIdentifier']
        asset_obj = {
            'assetIdentifier': assetId,
            'amount': 10,
            'id': 1
        }
        res, success, msg = userStore.addAssetItemToUser(
            userIdentifier,
            asset_obj,
            assetStore
        )
        databaseItem = userStore.client.getRecord(
                {
                    'userIdentifier': userIdentifier
                }, 
                db=userStore.databaseName, 
                collection=userStore.collectionName
            )[0]
        assets = databaseItem['assets']
        if item['itemType'] == ItemTypes['ERC20']:
            assert(assets[assetId]['amount'] == 10)
        elif item['itemType'] == ItemTypes['ERC721']:
            assert(assets[assetId]['amount'] == 1)
            assert(assets[assetId]['ids'] == [1])
        assert(len(assets[assetId].keys()) > 0)
        assetInUserStore(userStore, userIdentifier, assetId)

def test_add_multiple_assets_to_user(store, userStore, assetStore, assets, itemTypes):
    killDB(store)
    killAssets(assetStore)
    killUsers(userStore)

    resObj, success, mes = store.addCustomerWithAssets(
        TESTINGADDRESS,
        assets,
        itemTypes,
        assetStore
    )
    userIdentifier, success, mes = userStore.addUser(
        TESTINGUSERNAME
    )

    # Multiple ERC additions

    assetId = resObj['assetsAdded'][0]['assetIdentifier']
    asset_obj = {
        'assetIdentifier': assetId,
        'amount': 10,
    }

    res, success, msg = userStore.addAssetItemToUser(
        userIdentifier,
        asset_obj,
        assetStore
    )
    assets = userStore.getUserAssets(TESTINGUSERNAME)
    assert(assets[assetId]['amount'] == 10)

    res, success, msg = userStore.addAssetItemToUser(
        userIdentifier,
        asset_obj,
        assetStore
    )
    assets = userStore.getUserAssets(TESTINGUSERNAME)
    print(assets)
    assert(assets[assetId]['amount'] == 20)

def test_add_multiple_nfts_to_user(store, userStore, assetStore, assets, itemTypes):
    killDB(store)
    killAssets(assetStore)
    killUsers(userStore)

    resObj, success, mes = store.addCustomerWithAssets(
        TESTINGADDRESS,
        assets,
        itemTypes,
        assetStore
    )
    userIdentifier, success, mes = userStore.addUser(
        TESTINGUSERNAME
    )

    # Multiple ERC additions

    assetId = resObj['assetsAdded'][1]['assetIdentifier']
    asset_obj = {
        'assetIdentifier': assetId,
        'amount': 1,
        'id': 0
    }

    res, success, msg = userStore.addAssetItemToUser(
        userIdentifier,
        asset_obj,
        assetStore
    )
    assets = userStore.getUserAssets(TESTINGUSERNAME)
    assert(assets[assetId]['amount'] == 1)
    assert(assets[assetId]['ids'] == [0])

    asset_obj = {
        'assetIdentifier': assetId,
        'amount': 1,
        'id': 1
    }
    res, success, msg = userStore.addAssetItemToUser(
        userIdentifier,
        asset_obj,
        assetStore
    )
    assets = userStore.getUserAssets(TESTINGUSERNAME)
    print(assets)
    assert(assets[assetId]['amount'] == 2)
    assert(assets[assetId]['ids'] == [0, 1])


    

