from dotenv import load_dotenv, dotenv_values
import os
import json
import web3

from db import MongoDB

load_dotenv()

ItemTypes = {
    'NATIVE': 0,
    'ERC20': 1,
    'ERC721': 2,
    'ERC1155': 3,
    'NONE': 4
}

token = os.getenv('INFURA_KEY')
addresses = dotenv_values("../.env.addresses")

COORDADDRESS = dotenv_values("../.env.addresses")['COORDINATORADDRESS']
COORDABI = "../out/Coordinator.sol/Coordinator.json"

BASINADDRESS = dotenv_values("../.env.addresses")['BASINADDRESS']
BASINABI = "../out/Basin.sol/Basin.json"

CUSTODIAL = web3.Web3.toChecksumAddress(addresses['CUSTODIAL'])
CUSTODIALPK = addresses['CUSTODIALPK']
REGISTRAR = web3.Web3.toChecksumAddress(addresses['REGISTRAR'])


# Connector class will be designed to connect everything to Web3.
class Connector():

    def __init__(self, coordinatorAddress=COORDADDRESS, abi=None, basinAddress=BASINADDRESS):
        """Initialize for the coordinator."""
        self.coordAddress = web3.Web3.toChecksumAddress(coordinatorAddress)
        self.basinAddress = web3.Web3.toChecksumAddress(basinAddress)
        self.abi = abi
        self.contract = None
        self.basin = None
        self.w3 = web3.Web3(web3.HTTPProvider('http://127.0.0.1:8545'))
        if not self.w3.isConnected():
            print("Error loading web3 connection")
        self.version = self.w3.clientVersion
        self.attachContract()
        self.attachBasin()


    def attachContract(self):
        with open(COORDABI) as json_file:
            data = json.load(json_file)
        self.abi = data['abi']
        self.contract = self.w3.eth.contract(address=self.coordAddress, abi=self.abi)
        return self.contract 
    
    def attachBasin(self):
        with open(BASINABI) as json_file:
            data = json.load(json_file)
        abi = data['abi']
        self.basin = self.w3.eth.contract(address=self.basinAddress, abi=abi)
        return self.basin
    
    def getAbi(self, contractString):
        """
            returns abi, bytecode
        """
        location = f'../out/{contractString}.sol/{contractString}.json'
        with open(location) as json_file:
            data = json.load(json_file)
        return data['abi'], data['bytecode']['object']

    def getAssetContract(self, address, itemType):
        if itemType == ItemTypes['ERC20']:
            abi, _ = self.getAbi('ERC20')
            return self.w3.eth.contract(address=address, abi=abi)
        if itemType == ItemTypes['ERC721']:
            abi, _ = self.getAbi('ERC721')
            return self.w3.eth.contract(address=address, abi=abi)


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
                web3.Web3.toChecksumAddress(CUSTODIAL)
            ).call({'from': CUSTODIAL})
            return res
        except:
            return "BROKEN CONTRACT"
    
    def getUserBalance(self, userAddress, contractAddress, contractString):
        abi, _ = self.getAbi(contractString)
        contract = self.w3.eth.contract(address=contractAddress, abi=abi)
        print("CONTRACT")
        print(contract.all_functions())
        res = contract.functions.balanceOf(
                web3.Web3.toChecksumAddress(userAddress)
            ).call({'from': REGISTRAR})
        print(res)
        try: 
            res = contract.functions.balanceOf(
                web3.Web3.toChecksumAddress(userAddress)
            ).call({'from': REGISTRAR})
            return res
        except:
            return "BROKEN CONTRACT"

connector = Connector()