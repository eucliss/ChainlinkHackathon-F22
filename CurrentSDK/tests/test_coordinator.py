from dataclasses import dataclass
from sqlite3 import connect
from typing import Collection
import pytest
import web3
from unittest.mock import patch
from unittest.mock import Mock
from coordinator import Coordinator
from dotenv import load_dotenv, dotenv_values

load_dotenv()

addresses = dotenv_values("../.env.addresses")

COORDABI = "../out/Coordinator.sol/Coordinator.json"
COORDADDRESS = web3.Web3.toChecksumAddress(addresses['COORDINATORADDRESS'])

TOKEN = web3.Web3.toChecksumAddress(addresses['TOKEN'])
NFT = web3.Web3.toChecksumAddress(addresses['NFT'])

# TOKEN = web3.Web3.toChecksumAddress('0x101000000000000000000000000000000001dEaD')
# NFT = web3.Web3.toChecksumAddress('0x202000000000000000000000000000000001dEaD')

CONTROLLER = web3.Web3.toChecksumAddress(addresses['CONTROLLER'])
CONTROLLERPK = addresses['CONTROLLERPK']

ALICE = web3.Web3.toChecksumAddress('0x11111000000000000000000000000000000A11Ce')
BOB = web3.Web3.toChecksumAddress('0x1111100000000000000000000000000000000B0B')

DATABASE = 'TestingDB'
COLLECTION = 'TestingCustomers'
ASSETCOLLECTION = 'TestingAssets'
USERCOLLECTION = 'TestingUsers'

ItemTypes = {
    'NATIVE': 0,
    'ERC20': 1,
    'ERC721': 2,
    'ERC1155': 3,
    'NONE': 4
}

@pytest.fixture
def coord():
    return Coordinator(database=DATABASE, collection=COLLECTION)

@pytest.fixture
def assets():
    return [TOKEN, NFT]

@pytest.fixture
def itemTypes():
    return [ItemTypes['ERC20'], ItemTypes['ERC721']]

@pytest.fixture
def packages():
    package1 = {
        'itemType': 1,
        'token': TOKEN,
        'identifier': 1,
        'amount': 10
    }
    package2 = {
        'itemType': 2,
        'token': NFT,
        'identifier': 0,
        'amount': 1
    }
    return [package1, package2]

@pytest.fixture
def recipients():
    return [ALICE, BOB]

def test_register_customer(coord):
    res = coord.registerCustomer()
    assert(web3.Web3.isAddress(res['customer']))
    assert(res['controller'] == CONTROLLER)

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

def test_mint_assets(coord, packages, recipients):
    # No need to register assets cause its already done
    res = coord.mintAssets(
        packages,
        recipients
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
    assert(res['recipients'] == recipients)

def test_register_assets(coord, assets, itemTypes):
    invoiceAddress = coord.registerCustomer()['customer']
    res = coord.registerWithAssets(
        assets,
        itemTypes
    )
    assert(assets == res['additionalContracts'])
    assert(assets == res['updatedContracts'])

    
