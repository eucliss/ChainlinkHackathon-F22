// SPDX-License-Identifier: MIT
pragma solidity ^0.8.14;

import "@chainlink/contracts/src/v0.8/interfaces/KeeperCompatibleInterface.sol";
import "./lib/StructsAndEnums.sol";

contract Coordinator is KeeperCompatibleInterface {

    function registerGame() public {
        // Registers a customer (game)
        // Customers add their payable address for billing

    }

    function distributeAssets() public {}


    function checkUpkeep()
        public
        pure
        override
        returns (bool upkeepNeeded, bytes memory performData)
    {
        upkeepNeeded = true;
        performData = bytes("");

        // Checks if upkeep needs to happen
    }

    function performUpkeep(
        bytes calldata /* performData */
    ) external pure override {
        // add some verification
        (bool upkeepNeeded, ) = checkUpkeep("");
        require(upkeepNeeded, "Not Upkeep");
    }
}
