// SPDX-License-Identifier: MIT

pragma solidity ^0.8.14;

import "./utils/Helpers.sol";

contract CoordinatorTest is Helpers {
    function setUp() public {
        tokenContract = new CurrentToken();
        skinsContract = new CurrentNFT();
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

        coord = new Coordinator(REGISTRAR);

        vm.deal(bob, initEth + 0.1 ether);
        vm.prank(bob);
        invoiceAddress = payable(
            coord.registerWithAssets{value: 0.1 ether}(
                bob,
                assetContracts,
                assetItemTypes
            )
        );
    }

    function testConstructor() public {
        coord = new Coordinator(REGISTRAR);
        assert(coord.REGISTRAR() == REGISTRAR);
        assert(coord.customerLogic() != address(0));
    }

    function testRegisterCustomer() public {
        coord = new Coordinator(REGISTRAR);
        vm.prank(bob);
        address customer = coord.registerCustomer{value: 0.1 ether}(bob);
        assert(customer != address(0));

        assertEq(bob.balance, initEth - 0.1 ether);
        assertEq(customer.balance, 0.1 ether);

        (uint256 fees, , bool eligible, ) = coord.customers(customer);

        assertEq(fees, 0);
        assertTrue(eligible);
    }

    function testWithdraw() public {
        coord = new Coordinator(REGISTRAR);
        vm.deal(address(coord), 1 ether);
        assertEq(address(coord).balance, 1 ether);
        uint256 bal = REGISTRAR.balance;
        vm.prank(REGISTRAR);
        coord.withdraw();
        assertEq(REGISTRAR.balance, bal + 1 ether);
        assertEq(address(coord).balance, 0);
    }

    function testSetOwner() public {
        coord = new Coordinator(REGISTRAR);
        vm.prank(bob);
        vm.expectRevert("Not the owner");
        coord.setOwner(bob);
        assertEq(coord.OWNER(), REGISTRAR);

        vm.prank(REGISTRAR);
        coord.setOwner(bob);
        assertEq(coord.OWNER(), bob);
    }

    function testAddFeesToCustomer() public {
        coord = new Coordinator(REGISTRAR);
        vm.prank(bob);
        address customer = coord.registerCustomer{value: 0.1 ether}(bob);
        (uint256 fees, , bool eligible, ) = coord.customers(customer);
        assertEq(fees, 0);
        assertTrue(eligible);

        vm.prank(REGISTRAR);
        coord.addFeesToCustomer(customer, 1 ether);
        bool bill;
        (fees, , eligible, bill) = coord.customers(customer);
        assertEq(fees, 1 ether);
        assertTrue(bill);

        bytes memory billsBytes = coord.getEncodedRequiredBills();
        address[] memory billsRequired = abi.decode(billsBytes, (address[]));
        assertEq(billsRequired.length, 1);
    }

    function testRegisterAssets() public {
        // Takes a list of assets and list of item types
        // adds the assets to the asset registry
        // adds the items to the customers index
        coord = new Coordinator(REGISTRAR);
        vm.startPrank(bob);
        address customer = coord.registerCustomer{value: 0.1 ether}(bob);
        coord.registerAssets(bob, customer, assetContracts, assetItemTypes);

        // Assert assets are loaded into the customer object
        address[] memory contracts = coord.getCustomerContracts(bob);
        assertEq(assetContracts, assetContracts);

        address resCustomer;
        address resExecutor;
        ItemType resType;
        bool resEligible;

        // Test for assets indexed in the asset contracts
        for (uint256 i = 0; i < assetContracts.length; i++) {
            (resCustomer, resExecutor, resType, resEligible) = coord.assets(
                assetContracts[i]
            );

            assertEq(resCustomer, customer);
            assertEq(resExecutor, bob);
            require(resType == assetItemTypes[i]);
            assertTrue(resEligible);
        }
    }

    function testRegisterGameStorage() public {
        (, , bool eligible, ) = coord.customers(invoiceAddress);

        assertTrue(eligible, "Not eligible");
        address p;
        address e;
        bool elig;
        for (uint256 i = 0; i < assetContracts.length; i++) {
            (p, e, , elig) = coord.assets(assetContracts[i]);
            assertEq(p, invoiceAddress, "Invoice Addresses are not equal");
            assertEq(e, bob, "Asset controllers are not equal");
            assertTrue(elig, "Asset contract not set to eligible");
        }
    }

    function testGetCustomerContracts() public {
        address[] memory contracts = coord.getCustomerContracts(invoiceAddress);
        assertEq(assetContracts, contracts);
    }

    function testGetCustomerContractsEmpty() public {
        address[] memory contracts = coord.getCustomerContracts(address(0x0));
        assertEq(0, contracts.length);
    }

    function testGetCustomerEligibility() public {
        bool eligible = coord.getEligibility(invoiceAddress);
        assert(eligible);
    }

    function testGetCustomerEligibilityEmpty() public {
        bool eligible = coord.getEligibility(address(0x0));
        assert(!eligible);
    }

    function testMintAssets() public {
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

        vm.prank(bob);
        coord.mintAssets(packages, recipients);

        custBalance = tokenContract.balanceOf(CUSTODIAL);
        noncustBalance = tokenContract.balanceOf(NONCUSTODIAL);
        assertEq(custBalance, 100);
        assertEq(noncustBalance, 0);

        custNFTBalance = skinsContract.balanceOf(CUSTODIAL);
        noncustNFTBalance = skinsContract.balanceOf(NONCUSTODIAL);
        assertEq(custNFTBalance, 0);
        assertEq(noncustNFTBalance, 1);

        bool bill;
        (fees, , , bill) = coord.customers(invoiceAddress);
        assert(fees > 0);
        assert(bill);
    }

    function testMintAssetsMultiple() public {
        setUpMultiInvoiceAndRegister();

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
        (fees, , , ) = coord.customers(invoiceAddress2);
        assertEq(fees, 0);

        vm.prank(bob);
        coord.mintAssets(packages, recipients);
        vm.prank(assetController);
        coord.mintAssets(packages2, recipients2);

        custBalance = tokenContract.balanceOf(CUSTODIAL);
        noncustBalance = tokenContract.balanceOf(NONCUSTODIAL);
        assertEq(custBalance, 100);
        assertEq(noncustBalance, 0);

        custNFTBalance = skinsContract.balanceOf(CUSTODIAL);
        noncustNFTBalance = skinsContract.balanceOf(NONCUSTODIAL);
        assertEq(custNFTBalance, 0);
        assertEq(noncustNFTBalance, 1);

        bool bill;
        (fees, , , bill) = coord.customers(invoiceAddress);
        assert(fees > 0);
        assert(bill);

        (fees, , , bill) = coord.customers(invoiceAddress2);
        assert(fees > 0);
        assert(bill);
    }

    function testUpkeep() public {
        vm.prank(bob);
        coord.mintAssets(packages, recipients);

        bytes memory billsBytes = coord.getEncodedRequiredBills();

        address[] memory billsRequired = abi.decode(billsBytes, (address[]));

        (bool upkeepRequired, bytes memory data) = coord.checkUpkeep("");

        require(upkeepRequired, "Upkeep should be required here.");

        address[] memory resCustomers = abi.decode(data, (address[]));

        assertEq(resCustomers.length, 1);
        assertEq(resCustomers[0], invoiceAddress);
    }

    function testMultipleInvoiceUpkeep() public {
        setUpMultiInvoiceAndRegister();

        vm.prank(bob);
        coord.mintAssets(packages, recipients);
        vm.prank(assetController);
        coord.mintAssets(packages2, recipients2);

        bytes memory billsBytes = coord.getEncodedRequiredBills();

        address[] memory billsRequired = abi.decode(billsBytes, (address[]));

        (bool upkeepRequired, bytes memory data) = coord.checkUpkeep("");

        require(upkeepRequired, "Upkeep should be required here.");

        address[] memory resCustomers = abi.decode(data, (address[]));

        assertEq(resCustomers.length, 2);
        assertEq(resCustomers[0], invoiceAddress);
        assertEq(resCustomers[1], invoiceAddress2);
    }

    function testPerformUpkeepLag() public {
        setUpMultiInvoiceAndRegister();

        vm.prank(bob);
        coord.mintAssets(packages, recipients);

        (bool upkeepRequired, bytes memory data) = coord.checkUpkeep("");

        vm.prank(assetController);
        coord.mintAssets(packages2, recipients2);

        (uint256 fees, , , bool bill) = coord.customers(invoiceAddress);
        (uint256 fees2, , , bool bill2) = coord.customers(invoiceAddress2);

        // Testing to make sure if there is any lag in the upkeep and TXs get
        // submitted in between that we dont lose any addresses in the billing
        bytes memory billsBytes = coord.getEncodedRequiredBills();
        require(keccak256(billsBytes) != keccak256(data), "Bytes not equal.");
        address[] memory billsRequired = abi.decode(billsBytes, (address[]));

        coord.performUpkeep(data);

        // Expect the balance of the customer to go down - fees
        assertEq(invoiceAddress.balance, 0.1 ether - fees);
        assertEq(invoiceAddress2.balance, 0.1 ether - fees2);
        // Expect balance of contract to go up + fees
        assertEq(address(coord).balance, fees + fees2);

        // Expect ready to bill for the invoice to be false
        (fees, , , bill) = coord.customers(invoiceAddress);
        assertEq(fees, 0);
        assert(!bill);

        (fees2, , , bill2) = coord.customers(invoiceAddress);
        assertEq(fees2, 0);
        assert(!bill2);

        // Expect the number of bills required to be 0
        billsBytes = coord.getEncodedRequiredBills();
        billsRequired = abi.decode(billsBytes, (address[]));
        assertEq(billsRequired.length, 0);
    }

    function testPerformUpkeep() public {
        vm.deal(invoiceAddress, 1 ether);

        vm.prank(bob);
        coord.mintAssets(packages, recipients);

        bytes memory billsBytes = coord.getEncodedRequiredBills();
        address[] memory billsRequired = abi.decode(billsBytes, (address[]));
        assertEq(billsRequired.length, 1);
        assertEq(billsRequired[0], invoiceAddress);

        // bool bill;
        (uint256 fees, , , bool bill) = coord.customers(invoiceAddress);
        assert(fees > 0);
        assert(bill);

        // Perform the upkeep
        coord.performUpkeep(billsBytes);

        // Expect the balance of the customer to go down - fees
        assertEq(invoiceAddress.balance, 1 ether - fees);
        // Expect balance of contract to go up + fees
        assertEq(address(coord).balance, fees);

        // Expect ready to bill for the invoice to be false
        (fees, , , bill) = coord.customers(invoiceAddress);
        assertEq(fees, 0);
        assert(!bill);

        // Expect the number of bills required to be 0
        billsBytes = coord.getEncodedRequiredBills();
        billsRequired = abi.decode(billsBytes, (address[]));
        assertEq(billsRequired.length, 0);
    }

    // Failure to pay bills case

    function testBill() public {
        setUpExposed();
        vm.deal(invoiceAddress, 1 ether);
        vm.prank(bob);
        exCoord.mintAssets(packages, recipients);

        (uint256 fees, , , bool bill) = exCoord.customers(invoiceAddress);
        assert(fees > 0);
        assert(bill);

        exCoord.bill(invoiceAddress);
        assertEq(address(exCoord).balance, fees);

        (fees, , , bill) = exCoord.customers(invoiceAddress);
        assert(fees == 0);
        assert(!bill);
    }
}
