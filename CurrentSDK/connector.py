from re import T
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
STAGE = os.getenv('STAGE')
addresses = ''
CHAIN_ID = 1
if STAGE == 'dev':
    PROVIDER = os.getenv('LOCAL_RPC')
    addresses = addresses = dotenv_values("../.env.addresses")
    CHAIN_ID = 31337
if STAGE == 'goerli':
    PROVIDER = os.getenv('GOERLI_RPC_URL')
    addresses = dotenv_values("../.env.goerli.addresses")
    CHAIN_ID = 5

COORDADDRESS = addresses['COORDINATORADDRESS']
COORDABI = "../out/Coordinator.sol/Coordinator.json"

CUSTODIAL = web3.Web3.toChecksumAddress(addresses['CUSTODIAL'])
CUSTODIALPK = addresses['CUSTODIALPK']

CONTROLLER = web3.Web3.toChecksumAddress(addresses['CONTROLLER'])
CONTROLLERPK = addresses['CONTROLLERPK']

REGISTRAR = web3.Web3.toChecksumAddress(addresses['REGISTRAR'])
REGISTRARPK = addresses['REGISTRARPK']


# Connector class will be designed to connect everything to Web3.
class Connector():

    def __init__(self, coordinatorAddress=COORDADDRESS, abi=None):
        """Initialize for the coordinator."""
        self.coordAddress = web3.Web3.toChecksumAddress(coordinatorAddress)
        self.abi = abi
        self.contract = None
        self.w3 = web3.Web3(web3.HTTPProvider(PROVIDER))
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
    
    # def attachBasin(self):
    #     with open(BASINABI) as json_file:
    #         data = json.load(json_file)
    #     abi = data['abi']
    #     self.basin = self.w3.eth.contract(address=self.basinAddress, abi=abi)
    #     return self.basin
    
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


    def getSignedDeployTx(self, ct):
        nonce = self.w3.eth.get_transaction_count(REGISTRAR)
        txn = ct.constructor().build_transaction({
            'chainId': CHAIN_ID,
            'gas': 10000000,
            'maxFeePerGas': self.w3.toWei('10', 'gwei'),
            'maxPriorityFeePerGas': self.w3.toWei('10', 'gwei'),
            'nonce': nonce
        })
        print(txn)
        signed_tx = self.w3.eth.account.sign_transaction(txn, private_key=REGISTRARPK)
        res = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash = self.w3.toHex(self.w3.keccak(signed_tx.rawTransaction))
        return tx_hash
    
    def signRegisterCustomer(self, coord, value, customer):
        nonce = self.w3.eth.get_transaction_count(REGISTRAR)
        txn = coord.functions.registerCustomer(
            customer
        ).build_transaction({
            'chainId': CHAIN_ID,
            'gas': 1000000,
            'maxFeePerGas': self.w3.toWei('50', 'gwei'),
            'maxPriorityFeePerGas': self.w3.toWei('50', 'gwei'),
            'nonce': nonce,
            'value': value
        })
        signed_tx = self.w3.eth.account.sign_transaction(txn, private_key=REGISTRARPK)
        res = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash = self.w3.toHex(self.w3.keccak(signed_tx.rawTransaction))
        return tx_hash
    
    # transferPackagesToRecipients
        # transfer
        # transferFrom

    def transferERC20(self, ct, recipient, amount):
        nonce = self.w3.eth.get_transaction_count(CUSTODIAL)
        txn = ct.functions.transfer(
            recipient,
            amount
        ).build_transaction({
            'chainId': CHAIN_ID,
            'gas': 1000000,
            'maxFeePerGas': self.w3.toWei('50', 'gwei'),
            'maxPriorityFeePerGas': self.w3.toWei('50', 'gwei'),
            'nonce': nonce
        })
        signed_tx = self.w3.eth.account.sign_transaction(txn, private_key=CUSTODIALPK)
        res = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash = self.w3.toHex(self.w3.keccak(signed_tx.rawTransaction))
        return tx_hash
    
    def transferERC721(self, ct, recipient, identifier):
        nonce = self.w3.eth.get_transaction_count(CUSTODIAL)
        txn = ct.functions.transferFrom(
            CUSTODIAL,
            recipient,
            identifier
        ).build_transaction({
            'chainId': CHAIN_ID,
            'gas': 1000000,
            'maxFeePerGas': self.w3.toWei('50', 'gwei'),
            'maxPriorityFeePerGas': self.w3.toWei('50', 'gwei'),
            'nonce': nonce
        })
        signed_tx = self.w3.eth.account.sign_transaction(txn, private_key=CUSTODIALPK)
        res = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash = self.w3.toHex(self.w3.keccak(signed_tx.rawTransaction))
        return tx_hash
    
    def registerAssets(self, coord, customerInvoice, assetAddresses, assetItemTypes):
        nonce = self.w3.eth.get_transaction_count(CONTROLLER)
        txn = coord.functions.registerAssets(
            CONTROLLER,
            customerInvoice,
            assetAddresses,
            assetItemTypes
        ).build_transaction({
            'chainId': CHAIN_ID,
            'gas': 10000000,
            'maxFeePerGas': self.w3.toWei('10', 'gwei'),
            'maxPriorityFeePerGas': self.w3.toWei('10', 'gwei'),
            'nonce': nonce
        })
        signed_tx = self.w3.eth.account.sign_transaction(txn, private_key=CONTROLLERPK)
        res = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash = self.w3.toHex(self.w3.keccak(signed_tx.rawTransaction))
        return tx_hash
    
    def mintAssets(self, coord, packages, addresses):
        nonce = self.w3.eth.get_transaction_count(CONTROLLER, 'pending')
        txn = coord.functions.mintAssets(
            packages,
            addresses
        ).build_transaction({
            'chainId': CHAIN_ID,
            'gas': 10000000,
            'maxFeePerGas': self.w3.toWei('10', 'gwei'),
            'maxPriorityFeePerGas': self.w3.toWei('10', 'gwei'),
            'nonce': nonce
        })
        signed_tx = self.w3.eth.account.sign_transaction(txn, private_key=CONTROLLERPK)
        res = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash = self.w3.toHex(self.w3.keccak(signed_tx.rawTransaction))
        return tx_hash
    
    def registerWithAssets(self, coord, assetAddresses, assetItemTypes, value):
        nonce = self.w3.eth.get_transaction_count(CONTROLLER, 'pending')
        txn = coord.functions.registerWithAssets(
            CONTROLLER,
            assetAddresses,
            assetItemTypes
        ).build_transaction({
            'chainId': CHAIN_ID,
            'gas': 10000000,
            'maxFeePerGas': self.w3.toWei('10', 'gwei'),
            'maxPriorityFeePerGas': self.w3.toWei('10', 'gwei'),
            'nonce': nonce,
            'value': value
        })
        signed_tx = self.w3.eth.account.sign_transaction(txn, private_key=CONTROLLERPK)
        res = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash = self.w3.toHex(self.w3.keccak(signed_tx.rawTransaction))
        return tx_hash
    
    # Register Assets
    # getCustomerBill ?
    # mintAssets
    # registerWithAssets
    # bill customer



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
        # tx_hash = ct.constructor().transact()
        tx_hash = self.getSignedDeployTx(ct)
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(tx_receipt)
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
        res = contract.functions.balanceOf(
                web3.Web3.toChecksumAddress(userAddress)
            ).call({'from': REGISTRAR})
        try: 
            res = contract.functions.balanceOf(
                web3.Web3.toChecksumAddress(userAddress)
            ).call({'from': REGISTRAR})
            return res
        except:
            return "BROKEN CONTRACT"

    #____
    def signBillCustomer(self, ct, invoiceAddress, amount):
        nonce = self.w3.eth.get_transaction_count(REGISTRAR)
        txn = ct.functions.addFeesToCustomer(
            invoiceAddress,
            amount
        ).build_transaction({
            'chainId': CHAIN_ID,
            'gas': 10000000,
            'maxFeePerGas': self.w3.toWei('10', 'gwei'),
            'maxPriorityFeePerGas': self.w3.toWei('10', 'gwei'),
            'nonce': nonce,
        })
        signed_tx = self.w3.eth.account.sign_transaction(txn, private_key=REGISTRARPK)
        res = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash = self.w3.toHex(self.w3.keccak(signed_tx.rawTransaction))
        return tx_hash

    def billCustomer(self, tx_reciept, invoiceAddress):
        # tx = self.contract.functions.addFeesToCustomer(
        #     invoiceAddress,
        #     tx_reciept.cumulativeGasUsed
        # ).transact({'from': REGISTRAR})
        tx = self.signBillCustomer(
            self.contract,
            invoiceAddress,
            tx_reciept.cumulativeGasUsed
        )
        bill_reciept = self.w3.eth.wait_for_transaction_receipt(tx)
        event = self.contract.events.AddedFeesToCustomer().processReceipt(bill_reciept)
        event = event[0]['args']
        return event



connector = Connector()