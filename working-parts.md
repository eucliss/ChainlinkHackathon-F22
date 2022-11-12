# TODO:

 - NFT art
 - Goerli testing (minting NFT and seeing in OpenSea)
 - Adding fees from SDK // DONE

## ppt
1. fundamenmtals
2. zero knowledge background
3. problem
4. solution
5. use cases
6. demo


### Slide 1: Introduction

Current
Hybrid-custodial GameFi solution

### Slide 2: Current State Web3 Games
- Some traction
    - People want games with web3 assets

- Ponzinomics
    - Buy this NFT, stake it, play game, win our token

- __Utility__ driven
    - But is it actually utility?

- 0 good graphics, no friend gameplay
    - I dont know 1 person that wants to play these games

### Slide 3: Problem

- Web3 gaming is shitty

- Tokenomics and NFTs dont matter but should
    - VBucks are tied to USD values
    - Skins are covetted

- Current NFT and Token markets are pure speculation
    - CS:GO skin market is not similar

- Too much overhead
    - Navigate to sketchy website
    - Connect Wallet
    - Sign transaction
    - User spends money to do nominal things

- Game Developers hate it
    - They dont want to participate in the massive __scam__

### Slide 4: Solution - Current

2 solutions provided by Current

- Current Hybrid-Custodial wallet
    - No blockchain transactions on the side of the user
    - No worries about private keys or holding your assets
    - Export Whenver you want, no strings

- CurrentSDK
    - No stress building
    - No transactions, no signing, no worrying
    - Game devs dont need to worry about web3 or blockchain, they dont even touch it, CurrentSDK handles everything

### Slide 5: Use Cases

- Gaming - built by gamers for gamers
- Easy Dev - built by devs for devs

Web2 - Web3 transitions
    - AAA (Fortnite, Call of Duty)
        - Migrate VBucks to on-chain ERC20 tokens, distribute to users through CurrentSDK.
            - No hassle, no wallets, just unique accounts
        - Skins migrated to ERC721 or ERC1155 contracts
            - Minimal code changes for devs, no blockchain transactions required
    - Indie
        - Dont worry about your users having wallets or even wanting on chain assets
        - If they want to export they can no problem

Web3 games
    - Super easy SDK for implementing their contracts and assets in their game
    - No transactions required

### Slide 6: Demo Outline

We used a completely unrelated software to build a web3 game - its that easy

Dice roll



## Basic flow for a customer

```
Basically it comes down to three groups:

1. I only want to register as a customer, add assets later.

2. I am a customer and want to add some assets.

3. I have assets but no invoice contract.
```

### Only Register

For this path, customers register by calling the function `registerCustomer` with the address they want to control the invoice contract. The customer will then recieve their invoice address as a response. The customer must send 0.1 ether along with this function to instantiate their invoice contract.

This customer can add assets later on for just gas costs.

### Already a customer, add assets.

For this path, the customer must already have their invoice contract established and be executing on the invoice contracts owner - this was set when they instantiated their account.

The customer then gathers all his asset contracts and their types (erc20, 721, ...) and passes them along to `registerAssets` along with the controller of the assests and their invoice address. 

### I have assets but no account.

For this path, the customer can just call the function `register` with their asset controller and assets similar to above. but without the invoice address. This function will create a cloned invoice contract for them and return the address after execution.

## What happens once I'm done loading and registering?

Now we can distribute assets to your users. You will already have given this contract access to mint and distribute your assets in the game, so now in the SDK we can automatically distribute these assets using our access to this contract. I think my logic is a little screwed up here at the moment, but all the pieces are pretty much set.

Customers can mint their assets directly to users using the mint functionality. Additionally, we're using chainlink automation to automatically bill the customers when their balance exceeds a certain threshold.

One thing I need to figure out is how to take care of all the minting and get this contract owner permissions to mint on all their contracts, thats TBD. Also if a customer wants to distribute Eth then we'll have to transfer Eth from their invoiceAddress. I think to make this even better we should deploy basic ERC20, ERC721, and ERC1155 contracts that allow the user to create assets through out SDK. I dont think this should be done via a web UI, but its certainly a possibility.

