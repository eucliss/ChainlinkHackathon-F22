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

# TOKEN = web3.Web3.toChecksumAddress(addresses['TOKEN'])
# NFT = web3.Web3.toChecksumAddress(addresses['NFT'])

TOKEN = web3.Web3.toChecksumAddress('0x10000000000000000000000000000000000adEaD')
NFT = web3.Web3.toChecksumAddress('0x20000000000000000000000000000000000adEaD')

CONTROLLER = web3.Web3.toChecksumAddress(addresses['CONTROLLER'])
CONTROLLERPK = addresses['CONTROLLERPK']


ItemTypes = {
    'NATIVE': 0,
    'ERC20': 1,
    'ERC721': 2,
    'ERC1155': 3,
    'NONE': 4
}

@pytest.fixture
def coord():
    return Coordinator()

@pytest.fixture
def assets():
    return [TOKEN, NFT]

@pytest.fixture
def itemTypes():
    return [ItemTypes['ERC20'], ItemTypes['ERC721']]

def test_register_customer(coord):
    res = coord.registerCustomer()
    assert(web3.Web3.isAddress(res))

def test_register_assets(coord, assets, itemTypes):
    invoiceAddress = coord.registerCustomer()
    res = coord.registerAssets(
        invoiceAddress,
        assets,
        itemTypes
    )
    print(res)
    assert(invoiceAddress == res['customer'])
    assert(assets == res['additionalContracts'])
    assert(assets == res['updatedContracts'])
    # print(res)

    
