-include .env
-include .env.addresses
-include .env.test
-include .env.goerli.addresses

.PHONY: all test clean deploy-anvil

all: clean remove install update build

# Clean the repo
clean  :; forge clean

# Remove modules
remove :; rm -rf .gitmodules && rm -rf .git/modules/* && rm -rf lib && touch .gitmodules && git add . && git commit -m "modules"

install :; forge install smartcontractkit/chainlink-brownie-contracts && forge install rari-capital/solmate && forge install foundry-rs/forge-std && forge install openzeppelin/openzeppelin-contracts && npm install @openzeppelin/contracts

# Update Dependencies
update:; forge update

build:; forge build

test :; forge test -vv

test-gas :; forge test -vv --gas-report

pytest :; pytest -s

snapshot :; forge snapshot

slither :; slither ./src 

format :; prettier --write src/**/*.sol && prettier --write src/*.sol

# solhint should be installed globally
lint :; solhint src/**/*.sol && solhint src/*.sol

anvil :; anvil -m 'test test test test test test test test test test test junk'

# use the "@" to hide the command from your shell 
# deploy-goerli :; @forge script script/${contract}.s.sol:Deploy${contract} --rpc-url ${GOERLI_RPC_URL}  --private-key ${PRIVATE_KEY} --broadcast --verify --etherscan-api-key ${ETHERSCAN_API_KEY}  -vvvv

# This is the private key of account from the mnemonic from the "make anvil" command
deploy-anvil :; @forge script script/CoordinatorDeploy.s.sol:DeployCoordinator --rpc-url http://localhost:8545  --private-key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 --broadcast 
deploy-assets :; @forge script script/AssetDeploy.s.sol:DeployAsset --rpc-url http://localhost:8545  --private-key 0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a --broadcast 

deploy-local :;
	@forge script script/CoordinatorDeploy.s.sol:DeployCoordinator --rpc-url ${local-network}  --private-key ${local-deployer} --broadcast 
	@forge script script/AssetDeploy.s.sol:DeployAsset --rpc-url ${local-network}  --private-key ${local-customer} --broadcast 

deploy-goerli :;
	@forge script script/CoordinatorDeploy.s.sol:DeployCoordinator --rpc-url ${GOERLI_RPC_URL}  --private-key ${DEPLOYERPK} --broadcast --verify --etherscan-api-key ${ETHERSCAN_API_KEY}  -vvvv	

#@forge script script/AssetDeploy.s.sol:DeployAsset --rpc-url ${GOERLI_RPC_URL}  --private-key ${CUSTOMERPK} --broadcast 


deploy-all :; make deploy-${network} contract=APIConsumer && make deploy-${network} contract=KeepersCounter && make deploy-${network} contract=PriceFeedConsumer && make deploy-${network} contract=VRFConsumerV2

mongodb-start :;  brew services start mongodb-community@6.0

mongodb-stop :; brew services stop mongodb-community@6.0