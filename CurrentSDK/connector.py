from dotenv import load_dotenv, dotenv_values
import os
import json
import web3

from db import MongoDB

load_dotenv()

token = os.getenv('INFURA_KEY')
addresses = dotenv_values("../.env.addresses")

COORDADDRESS = dotenv_values("../.env.addresses")['COORDINATORADDRESS']
COORDABI = "../out/Coordinator.sol/Coordinator.json"

CUSTODIAL = web3.Web3.toChecksumAddress(addresses['CUSTODIAL'])
CUSTODIALPK = addresses['CUSTODIALPK']

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
    
    def getAbi(self, contractString):
        """
            returns abi, bytecode
        """
        location = f'../out/{contractString}.sol/{contractString}.json'
        with open(location) as json_file:
            data = json.load(json_file)
        return data['abi'], data['bytecode']['object']
    

    def deployContract(self, contractString=None):
        """
            contractString must be in the out folder

            returns (
                contractAddress,
                ABI,
                contract
            )
        """
        if contractString == None:
            return False, "ERROR no contract selected", "", ""
        abi, bytecode = self.getAbi(contractString)
        ct = self.w3.eth.contract(abi=abi, bytecode=bytecode)
        tx_hash = ct.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        c = self.w3.eth.contract(
            address=tx_receipt.contractAddress,
            abi=abi
        )
        return True, tx_receipt.contractAddress, abi, c

    def getCustodialBalance(self, contractAddress, contractString):
        abi, _ = self.getAbi(contractString)
        contract = self.w3.eth.contract(address=contractAddress, abi=abi)

        try: 
            res = contract.functions.balanceOf(
                CUSTODIAL
            ).call({'from': CUSTODIAL})
            return res
        except:
            return "BROKEN CONTRACT"



connector = Connector()