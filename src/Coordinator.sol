// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "@chainlink/contracts/src/v0.8/interfaces/KeeperCompatibleInterface.sol";
import "./lib/StructsAndEnums.sol";

contract Coordinator is KeeperCompatibleInterface {
    // nextBillTime: (block.timestamp + 1 weeks),

    address[] public paymentsDue;

    mapping(address => CustomerStruct) public customers;
    mapping(address => AssetContract) public assets;

    function registerGame(
        address payable invoiceAddress,
        address gameContract,
        address assetController,
        address[] calldata assetContractAddresses,
        ItemType[] calldata assetContractItemTypes
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

        require(assetContractAddresses.length == assetContractItemTypes.length, "Missatch in asset addresses and itemtypes");

        //ToDo: Add details to storage mapping
        customers[invoiceAddress] = CustomerStruct({
            feesDue: 0,
            gameContract: gameContract,
            eligible: true,
            timeToBill: false,
            assetContracts: assetContractAddresses
        });

        uint256 ctLength = assetContractAddresses.length;
        for(uint256 i = 0; i < ctLength; i++){
            // Add contracts to asset contract object and shit
            assets[assetContractAddresses[i]] = AssetContract({
                customer: invoiceAddress,
                executor: assetController,
                itemType: assetContractItemTypes[i]
            });
        }

        // Need to test all this shit
        

    }

    function distributeAssets(
        PackageItem[] calldata assets,
        address[] calldata recipients
    ) public {

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
