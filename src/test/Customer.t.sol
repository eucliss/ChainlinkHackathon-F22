// SPDX-License-Identifier: MIT

pragma solidity ^0.8.14;

import "./utils/Helpers.sol";
import {ICustomer, Customer} from "../utils/Customer.sol";

contract CustomerTest is Helpers {
    Customer public c;
    address payable public coordinatorSpoof = payable(address(0xAAAAA));

    function setUp() public {
        c = new Customer(coordinatorSpoof);
    }

    function testConstructor() public {
        assertEq(c.coordinator(), coordinatorSpoof);
    }

    function testDeposit() public {
        vm.deal(bob, initEth);
        vm.prank(bob);
        c.deposit{value: 1 ether}();

        assertEq(bob.balance, initEth - 1 ether);
        assertEq(address(c).balance, 1 ether);
        assertEq(c.balance(), 1 ether);
    }

    function testGhostDeposit() public {
        vm.deal(bob, initEth);
        vm.prank(bob);
        address(c).call{value: 1 ether}("");

        assertEq(bob.balance, initEth - 1 ether);
        assertEq(address(c).balance, 1 ether);
        assertEq(c.balance(), 1 ether);
    }

    function testBill() public {
        vm.deal(bob, initEth);
        vm.prank(bob);
        address(c).call{value: 1 ether}("");

        vm.prank(coordinatorSpoof);
        bool success = c.bill(1 ether);

        assert(success);
        assertEq(address(c).balance, 0);
        assertEq(c.balance(), 0);
        assertEq(coordinatorSpoof.balance, 1 ether);
    }
}
