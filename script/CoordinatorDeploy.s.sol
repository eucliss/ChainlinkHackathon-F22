// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.7;

import "forge-std/Script.sol";
import "forge-std/console.sol";
import "./HelperConfig.sol";
import "../src/Coordinator.sol";

contract DeployCoordinator is Script {

    // SET THIS BEFORE DEPLOY
    address public immutable REGISTRAR = address(0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65);


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

        address coord = address(new Coordinator(REGISTRAR));

        vm.stopBroadcast();
        // Idea here is we need to put the contract location in the env
        string memory res =string.concat("COORDINATORADDRESS=", toString(coord));

        console.log("---------------- COORDINATOR ----------------");
        console.log(res);
        console.log("----------------------------------------");
    }
}
