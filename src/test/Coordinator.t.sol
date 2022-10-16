// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "../Coordinator.sol";
import "@std/Test.sol";
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
    address public CUSTODIAL = address(0x420420);
    address public NONCUSTODIAL = address(0x1010101);
    GameERC20 public tokenContract;
    GameERC721 public skinsContract;
    GameERC1155 public consumablesContract;

    address public token;
    address public skins;
    address public consumables;

    address[] public assetContracts;
    ItemType[] public assetItemTypes;
    address[] recipients;
    PackageItem[] packages;

    function setUp() public {
        tokenContract = new GameERC20();
        skinsContract = new GameERC721();
        // consumablesContract = new GameERC1155();

        token = address(tokenContract);
        skins = address(skinsContract);
        // consumables = address(consumablesContract);

        assetContracts = [token, skins];
        assetItemTypes = [ItemType.ERC20, ItemType.ERC721];
        recipients = [CUSTODIAL, NONCUSTODIAL];
        PackageItem memory t = PackageItem({
            itemType: ItemType.ERC20,
            token: token,
            identifier: 0,
            amount: 100
        });
        PackageItem memory s = PackageItem({
            itemType: ItemType.ERC721,
            token: skins,
            identifier: 0,
            amount: 1
        });
        packages.push(t);
        packages.push(s);

        coord = new Coordinator();
    }

    function testCheckUpkeepReturnsTrue() public {
        (bool upkeepNeeded, ) = coord.checkUpkeep("0x");
        assertTrue(upkeepNeeded);
    }

    function testRegisterGameStorage() public {
        coord.registerGame(
            invoiceAddress,
            defaultGame,
            assetController,
            assetContracts,
            assetItemTypes
        );
        (, address gameContractRes, bool eligible, ) = coord.customers(
            invoiceAddress
        );
        assertEq(
            gameContractRes,
            defaultGame,
            "Game contracts not set properly."
        );
        assert(eligible);
        address p;
        address e;
        bool elig;
        for(uint256 i = 0; i < assetContracts.length; i++){
            (p, e, ,elig) = coord.assets(assetContracts[i]);
            assertEq(p, invoiceAddress);
            assertEq(e, assetController);
            assert(elig);
        }
    }

    function testGetCustomerContracts() public {
        coord.registerGame(
            invoiceAddress,
            defaultGame,
            assetController,
            assetContracts,
            assetItemTypes
        );

        address[] memory contracts = coord.getCustomerContracts(invoiceAddress);
        assertEq(assetContracts, contracts);
    }

    function testGetCustomerContractsEmpty() public {
        address[] memory contracts = coord.getCustomerContracts(address(0x0));
        assertEq(0, contracts.length);
    }

    function testGetCustomerEligibility() public {
        coord.registerGame(
            invoiceAddress,
            defaultGame,
            assetController,
            assetContracts,
            assetItemTypes
        );

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

    function testMintAssets() public {

        coord.registerGame(
            invoiceAddress,
            defaultGame,
            assetController,
            assetContracts,
            assetItemTypes
        );

        uint256 custBalance = tokenContract.balanceOf(CUSTODIAL);
        uint256 noncustBalance = tokenContract.balanceOf(NONCUSTODIAL);
        assertEq(custBalance, 0);
        assertEq(noncustBalance, 0);

        uint256 custNFTBalance = skinsContract.balanceOf(CUSTODIAL);
        uint256 noncustNFTBalance = skinsContract.balanceOf(NONCUSTODIAL);
        assertEq(custNFTBalance, 0);
        assertEq(noncustNFTBalance, 0);

        (uint256 fees, , , ) = coord.customers(invoiceAddress);
        assertEq(fees, 0);

        
        coord.mintAssets(
            packages,
            recipients
        );


        custBalance = tokenContract.balanceOf(CUSTODIAL);
        noncustBalance = tokenContract.balanceOf(NONCUSTODIAL);
        assertEq(custBalance, 100);
        assertEq(noncustBalance, 0);

        custNFTBalance = skinsContract.balanceOf(CUSTODIAL);
        noncustNFTBalance = skinsContract.balanceOf(NONCUSTODIAL);
        assertEq(custNFTBalance, 0);
        assertEq(noncustNFTBalance, 1);
        
        (fees, , , ) = coord.customers(invoiceAddress);
        console.log(fees);


    }
}
