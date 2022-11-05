pragma solidity ^0.8.14;

import "ds-test/test.sol";
import {Vm} from "@std/Vm.sol";

import {CurrentToken} from "../assets/CurrentToken.sol";
import {CurrentNFT} from "../assets/CurrentNFT.sol";
import {GameERC1155} from "../assets/GameERC1155.sol";

contract ContractTest is DSTest {
    CurrentToken public token;
    CurrentNFT public nft;
    GameERC1155 public multiToken;
    Vm cheats = Vm(HEVM_ADDRESS);
    address immutable god = address(0xdead);

    function setUp() public {
        cheats.startPrank(god);
        token = new CurrentToken();
        nft = new CurrentNFT();
        multiToken = new GameERC1155();
        cheats.stopPrank();
    }

    function testBalances() public {
        // ERC20
        assertEq(token.balanceOf(god), token.INITIAL_SUPPLY());

        // ERC721
        cheats.prank(god);
        nft.mint(god, 0);
        assertEq(nft.balanceOf(god), 1);

        // ERC1155
        assertEq(multiToken.balanceOf(god, 1), 50);
        assertEq(multiToken.balanceOf(god, 69), 50);
        assertEq(multiToken.balanceOf(god, 420), 50);
    }
}
