from dotenv import load_dotenv, dotenv_values
import os
import json
import web3

from db import MongoDB

load_dotenv()

token = os.getenv('INFURA_KEY')
COORDADDRESS = dotenv_values("../.env.addresses")['COORDINATORADDRESS']
COORDABI = "../out/Coordinator.sol/Coordinator.json"

# Connector class will be designed to connect everything to Web3.
class Connector():

    def __init__(self, coordinatorAddress=COORDADDRESS, abi=None):
        """Initialize for the coordinator."""
        self.coordAddress = web3.Web3.toChecksumAddress(coordinatorAddress)
        self.abi = abi
        self.contract = None
        self.w3 = web3.Web3(web3.HTTPProvider('http://127.0.0.1:8545'))
        if not self.w3.isConnected():
            print("Error loading web3 connection")
        self.version = self.w3.clientVersion

        self.attachContract()



    def attachContract(self):
        with open(COORDABI) as json_file:
            data = json.load(json_file)
        self.abi = data['abi']
        self.contract = self.w3.eth.contract(address=self.coordAddress, abi=self.abi)
        return self.contract 


connector = Connector()