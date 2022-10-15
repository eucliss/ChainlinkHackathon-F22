// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "../Coordinator.sol";
import "forge-std/Test.sol";
import "./utils/Cheats.sol";

import {GameERC20} from "../assets/GameERC20.sol";
import {GameERC721} from "../assets/GameERC721.sol";
import {GameERC1155} from "../assets/GameERC1155.sol";

contract CoordinatorTest is Test {
    Coordinator public coord;
    Cheats internal constant cheats = Cheats(HEVM_ADDRESS);

    address payable public invoiceAddress = payable(address(0xB0B));
    address public defaultGame = address(0xAAA);
    address public assetController = address(0xA11CE);
    GameERC20 public tokenContract;
    GameERC721 public skinsContract;
    GameERC1155 public consumablesContract;

    address public token;
    address public skins;
    address public consumables;

    address[] public assetContracts;
    ItemType[] public assetItemTypes;

    function setUp() public {
        tokenContract = new GameERC20();
        skinsContract = new GameERC721();
        // consumablesContract = new GameERC1155();

        token = address(tokenContract);
        skins = address(skinsContract);
        // consumables = address(consumablesContract);

        assetContracts = [token, skins];
        assetItemTypes = [ItemType.ERC20, ItemType.ERC20];
        

        coord = new Coordinator();
    }

    function testCheckUpkeepReturnsTrue() public {
        (bool upkeepNeeded, ) = coord.checkUpkeep("0x");
        assertTrue(upkeepNeeded);
    }

    function testRegisterGameStorage() public {
        coord.registerGame(invoiceAddress, defaultGame, assetController, assetContracts, assetItemTypes);
        (, address gameContractRes, bool eligible, ) = coord.customers(
            invoiceAddress
        );
        assertEq(
            gameContractRes,
            defaultGame,
            "Game contracts not set properly."
        );
        assert(eligible);
    }

    function testGetCustomerContracts() public {
        coord.registerGame(invoiceAddress, defaultGame, assetController, assetContracts, assetItemTypes);

        address[] memory contracts = coord.getCustomerContracts(invoiceAddress);
        assertEq(assetContracts, contracts);
    }

    function testGetCustomerContractsEmpty() public {
        address[] memory contracts = coord.getCustomerContracts(address(0x0));
        assertEq(0, contracts.length);
    }

    function testGetCustomerEligibility() public {
        coord.registerGame(invoiceAddress, defaultGame, assetController, assetContracts, assetItemTypes);

        bool eligible = coord.getEligibility(invoiceAddress);
        assert(eligible);
    }

    function testGetCustomerEligibilityEmpty() public {
        bool eligible = coord.getEligibility(address(0x0));
        assert(!eligible);
    }

    // function testFuzzingExample(bytes memory variant) public {
    //     // We expect this to fail, no matter how different the input is!
    //     cheats.expectRevert(bytes("Time interval not met"));
    //     counter.performUpkeep(variant);
    // }
}
