// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "@chainlink/contracts/src/v0.8/interfaces/KeeperCompatibleInterface.sol";
import "./lib/StructsAndEnums.sol";
import "@std/Test.sol";
// import {SafeTransferLib} from "@solmate/src/utils/SafeTransferLib.sol";

interface IERC20 {
    function mint(address to, uint256 amount) external returns(bool);
}
interface IERC721 {
    function mint(address to, uint256 identifier) external returns(bool);
}



contract Coordinator is KeeperCompatibleInterface {
    // using SafeTransferLib for ERC20;
    // using SafeTransferLib for address;
    // nextBillTime: (block.timestamp + 1 weeks),

    event GameRegistered(address invoiceAddress, uint256 contracts);

    address[] public paymentsDue;

    mapping(address => CustomerStruct) public customers;
    mapping(address => AssetContract) public assets;

    function registerGame(
        address payable invoiceAddress, // Address to bill for contract execution
        address gameContract, // Overarching game contract if there is one (not sure why)
        address assetController, // Address of who controlls the asset, call gate (??)
        address[] calldata assetContractAddresses, // Addresses of your Asset contracts
        ItemType[] calldata assetContractItemTypes // ItemTypes of your Asset contracts
    ) public {
        // Registers a customer (game)
        // Customers add their payable address for billing
        // Game address if they have an onchain game
        // Adds their game asset contracts, we'll enforce ownership
        // eventually through ZK proofs onchain
        require(
            customers[invoiceAddress].eligible == false,
            "Invoice Address already registered."
        );

        require(
            assetContractAddresses.length == assetContractItemTypes.length,
            "Missatch in asset addresses and itemtypes"
        );

        //ToDo: Add details to storage mapping
        // Set the customers mapping with the invoice struct
        customers[invoiceAddress] = CustomerStruct({
            feesDue: 0, // 0 fees due to start
            gameContract: gameContract, 
            eligible: true,
            timeToBill: false, // (???)
            assetContracts: assetContractAddresses
        });

        uint256 ctLength = assetContractAddresses.length;
        for (uint256 i = 0; i < ctLength; i++) {
            // Add each contract to assets map
            assets[assetContractAddresses[i]] = AssetContract({
                customer: invoiceAddress, // Who gets billed
                executor: assetController, // Who controlls
                itemType: assetContractItemTypes[i], // What asset type
                eligible: true
            });
        }

        emit GameRegistered(invoiceAddress, ctLength);

        // Need to test all this shit
    }


    // Pretty much wondering what the best way to do this is
    // I think the SDK needs to consider 2 cases:
    // 1. Game developer has a single location with all assets that it is distributing
    // 2. Game developer wants basin to deal with the full distribution and minting
    // I think we'll need 2 functions and I think building out the mint one first
    // is going to be my approach
    function distributeAssets(
        PackageItem[] calldata packages,
        address[] calldata recipients
    ) public {}


    function mintAssets(
        PackageItem[] calldata packages,
        address[] calldata recipients
    ) public 
    {
        console.log(gasleft());
        uint256 packLen = packages.length;
        require(packLen == recipients.length, "Packages and recipients mismatch.");
        // Loop through all the packages
        for(uint256 i = 0; i<packLen; i++) {
            // Mint the package to the user
            require(assets[packages[i].token].eligible, "Contract not registered.");
            _mintPackage(packages[i], recipients[i]);
            // (bool success) = 

            // Add the gas to the transaction cost of the call

        }
        console.log(gasleft());
    }

    function _mintPackage(PackageItem calldata package, address recipient) internal {
        uint256 gas = gasleft();
        // NATIVE
        // if(packages[i].itemType == ItemType.NATIVE){
        //     //
        // }
        // ERC20
        if(package.itemType == ItemType.ERC20){
            bool success = IERC20(package.token).mint(recipient, package.amount);
            require(success, "Mint failed");
        }
        // ERC721
        if(package.itemType == ItemType.ERC721){
            bool success = IERC721(package.token).mint(recipient, package.identifier);
            require(success, "Mint failed");
        }
        // ERC1155
        // if(packages[i].itemType == ItemType.ERC1155){
            
        // }
        // // NONE
        // if(packages[i].itemType == ItemType.NONE){
        
        // }
        gas -= gasleft();
        customers[assets[package.token].customer].feesDue += gas;
    }

    function getCustomerContracts(address invoiceAddress)
        public
        view
        returns (address[] memory)
    {
        return customers[invoiceAddress].assetContracts;
    }

    function getEligibility(address invoiceAddress) public view returns (bool) {
        return customers[invoiceAddress].eligible;
    }

    function checkUpkeep(
        bytes memory /* checkData */
    )
        public
        pure
        override
        returns (bool upkeepNeeded, bytes memory performData)
    {
        upkeepNeeded = true;
        performData = bytes("");

        // Checks if upkeep needs to happen
        // In this instance upkeep is going to be charging customers wallets
        // Essentially using Chainlink automation to bill our users for their
        // Transaction costs
    }

    function performUpkeep(
        bytes calldata /* performData */
    ) external pure override {
        // add some verification
        (bool upkeepNeeded, ) = checkUpkeep("");
        require(upkeepNeeded, "Not Upkeep");

        // Transfers eth from the owners payable address to here
        // This is basically forcing people to pay their bills
        // pauses maintenance window and deletes balances for addrs billed
    }
}
