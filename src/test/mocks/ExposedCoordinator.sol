// SPDX-License-Identifier: MIT
pragma solidity ^0.8.14;


import "@std/Test.sol";
import "../../Coordinator.sol";
import "../utils/Helpers.sol";

interface IExposedCoordinator {

    function mintAssets(
        PackageItem[] calldata packages,
        address[] calldata recipients
    ) external;

}

contract ExposedCoordinator is Coordinator(address(0xb0b0b0b0b)) {
    
    function bill(address customer) public {
        _billCustomer(customer);
    }
}