# Current State (10/26) and next steps for hackathon.

## Moving parts
- Smart contracts (minimum submission, using chainlink keepers, goerli)
- SDK
- Discord Bot

### Smart Contracts
- Coordinator.sol 
  - This is the main interactive contract for the SDK. It spawns customer contracts when new registrations happen and it bills customers everytime they execute a distribution function or mint new assets to users. Chainlink will hit this contract to check and perform upkeep, the billing is done completely in a decentralized way using the chainlink DON.

  Functions:
  - registerCustomer (address): Creates a new customer contract for a registering customer, requires 0.1 ether to initiate.
  - registerAssets (address, address, address[], ItemType[]): Registers assets to an existing customer. Takes a list of addresses of their item contracts as well as their ItemTypes (ERC20, 721, 1155).
  - registerWithAssets (address, address[], ItemType[]): Registers a new customer along with their assets.
  - distributteAssets (PackageItem[], address[]): Distributes assets to a recipient address. (WIP)
  - mintAssets (PackageItem[], address[]): Mint assets to a recipients address.
  - checkUpkeep (bytes): Chainlink Automation required function. Checks if we need to bill any customers and returns the customers that need billing in bytes form.
  - performUpkeep (bytes): Bills the customers invoice addresses, if they cant pay right now, it adds them back to the paymentsDue array. Will eventually make them un-eligible and lock their asset contracts from execution.

  Getters:
  - getCustomerContractsEncoded (address): Gets an encoded hash of customers asset addresses.
  - getCustomerContracts (address): Gets a list of customer asset addresses.
  - getEligibility (address): Checks if an invoice Address is eligible.

- utils/Customer.sol
  - This contract is an initializable contract that is cloned each time a new customer is registered. It allows the customer to deposit ETH into their account to top up their billing, and it also allows the coordinator contract to withdraw ETH through the bill function.

- lib/StructsAndEnums.sol
  - This function holds all the structs and enums that will be used.

- assets/CurrentToken.sol (Mock ERC20)
- assets/CurrentNFT.sol (Mock ERC721)
- assets/GameERC1155.sol (Mock ERC1155)

### SDK
- connector.py
  - Hook to connect to the chain.
- coordinator.py
  - Python class that wraps the smart contract implementation, allows for easy registering of new customers and adding new assets to their customer profile.
- customerStore.py
  - This will be a layer above the MongoDB implementation. Allows for simpler storing of new customers in the db.
- db.py
  - Mongo DB implementation to store and update users, pretty basic implementation.

### Discord Bot
- bot.py
  - Allows for doing almost everything with the SDK through simple discord commands. This will serve as the demo for chainlink and it will be an open discord for them to test.

### Next steps
The most important thing is to get this project to an MVP.
For the MVP, I will be the primary customer and all my details will be setup prior to the execution of the demo. Future state there will be a way for the customer to register all their shit through a UI or the SDK itself, but for the MVP there will only be 1 customer. Realistically, once the contract is deployed, anyone can register through the smart contract and eventually that will be abstracted out to a UI.
Once the customer is all set the user should be able to go into discord, create an account, play a simple game, and get paid out on chain with whatever assets they win. The user should then be able to export their assets all while the customer is getting billed.

Most of the work needs to be done in the SDK. I'll probably be using hardcoded keys and accounts for the demo, in a production environment there would be a lot more code required to allow for anyone to create a customer through the SDK. Additionally, most of the project is on chain, so it might be better just to build a simple UI to allow any one to register as a customer. In the end that would make sense, kinda like how a standard API works. A customer would register on our website with their wallet, etc., then they would add their asset contracts or use our system to deploy more, then they would fund their invoiceAddress and build out functionality in their game for the SDK. May have to re-architecture this after the hackathon project is submitted. Will also need a UI, will connect all this with Current once we get the UI built out and add in Basin for asset distribution.



