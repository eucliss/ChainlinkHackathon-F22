from dataclasses import dataclass
from sqlite3 import connect
from typing import Collection
import pytest
import web3
from unittest.mock import patch
from unittest.mock import Mock
from connector import Connector
from dotenv import load_dotenv, dotenv_values


load_dotenv()

ItemTypes = {
    'NATIVE': 0,
    'ERC20': 1,
    'ERC721': 2,
    'ERC1155': 3,
    'NONE': 4
}

GAMEERC20 = 'GameERC20'
GAMEERC721 = 'GameERC721'

addresses = dotenv_values("../.env.addresses")

CUSTODIAL = web3.Web3.toChecksumAddress(addresses['CUSTODIAL'])

@pytest.fixture
def connector():
    return Connector()

def test_attach(connector):
    res = connector.attachContract()
    assert 'checkUpkeep' in res.functions
    assert 'performUpkeep' in res.functions

def test_deployContract(connector):
    success, addr, abi, game = connector.deployContract(GAMEERC20)
    assert(success)
    assert(addr != "")
    assert('mint' in game.functions)
    assert(abi != "")

def test_getCustodialBalance(connector):
    w3 = web3.Web3(web3.HTTPProvider('http://127.0.0.1:8545'))
    _, addr, _, _ = connector.deployContract("GameERC20")
    val = connector.getCustodialBalance(addr, "GameERC20")
    assert(val == 0)

    abi, _ = connector.getAbi("GameERC20")
    contract = w3.eth.contract(address=addr, abi=abi)
    tx_hash = contract.functions.mint(
                CUSTODIAL,
                100
            ).transact({'from': CUSTODIAL})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    val = connector.getCustodialBalance(addr, "GameERC20")
    assert(val == 100)

def test_getCustodialBalance_NFT(connector):
    w3 = web3.Web3(web3.HTTPProvider('http://127.0.0.1:8545'))
    _, addr, _, _ = connector.deployContract(GAMEERC721)
    val = connector.getCustodialBalance(addr, GAMEERC721)
    assert(val == 0)


    abi, _ = connector.getAbi(GAMEERC721)
    contract = w3.eth.contract(address=addr, abi=abi)
    tx_hash = contract.functions.mint(
                CUSTODIAL,
                0
            ).transact({'from': CUSTODIAL})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    val = connector.getCustodialBalance(addr, GAMEERC721)

    assert(val == 1)

def test_get_asset_contract(connector):
    # ERC20 
    success, addr, abi, _ = connector.deployContract('ERC20')
    assert(success)
    contract = connector.getAssetContract(addr, ItemTypes['ERC20'])
    assert('name' in contract.functions)
    assert('approve' in contract.functions)
    assert('transfer' in contract.functions)

    # ERC721
    success, addr, abi, _ = connector.deployContract('ERC721')
    assert(success)
    contract = connector.getAssetContract(addr, ItemTypes['ERC721'])
    assert('name' in contract.functions)
    assert('approve' in contract.functions)
    assert('transferFrom' in contract.functions)





