// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./utils/Helpers.sol";


contract CoordinatorTest is Helpers {

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

        
        coord.mintAssets(
            packages,
            recipients
        );
        coord.mintAssets(
            packages2,
            recipients2
        );


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
        coord.registerGame(
            invoiceAddress,
            defaultGame,
            assetController,
            assetContracts,
            assetItemTypes
        );
        
        coord.mintAssets(
            packages,
            recipients
        );

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
        
        coord.mintAssets(
            packages,
            recipients
        );
        coord.mintAssets(
            packages2,
            recipients2
        );

        bytes memory billsBytes = coord.getEncodedRequiredBills();

        address[] memory billsRequired = abi.decode(billsBytes, (address[]));

        (bool upkeepRequired, bytes memory data) = coord.checkUpkeep("");

        require(upkeepRequired, "Upkeep should be required here.");

        address[] memory resCustomers = abi.decode(data, (address[]));

        assertEq(resCustomers.length, 2);
        assertEq(resCustomers[0], invoiceAddress);
        assertEq(resCustomers[1], invoiceAddress2);
    }

    function testPerformUpkeep() public {
        vm.deal(invoiceAddress, 1 ether);
        coord.registerGame(
            invoiceAddress,
            defaultGame,
            assetController,
            assetContracts,
            assetItemTypes
        );
        
        coord.mintAssets(
            packages,
            recipients
        );

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
        assert(bill);

        // Expect the number of bills required to be 0
        billsBytes = coord.getEncodedRequiredBills();
        billsRequired = abi.decode(billsBytes, (address[]));
        assertEq(billsRequired.length, 0);
    }

    // Failure to pay bills case

}

