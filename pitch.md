# Current.gg

Revolutionizing asset ownership in digital games.

## Company Purpose

Current is an GameFi infrastructure project whose purpose is to facilitate the shift from Web2 games to Web3 games by allowing businesses and developers to easily integrate Web3 based assets into their existing games. Current will help developers and gaming companies create easy interfaces for their users to utilize and own on-chain assets in-game.

## Problem

Web2 and Web3 gaming do not get along well. There are web2 developers who want no part in NFTs and there are Web3 developers who arent getting any traction with their finance based games. In order for there to be a shift from current gen web2 assets to next gen web3 ownable assets, there needs to be a paradigm shift in how assets are fundamentally handled by games and organizations. This means that games need to be able to distribute rewards and assets to users for in game actions, and users should be able to hold these assets in custodial or non-custodial locations. Users should not be bothered with anything on chain until they elect to do so. On-chain transactions should be opt-in, not required or opt-out. We will not see mass adoption until this is the case.

## Solution

Current will build an SDK to allow any game to easily distribute and award web3 assets to their users without requiring any blockchain interaction on the part of the user. Current will build an asset distribution network on chain that handles the custodial ownership of users assets as well as allowing for non-custodial ownership and export. Current will allow for anyone to register themselves as a customer and execute transactions through the SDK without requiring an entire web3 setup - the only requirement is filling your billing contract with Ether for the Chainlink Decentralized Oracle Network (DON) to bill. Future state Current will allow simple one click asset addition and other management functions through a web UI.

Future State: Current will build out infrastructure for in-game marketplaces to facilitate purchases in USD and other currencies while giving access and ownership on the blockchain. Current will be decentralized enough to allow anyone to use the SDK and the smart contracts, but will be centralized to also deal with the financial requirements our customers will have.

We will be as decentralized as possible, we will deploy to L2s.

Thought: We could build out custome ERC contracts that hold assets in game ecosystems.

## Why Now

Web3 gaming is growing at a steady pace but people are still very skeptical of the NFT ecosystem and the gimicky finance issues that come along with it. We are just starting to see Web2 companies embrace NFTs, however, they are doing it incorrectly. They still see NFTs as collectibles (hence reddit digital collectible), but NFTs are much more than that and we will see them grow to exponentially more than that in the future. The problem is that most current NFTs are attached to a market and are extrememly speculative. This will not always be the case. Web2 companies want to sell and distribute assets with a fixed price in USD and assets that will not be bought/sold entirely based on their speculative value, but on their pure demand value in game. How many people want that item in game?

Example: Dota/CS:GO Skins - Auxillary: Call of Duty / Fortnite without the steam marketplace.
In Dota you have the opportunity to purchase skins and in-game items from the in-game store. These items are allocated to you on steams servers and can be sold on the steam market. These items are not owned by you in their entirety. If your account gets banned you can lose all your items. Additionally, selling these items yield steam dollars, not exportable dollars. There is no speculation in the steam market, items are purchased and sold completely based off supply and demand. Nobody is buying X item to resell it at a higher price, they are buying it to USE it. This is the future of NFTs. Current will be the infrastructure that allows gaming companies to build NFTs that are not speculative, but based on usage and demand only. Dota has thousands of items in-game, CS:GO has thousands, CoD, Fortnite all have thousands. These will be priced at <$20 on average. We need to distribute these efficiently and effectively, they will not be like the NFTs we see today.

Case study: Reddit.
Rebranded NFTs as digital collectables and sold them to their users. Users still required a vault and the assets are purchasable on opensea. This inherently created a market and NFT twitter ran with it. Users on Reddit are now understanding how NFTs will be used in the future. This is step 1.

## Market Size

Its fucking huge.

## Competition

Stardust.gg - They do a similar thing, I think their business model is much different. They require a base fee to use their UI and API to generate Assets in their smart contracts. This may seem like a good idea but it will not attract web2 developrs. As a developer myself, I do not want to be clicking in a UI to add assets. Assets should be easily created through the SDK and developers should have full controll over how the assets are implemented, created, distributed, and purchased. Stardust abstracting any of this logic will lead to poor developer experience and slow growth.

We will build a web3 product that developers cant tangibly feel is web3.

## Product

- Smart contracts: decentralized registration and automatic customer billing from Chainlink DON.
- CurrentSDK: SDK which abstracts all web3 logic away from the developer. Customers will be able to do everything they need through the SDK and any additional requirements can be controlled through our management UI. We will not force structure on the customer and will allow them to develop any custom logic in their smart contracts. We will build a robust testing framework for the customers to test their custom contracts in test-nets before deploying to mainnet.
- Layer2: This will be on Layer2s. Its clear Layer2s are the future and we will deploy Current to multiple Layer2s.

## Business Model

This needs to be thought out a bit more. 

- Smart Contract: On-chain billing for customer usage. Minimum registration fee (?). Base fee per transaction.

- SDK: Free tier, Indie game Tier, Enterprise tier.
    - Transaction based, user based, fee for custodial wallets, same billing strucutre from smart contract (?). 

## Team

Miller - CTO.
Walt (anon) - CFO.

## Financials

@Walt this is you brother.

Heres what we'll need

Smart contract deployment - might cost a few eth (highball), nothing too crazy.
AWS cloud - will need to host some things in the cloud to take care of execution of customer transactions and database storing. Scales with growth. Initial stages cheap.
Salaries - Not required until full-time. Hard cap at $200k.
Devs - yeah we'll need a lot of these.
Other headcount - Going to need to flesh this out a bit more too.