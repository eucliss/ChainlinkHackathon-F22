![Current-Banner](img/Twitter-header.png "CurrentSDK-banner")

# Current
## GameFi infrastructure for augmenting Web2 games with decentralized Web3 asset ownership

---------------------------------------------------------------

  ### By Eucliss 

[![Twitter URL](https://img.shields.io/twitter/url/https/twitter.com/Current_GameFi.svg?style=social&label=Follow%20%40Current_GameFi)](https://twitter.com/Current_GameFi)

[![Foundry][foundry-badge]][foundry]

[foundry]: https://getfoundry.sh/
[foundry-badge]: https://img.shields.io/badge/Built%20with-Foundry-FFDB1C.svg

## Description

The goal of the Current project is to bridge the gap between Web2 games and Web3. Our vision is to have open access to web3 for users and developers regardless of their comfort level with web3. We aim to be a hybrid-custodial software solution for developing and using web3 without any of the hassle of onboarding. For the purposes of the Chainlink Hackathon, we built an end-to-end demo of how a user, customer, and developer would utilize Current to build a game that rewarded the user with blockchain assets - No wallets, transactions, or signatures required.

## High level overview

The CurrentSDK is designed to integrate with any Web2 game that implements items or native currencies. For instance: Fortnite or Call of Duty skins and tokens. The game developers can continue their normal workflows of rewarding players with items in their games, the only difference is they need to make a few simple calls to the Current SDK to deliver those items to the users over the blockchain. The users will then have the option to export those assets to their own non-custodial wallet if they'd like.

In this diagram you can see Chainlink at the bottom. Chainlink is responsible for our custom on-chain billing infrastructure. As the SDK executes transactions for the game and users, the game (customer) who is responsible for those transactions gets billed on-chain. Chainlink then executes automations through the Chainlink DON to bill the customers in a decentralized, trustless manner.

![CurrentSDK-easy](/img/Current-Easy-diagram.drawio.png "CurrentSDK-easy")
## Chainlink Hackathon Architecture

For the Chainlink hackathon we extended the above diagram to be specific to a discord app (mock game) we created. The app is extremely simple - it lets you "roll" a dice and recieve rewards. The idea is that this is an overly simplified reward system for a Web2 game not connected to the blockchain. The discord app does not directly touch the chain, that is all handled in the SDK. The app only interacts with the SDK and the database (see for yourself in bot.py). The app allows you to register your discord as a user, then roll the dice to get rewards - this is all handled in a custodial manner. If you want to change your account from custodial to non-custodial, its just one command away (!setAddress), then you can !export your assets to your own address or hold them in the custodial address. Once registered as non-custodial, all future rewards will be sent to your set address. This obfuscates all the unnecessary interactions and transactions from the user, its all in CurrentSDK.

We use chainlink here to bill the customer who deployed the game and connected it to SDK, so we automatically determine how much they owe us for the usage, and use the Chainlink DON to keep our billing decentralized and trustless.

![CurrentSDK](/img/Current-CurrentSDK.drawio.png "CurrentSDK")

## How to run this code

There are 3 things that need to be run to use this code locally and in discord.

1. ANVIL (for local blockchain)
2. MongoDB (for SDK)
3. Discord bot (for the bot)

but first, initializing the repo.

### Initialization && ANVIL

First clone the repo

```git clone git@github.com:eucliss/ChainlinkHackathon-F22.git```

Then run the make commands to initalize the repo

```
make all
```

this does a few things:

  - forge clean
  - removes all modules and libs
  - installs dependencies
  - updates forge
  - builds the contracts

Then to test the contracts:

```
make test
```

Now the contracts should be good to go, we can setup the local anvil instance.

```
make anvil
```

That should make a set of address and private keys for you, you can copy those over to .env.addresses for use in the CurrentSDK.

The addresses you'll need in .env.addresses (dont worry about TOKEN and NFT for now):
```
COORDINATORADDRESS=0x
DEPLOYER=0x
DEPLOYERPK=0x
CUSTODIAL=0x
CUSTODIALPK=0x
CUSTOMER=0x
CUSTOMERPK=0x
REGISTRAR=0x
REGISTRARPK=0x
CONTROLLER=0x
CONTROLLERPK=0x
TOKEN=0x
NFT=0x
```

Now you're set with a local blockchain and some accounts, lets deploy the tokens and the Coordinator.

Setup another env file: .env.test with the following (add local deployer and customer private keys from the other file)

```
local-network=http://localhost:8545

local-deployer=0x
local-customer=0x
```

Then run

```
make deploy-local
```

Within the output of that command you should find the COORDINATOR, TOKEN, and NFT contract addresses - add those to your .env.addresses file.

Now we're good to go with the local blockchain setup, tests passing, and Coordinator deployed with test assets. Next we can setup the MongoDB

### MongoDB setup

This ones easy, install mongo DB through brew: [tutorial](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-os-x/)

```
brew install mongodb-community@6.0
```

Then run the make command to start it:

```
make mongodb-start
```

And to stop it (after you're done):

```
make mongodb-stop
```

Next is the bot

### Discord Bot

For the Discord bot, you'll need to go through the Discord docs to create a new bot and add it to development server.

Once the bot is setup, we'll need some more env variables, setup your .env file to look like the following:
```
GOERLI_RPC_URL=
POLYGON_RPC_URL=
FOUNDRY_SOLC_VERSION=0.8.14
DISCORD_TOKEN=
MONGO_URI=mongodb://localhost:27017
```

That should give us what we need now for the entire bot to function properly.

Navigate to the CurrentSDK directory and run the following to make sure everything works (tests):

```
pytest -sv
```

Then run this command to start the bot:

```
python bot.py
```

If you're having issues where CurrentSDK cant be found fix your path:
```
TOPDIR=${pwd}
export PYTHONPATH=${PYTHONPATH}:${TOPDIR}
```

You should be good to go, navigate to the discord you have setup with the bot and you should be able to interact with your local blockchain through discord commands!

P.S. to test the bot, run `!ping`.

## Discord Bot Commands:
```
1. !register
  The register command is indended to be run for each Discord user who wants to participate in the dice roll game. This adds the user to the database and adds them to the custodial wallets for recieving assets. It is not required for the user to setup their own wallet to gain assets from the roll command, but it is required for them to register with us before running !roll.

2. !roll
  This command rolls a dice for the user (random number). The user has a chance to win 100 tokens, 1000 tokens, or 1000 tokens + 1 NFT based on the outcome of the roll. The assets are automatically stored for the user in the custodial wallet or transfered to the user if they're not custodial.

3. !setAddress <address>
  This command allows a user to set their address for assets to be sent to. If a user sets their address they will not be a custodial customer and will have full control over their assets. All future assets will be distributed to this address instead of the custodial address.
  This command must be run before !export.

4. !export
  This command exports all your assets from the custodial address to the address you set using !setAddress. All the items you own will now be under your control. We will still keep track of your assets for use in the dice roll game in our database.

5. !balance
  This command will show you what we have in our database as your assets.

6. !chainBalance
  This command will tell you what assets you have on chain. If you have not set your address yet this command will tell you to do so - if this is the case the custodial address has all your assets.

----- ADMIN COMMANDS -----

1. !init
  The init function is designed to start the entire process and register the primary customer (us). The command initialized the CONFIG to a state of initialized and also deploys assets to the chain. For our game we have 2 assets: CurrentToken and CurrentNFT. These are simple ERC20 and ERC721 contracts that allow us to mint tokens to the users. For the purposes of this demo we're internalizing everything. In the future we will allow anyone to create a customer in our system and get billed for their usage.


2. !checkChain
  This command checks the chain to determine how many assets the custodial address has.

3. !getBill
  This command checks how much the customers bill is on-chain. The customer will be billed next time the upkeep function is called by Chainlink Automation.

4. !getUserObject
  This command gets the users object from the database. (mainly for testing)

```

## Whats the future look like for Current?

I'm glad you asked ...

```
  1. Space and Time (decentralized database)
    - Currently we run a local mongoDB for easy development and storage of user assets, this will need to become decentralized to ensure we follow the ethos of crypto.

  2. Layer 2 (zk rollups)
    - We intend to use Layer 2 technologies to bolster our product. ZK-rollups are the future of ethereum scaling and we will need that to execute thousands of in-game transactions a second.

  3. Customer authentication through API / SDK (Zero Knowledge proof security)
    - We intend to research how we can utilize zk proofs to confirm an SDK caller is the correct customer thus ensuring that the correct calls are being made and the correct customer is getting billed.
  
  4. True SDK Build out
    - Currently we're only building in python (for dev speed). We'll need to build out the SDK in more languages that work better for gaming
  
  5. Customer portal (UI/UX)
    - The customer will need a portal to perform admin activities (maybe even a __no code solution++?__).
  
  6. Fiat On-Ramp
    - Not everyone wants to transact in crypto only, we'll need a way to make it so users can buy assets in game from a store and execute a transaction through us.
    - We'll also need a way for customers to deposit funds to their smart contract through our UI / UX so they dont even need to touch the chain
  
  7. Asset generation
    - We'll need more smart contracts to allow a customer to deploy assets through us, similar to how we deploy the customer invoice address in our Coordinator.sol
  
  8. Optimization++
    - Custom errors -> Error types
    - LOGGING
```

## Requirements

Please install the following:

-   [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)  
    -   You'll know you've done it right if you can run `git --version`
-   [Foundry / Foundryup](https://github.com/gakonst/foundry)
    -   This will install `forge`, `cast`, and `anvil`
    -   You can test you've installed them right by running `forge --version` and get an output like: `forge 0.2.0 (f016135 2022-07-04T00:15:02.930499Z)`
    -   To get the latest of each, just run `foundryup`

And you probably already have `make` installed... but if not [try looking here.](https://askubuntu.com/questions/161104/how-do-i-install-make)
