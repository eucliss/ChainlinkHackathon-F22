
## Elevator Pitch

Current is a hybrid-custodial software integration layer for web2 games to provide and reward their users with web3 assets without any of the overhead of connecting and transacting with blockchains.


## Blockchain gaming is inaccessible
what inspired you, what you learned, how you built your project, and the challenges you faced.

The inspiration for this project started over a year ago and has morphed into something completely different. At first, the project was designed to solve the issue of fairness in digital tournamnets: some gaming tournaments complete and winners have to wait weeks or months for their winnings - thats not right. We wanted to streamline this and put it on chain for immediate pay out in gaming tournamnets. That was the inspiration behind a project of mine, [Basin](https://github.com/eucliss/Basin). I then went to Chainlink SmartCon 2022 and told everyone about it which generated some traction and started some really good conversations. By the end of the conference, I realized that Basin was not the right approach, and that there were some fundamental issues with crypto gaming - thats what started this hackathon project.

The two main drivers are:

1. Crypto based games suck.
  There is way too much overhead just to play a shitty crypto game, and nobody wants to build on crypto games cause its extremely complicated for developers and end users.

2. Chainlink Hackathon.
  Basin needed help. Only crypto native users would consider using it, and it needed a much larger infrastructure behind it to make it useful. Thats what lead us to Chainlink Automation which was a perfect application for the hackathon.

We decided to restart the whole distribution idea and build our Chainlink Hackathon project around these two points. The future state goal of this project is to design a system that allows anyone to build fast, state-of-the-art games on top of our SDK and obfuscate all blockchain related processes from both the users as well as the developers. This is a completely new idea from Basin and requires brand new smart contracts, infrastructure, and acceessiblity.

## What even is Current? And why sometimes CurrentSDK?

Current is a custodial web3 asset solution designed for web2 games. CurrentSDK is the software development kit that is designed for game developers to utilize in their games. We built Current and the CurrentSDK so that developers could obfuscate all blockchain details away from their users (and themselves)! You can see the power of the CurrentSDK by joining our Discord and using the !roll functionality in the __dice roll__ channel. This channel allows for any user to roll a dice and earn blockchain based rewards, no wallet connection or transactions required. Just log in, register in the channel, and win rewards. The discord bot is just to demo the CurrentSDKs power and the connectivity to the blockchain - ideally a skilled developer would come in and build a whole AAA game on top of the CurrentSDK - its built by devs, for devs.

## UI's are cool, but devs run the world

Some other companies trying this project are focused on building a UI and UX for companies to use blockchain assets in web2 games. We're the opposite. It's all about the devs - and all about easy access for them.

The developers should be able to easily build on top of our software and deliver blockchain based assets to their users, and the users should have a completely seemless experience earning blockchain assets and exporting them to their own non-custodial wallet (if they want). On top of this, the user and the developer should NEVER see a transaction, they should never have to connect a wallet, connect to a blockchain, wait for execution of a transaction, etc. We should take care of all of that. This is how we onboard the masses to crypto: take out the crypto and make it a true backend. 

In our model (future state), a developer should be able to make a simple call to our API/SDK to deliver an asset to a user, this can be in the form of ERC20, ERC721 or ERC1155. The developer only needs to know what the item is, and whats its identifier is, we will handle all the mapping and allocating and everything else. Then the developer just needs to check our database for what items the user has (or their own DB in the future). The user on the other hand, just needs to play the game. When they're rewarded an item, we will store it at our custodial address and note in the database what assets the user has. From a UI/UX standpoint, there is no blockchain interaction or lag. A user does something in game (!roll) and they recieve an asset. When they decided they're ready to become non-custodial, they can set their blockchain address (!setAddress) through a UI, and export (!export) their assets to their non-custodial address. From then on, we store their address in the database and automatically send them all future rewards from the game. This allows for a completely seemless experience for the user, no more connect wallet, sketchy websites, sign transactions, scared of getting hacked, etc. We will control assets on our end - similar to how Coinbase works.

## Transactions cost money, how are you covering the cost??

This is where our smart contracts and Chainlink comes in. We have infrastructure setup to allow a new customer to register on chain. When they do so they are given a new implementation of our Customer contract and they fund it with a small fee (0.1eth). Everytime we mint an asset to a user or our custodial address, we add the transaction cost to the customers object on chain and will bill them later. This is billing through code. Then we use the chainlink DON to automate our billing process and ensure a decentralized approach to collecting fees. We have additional functionality being built out to allow for the registration address of the SDK to bill users for other transactions they incure through the SDK. This will all be open source and transparent (besides our private key of course)!

This is a big reason to use Chainlink, the Decentralized Oracle Network (DON). Customers dont have to rely on us to create billing statements or charge them for their usage and they can completely trust the Chainlink DON for automated execution of their invoice contract (Customer.sol). This allows us to build an awesome product that connects games to the blockchain, allows customers to pay us fairly through decentralized code execution, and allows users and developers to have a completely obfuscated experience with blockchain assets in their games.

## So why did you build it like this, wheres the website?

For the hackathon project we decided to switch it up a bit. We didnt build a website where you go and connect your wallet and run some transactions. __Remember we're an SDK for devs, not web users!__ In true Web3 fashion, we used discord. You can join our discord today and play our dice roll game for free. It's a really simple game that simulates a dice roll. Sometimes you'll win 100 tokens, sometimes 1000, and sometimes an NFT. All of this in discord with no wallet requirements. Just !register with your discord username and you're ready to collect some web3 assets. When you're ready, follow the instructions to export them to your own wallet.

We chose to do it this way because:
  1. Its different - sending transactions through discord?? Thats not normal
  2. People are familiar with Discord and already use it - no sketchy websites.
  3. The discord bot required 1 file - the real power is in the SDK.

With using Discord, we wanted to show something: There is no custom logic handling transactions in the UI - its all in the SDK. You can read the code executing the Discord bot, it only interacts with the coordinator and the database, there isnt any javascript asking for signature or connecting a wallet or executing transactions. This simulates a real game. In an online game, when you're rewarded with items or tokens, you arent required to sign a transaction and accept them, they just show up in your inventory. Thats how the bot works. Once you're registered, just roll the dice and earn tokens - super simple.

## Take aways

There were some lessons learned while building this thing. 

Custodial solutions are very hard to build. Seems pretty simple from the outside, but building the architecture for the software and how we're going to charge customers was a very difficult problem. This project took many different iterations and architecture diagrams to figure out how we were going to connect the off-chain data with the on-chain costs - and how we would automate the fund collection and asset management. Chainlink automation was a clear winner for us, the only issue was figuring out what exactly it was going to do, and how we were going to automate the data flow in our smart contracts.

Databases are not fun to work with. I'd much rather build a smart contract and use on-chain storage than remember all the information required for users off-chain (and there are still some big issues we need to address).

I learned that tooling is incredibly important. I'm looking forward to some time after the hackathon to fix the Makefile, our python tests (mocks!), and our foundry tests (cheats, helpers, configurations, multi-chain). Theres been quite a bit of tech debt created just to get the product out the door. That leads me to the next section, there is a ton of work to be done in the future for Current.

## Current++

In the future state there are a few things we are considering to enhance our decentralized architecture and make the experience better for users and developers.
  
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

This is the starting point of the company Current. We plan on building out the Current ecosystem to facilitate the web2 to web3 paradigm shift in gaming. We will onboard users and make their lives easier while also providing more ownership of assets and a trustless system of interaction. This is how we onboard games and users to Web3.

