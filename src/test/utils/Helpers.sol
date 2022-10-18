// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "../../Coordinator.sol";
import "@std/Test.sol";
import "../utils/Cheats.sol";
import "../mocks/ExposedCoordinator.sol";

import {GameERC20} from "../../assets/GameERC20.sol";
import {GameERC721} from "../../assets/GameERC721.sol";
import {GameERC1155} from "../../assets/GameERC1155.sol";

contract Helpers is Test {
    Coordinator public coord;
    ExposedCoordinator public exCoord;
    Cheats internal constant cheats = Cheats(HEVM_ADDRESS);

    address payable public bob = payable(address(0xB0B));
    address payable public invoiceAddress = payable(address(0xB1B));
    address payable public invoiceAddress2 = payable(address(0xB0B1111));
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
    address[] public assetContracts2;
    ItemType[] public assetItemTypes2;
    address[] recipients;
    address[] recipients2;
    PackageItem[] packages;
    PackageItem[] packages2;

    uint256 public immutable initEth = 10 ether;


    function setUpMultiInvoiceAndRegister() public {

        tokenContract = new GameERC20();
        skinsContract = new GameERC721();
        // consumablesContract = new GameERC1155();

        token = address(tokenContract);
        skins = address(skinsContract);
        // consumables = address(consumablesContract);

        assetContracts = [token];
        assetItemTypes = [ItemType.ERC20];
        recipients = [CUSTODIAL];


        delete packages;
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
        packages2.push(s);

        coord = new Coordinator();
        
        vm.deal(bob, 0.1 ether);
        vm.deal(assetController, 0.1 ether);
        
        vm.prank(bob);
        invoiceAddress = payable(coord.registerWithAssets{value: 0.1 ether}(
            bob,
            assetContracts,
            assetItemTypes
        ));


        assetContracts2 = [skins];
        assetItemTypes2 = [ItemType.ERC721];
        recipients2 = [NONCUSTODIAL];

        vm.prank(assetController);
        invoiceAddress2 = payable(coord.registerWithAssets{value: 0.1 ether}(
            assetController,
            assetContracts2,
            assetItemTypes2
        ));

        (, address gameContractRes, bool eligible, ) = coord.customers(
            invoiceAddress
        );
        assert(eligible);

        (, , eligible, ) = coord.customers(
            invoiceAddress2
        );
        assert(eligible);

    }

    function setUpExposed() public {
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
        delete packages;
        packages.push(t);
        packages.push(s);

        exCoord = new ExposedCoordinator();

        vm.deal(bob, initEth + 0.1 ether);
        vm.prank(bob);
        invoiceAddress = payable(exCoord.registerWithAssets{value: 0.1 ether}(
            bob,
            assetContracts,
            assetItemTypes
        ));
    }
}

