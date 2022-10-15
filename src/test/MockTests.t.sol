pragma solidity ^0.8.14;

import "ds-test/test.sol";
import {Vm} from "@std/Vm.sol";

import {GameERC20} from "../assets/GameERC20.sol";
import {GameERC721} from "../assets/GameERC721.sol";
import {GameERC1155} from "../assets/GameERC1155.sol";

contract ContractTest is DSTest {
    GameERC20 public token;
    GameERC721 public nft;
    GameERC1155 public multiToken;
    Vm cheats = Vm(HEVM_ADDRESS);
    address immutable god = address(0xdead);

    function setUp() public {
        cheats.startPrank(god);
        token = new GameERC20();
        nft = new GameERC721();
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
