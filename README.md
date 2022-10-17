# Custodial Game Assets

## By Euclis

## Basic flow for a customer

```
Basically it comes down to three groups:

1. I only want to register as a customer, add assets later.

2. I am a customer and want to add some assets.

3. I have assets but no invoice contract.
```

#### Only Register

For this path, customers register by calling the function `registerCustomer` with the address they want to control the invoice contract. The customer will then recieve their invoice address as a response. The customer must send 0.1 ether along with this function to instantiate their invoice contract.

This customer can add assets later on for just gas costs.

#### Already a customer, add assets.

For this path, the customer must already have their invoice contract established and be executing on the invoice contracts owner - this was set when they instantiated their account.

The customer then gathers all his asset contracts and their types (erc20, 721, ...) and passes them along to `registerAssets` along with the controller of the assests and their invoice address. 

#### I have assets but no account.

For this path, the customer can just call the function `register` with their asset controller and assets similar to above. but without the invoice address. This function will create a cloned invoice contract for them and return the address after execution.

## What happens once I'm done loading and registering?

Now we can distribute assets to your users. You will already have given this contract access to mint and distribute your assets in the game, so now in the SDK we can automatically distribute these assets using our access to this contract. I think my logic is a little screwed up here at the moment, but all the pieces are pretty much set.

Customers can mint their assets directly to users using the mint functionality. Additionally, we're using chainlink automation to automatically bill the customers when their balance exceeds a certain threshold.

One thing I need to figure out is how to take care of all the minting and get this contract owner permissions to mint on all their contracts, thats TBD. Also if a customer wants to distribute Eth then we'll have to transfer Eth from their invoiceAddress.

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/smartcontractkit/foundry-starter-kit)

Foundry Starter Kit is a repo that shows developers how to quickly build, test, and deploy smart contracts with one of the fastest frameworks out there, [foundry](https://github.com/gakonst/foundry)!


- [Foundry Starter Kit](#foundry-starter-kit)
- [Getting Started](#getting-started)
  - [Requirements](#requirements)
  - [Quickstart](#quickstart)
  - [Testing](#testing)
- [Deploying to a network](#deploying-to-a-network)
  - [Setup](#setup)
  - [Deploying](#deploying)
    - [Working with a local network](#working-with-a-local-network)
    - [Working with other chains](#working-with-other-chains)
- [Security](#security)
- [Contributing](#contributing)
- [Thank You!](#thank-you)
  - [Resources](#resources)
    - [TODO](#todo)

# Getting Started

## Requirements

Please install the following:

-   [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)  
    -   You'll know you've done it right if you can run `git --version`
-   [Foundry / Foundryup](https://github.com/gakonst/foundry)
    -   This will install `forge`, `cast`, and `anvil`
    -   You can test you've installed them right by running `forge --version` and get an output like: `forge 0.2.0 (f016135 2022-07-04T00:15:02.930499Z)`
    -   To get the latest of each, just run `foundryup`

And you probably already have `make` installed... but if not [try looking here.](https://askubuntu.com/questions/161104/how-do-i-install-make)

## Quickstart

```sh
git clone https://github.com/smartcontractkit/foundry-starter-kit
cd foundry-starter-kit
make # This installs the project's dependencies.
make test
```

## Testing

```
make test
```

or

```
forge test
```

# Deploying to a network

Deploying to a network uses the [foundry scripting system](https://book.getfoundry.sh/tutorials/solidity-scripting.html), where you write your deploy scripts in solidity!

## Setup

We'll demo using the Goerli testnet. (Go here for [testnet goerli ETH](https://faucets.chain.link/).)

You'll need to add the following variables to a `.env` file:

-   `GOERLI_RPC_URL`: A URL to connect to the blockchain. You can get one for free from [Alchemy](https://www.alchemy.com/). 
-   `PRIVATE_KEY`: A private key from your wallet. You can get a private key from a new [Metamask](https://metamask.io/) account
    -   Additionally, if you want to deploy to a testnet, you'll need test ETH and/or LINK. You can get them from [faucets.chain.link](https://faucets.chain.link/).
-   Optional `ETHERSCAN_API_KEY`: If you want to verify on etherscan

## Deploying

```
make deploy-goerli contract=<CONTRACT_NAME>
```

For example:

```
make deploy-goerli contract=PriceFeedConsumer
```

This will run the forge script, the script it's running is:

```
@forge script script/${contract}.s.sol:Deploy${contract} --rpc-url ${GOERLI_RPC_URL}  --private-key ${PRIVATE_KEY} --broadcast --verify --etherscan-api-key ${ETHERSCAN_API_KEY}  -vvvv
```

If you don't have an `ETHERSCAN_API_KEY`, you can also just run:

```
@forge script script/${contract}.s.sol:Deploy${contract} --rpc-url ${GOERLI_RPC_URL}  --private-key ${PRIVATE_KEY} --broadcast 
```

These pull from the files in the `script` folder. 

### Working with a local network

Foundry comes with local network [anvil](https://book.getfoundry.sh/anvil/index.html) baked in, and allows us to deploy to our local network for quick testing locally. 

To start a local network run:

```
make anvil
```

This will spin up a local blockchain with a determined private key, so you can use the same private key each time. 

Then, you can deploy to it with:

```
make deploy-anvil contract=<CONTRACT_NAME>
```

Similar to `deploy-goerli`

### Working with other chains

To add a chain, you'd just need to make a new entry in the `Makefile`, and replace `<YOUR_CHAIN>` with whatever your chain's information is. 

```
deploy-<YOUR_CHAIN> :; @forge script script/${contract}.s.sol:Deploy${contract} --rpc-url ${<YOUR_CHAIN>_RPC_URL}  --private-key ${PRIVATE_KEY} --broadcast -vvvv

```

# Security

This framework comes with slither parameters, a popular security framework from [Trail of Bits](https://www.trailofbits.com/). To use slither, you'll first need to [install python](https://www.python.org/downloads/) and [install slither](https://github.com/crytic/slither#how-to-install).

Then, you can run:

```
make slither
```

And get your slither output. 



# Contributing

Contributions are always welcome! Open a PR or an issue!

# Thank You!

## Resources

-   [Chainlink Documentation](https://docs.chain.link/)
-   [Foundry Documentation](https://book.getfoundry.sh/)

### TODO

[ ] Add bash scripts to interact with contracts using `cast`

[ ] Make deploying contracts to `anvil` simpler
