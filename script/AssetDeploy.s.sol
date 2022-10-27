// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.7;

import "forge-std/Script.sol";
import "forge-std/console.sol";
import "./HelperConfig.sol";
import "../src/assets/GameERC20.sol";
import "../src/assets/GameERC721.sol";

contract AssetDeploy is Script, HelperConfig {

    function toString(address account) public pure returns(string memory) {
        return toString(abi.encodePacked(account));
    }

    function toString(uint256 value) public pure returns(string memory) {
        return toString(abi.encodePacked(value));
    }

    function toString(bytes32 value) public pure returns(string memory) {
        return toString(abi.encodePacked(value));
    }

    function toString(bytes memory data) public pure returns(string memory) {
        bytes memory alphabet = "0123456789abcdef";

        bytes memory str = new bytes(2 + data.length * 2);
        str[0] = "0";
        str[1] = "x";
        for (uint i = 0; i < data.length; i++) {
            str[2+i*2] = alphabet[uint(uint8(data[i] >> 4))];
            str[3+i*2] = alphabet[uint(uint8(data[i] & 0x0f))];
        }
        return string(str);
    }

    function run() external {
        HelperConfig helperConfig = new HelperConfig();

        vm.startBroadcast();

        address token = address(new GameERC20());
        address nft = address(new GameERC721());


        vm.stopBroadcast();
        // Idea here is we need to put the contract location in the env
        string memory resToken = string.concat("TOKEN=", toString(token));
        string memory resNFT = string.concat("NFT=", toString(nft));
    }
}
