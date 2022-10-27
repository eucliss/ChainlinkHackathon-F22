from dataclasses import dataclass
from sqlite3 import connect
from typing import Collection
import pytest
import web3
from unittest.mock import patch
from unittest.mock import Mock
from connector import Connector

@pytest.fixture
def connector():
    return Connector()

def test_attach(connector):
    res = connector.attachContract()
    assert 'checkUpkeep' in res.functions
    assert 'performUpkeep' in res.functions
