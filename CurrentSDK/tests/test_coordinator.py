from dataclasses import dataclass
from os import kill
from sqlite3 import connect
from typing import Collection
import pytest
import web3
from unittest.mock import patch
from unittest.mock import Mock
from coordinator import Coordinator
from connector import Connector
from dotenv import load_dotenv, dotenv_values

load_dotenv()

addresses = dotenv_values("../.env.addresses")

COORDABI = "../out/Coordinator.sol/Coordinator.json"
COORDADDRESS = web3.Web3.toChecksumAddress(addresses['COORDINATORADDRESS'])


CONTROLLER = web3.Web3.toChecksumAddress(addresses['CONTROLLER'])
CONTROLLERPK = addresses['CONTROLLERPK']

ALICE = web3.Web3.toChecksumAddress('0x11111000000000000000000000000000000A11Ce')
BOB = web3.Web3.toChecksumAddress('0x1111100000000000000000000000000000000B0B')

DATABASE = 'TestingDB'
COLLECTION = 'TestingCustomers'
ASSETCOLLECTION = 'TestingAssets'
USERCOLLECTION = 'TestingUsers'

TESTINGADDRESS = '0x0'
TESTINGUSERNAME = '0xTesting'

ItemTypes = {
    'NATIVE': 0,
    'ERC20': 1,
    'ERC721': 2,
    'ERC1155': 3,
    'NONE': 4
}

@pytest.fixture
def coord():
    return Coordinator(
        database=DATABASE, 
        customerCollection=COLLECTION,
        assetCollection=ASSETCOLLECTION,
        userCollection=USERCOLLECTION)

@pytest.fixture
def assets():
    c = Connector()
    _, TOKEN, _, _ = c.deployContract('GameERC20')
    _, NFT, _, _ = c.deployContract('GameERC721')
    TOKEN = web3.Web3.toChecksumAddress(TOKEN)
    NFT = web3.Web3.toChecksumAddress(NFT)
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
            {'username': userId},
            db=userStore.databaseName, 
            collection=userStore.collectionName
        )
    assert(recs[0]['assets'][assetId]['amount'] > 0)    

def getPackages(assets):
    package1 = {
        'itemType': 1,
        'token': assets[0],
        'identifier': 1,
        'amount': 10
    }
    package2 = {
        'itemType': 2,
        'token': assets[1],
        'identifier': 0,
        'amount': 1
    }
    return [package1, package2]

@pytest.fixture
def recipients():
    return [
        {
            'username': 'ALICE',
            'address': ALICE
        }, {
            'username': 'BOB',
            'address': BOB
        }]

def test_register_customer(coord):
    killDB(coord.customerStore)
    killAssets(coord.assetStore)
    killUsers(coord.userStore)
    res = coord.registerCustomer()
    assert(web3.Web3.isAddress(res['customer']))
    assert(res['controller'] == CONTROLLER)
    objectsInCustomerStore(coord.customerStore, {'invoiceAddress': res['customer']})

def test_get_fees_init(coord):
    killDB(coord.customerStore)
    killAssets(coord.assetStore)
    killUsers(coord.userStore)
    customer = coord.registerCustomer()['customer']
    res = coord.getCustomerBill(invoiceAddress=customer)
    assert(res == 0)
    
def test_get_fees_loaded(coord, assets, itemTypes, recipients):
    killDB(coord.customerStore)
    killAssets(coord.assetStore)
    killUsers(coord.userStore)
    packages = getPackages(assets)

    customer = coord.registerCustomer()['customer']
    res = coord.getCustomerBill(invoiceAddress=customer)
    assert(res == 0)

    usernames = []
    userIds = []
    for user in recipients:
        res, success, msg = coord.userStore.addUser(user['username'],custodial=False, address=user['address'])
        usernames.append(user['username'])
        userIds.append(res)

    res = coord.registerAssets(
        customer,
        assets,
        itemTypes
    )
    res = coord.mintAssets(
        packages,
        usernames
    )
    res = coord.getCustomerBill(invoiceAddress=customer)
    assert(res != 0)



def test_register_assets(coord, assets, itemTypes):
    invoiceAddress = coord.registerCustomer()['customer']
    res = coord.registerAssets(
        invoiceAddress,
        assets,
        itemTypes
    )
    assert(invoiceAddress == res['customer'])
    assert(assets == res['additionalContracts'])
    assert(assets == res['updatedContracts'])
    for item in assets:
        objectsInAssetStore(coord.assetStore, {'assetAddress': item})

def test_mint_assets(coord, recipients, assets, itemTypes):
    packages = getPackages(assets)

    invoiceAddress = coord.registerCustomer()['customer']
    res = coord.registerAssets(
        invoiceAddress,
        assets,
        itemTypes
    )

    usernames = []
    userIds = []
    for user in recipients:
        res, success, msg = coord.userStore.addUser(user['username'],custodial=False, address=user['address'])
        usernames.append(user['username'])
        userIds.append(res)
    res = coord.mintAssets(
        packages,
        usernames
    )
    package1 = {
        'itemType': res['packages'][0][0],
        'token': res['packages'][0][1],
        'identifier': res['packages'][0][2],
        'amount': res['packages'][0][3]
    }
    assert(package1 == packages[0])
    package2 = {
        'itemType': res['packages'][1][0],
        'token': res['packages'][1][1],
        'identifier': res['packages'][1][2],
        'amount': res['packages'][1][3]
    }
    assert(package2 == packages[1])
    for i in range(0, len(packages)):
        assert(res['recipients'][i] == recipients[i]['address'])
        assetInUserStore(coord.userStore, recipients[i]['username'], f'ASS{i+1}')

def test_register_with_assets(coord, assets, itemTypes):
    killAssets(coord.assetStore)
    res = coord.registerWithAssets(
        assets,
        itemTypes
    )
    assert(assets == res['additionalContracts'])
    assert(assets == res['updatedContracts'])
    objectsInCustomerStore(coord.customerStore, {'invoiceAddress': res['customer']})
    for item in assets:
        objectsInAssetStore(coord.assetStore, {'assetAddress': item})


    
