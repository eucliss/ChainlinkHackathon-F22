// SPDX-License-Identifier: MIT
pragma solidity ^0.8.14;

import "@chainlink/contracts/src/v0.8/interfaces/KeeperCompatibleInterface.sol";
import "./lib/StructsAndEnums.sol";
import "@std/Test.sol";
import { ICustomer, Customer } from "./utils/Customer.sol";
import {Clones} from "@oz/proxy/Clones.sol";

interface IERC20 {
    function mint(address to, uint256 amount) external returns(bool);
}
interface IERC721 {
    function mint(address to, uint256 identifier) external returns(bool);
}



contract Coordinator is KeeperCompatibleInterface {
    // using SafeTransferLib for ERC20;
    // using SafeTransferLib for address;
    // nextBillTime: (block.timestamp + 1 weeks),

    event GameRegistered(address invoiceAddress, uint256 contracts);
    event CustomerRegistered(address customer, address controller);
    event AddedAssetsToCustomer(
        address customer, 
        address[] additionalContracts, 
        address[] updatedContracts
    );
    event MintedAssets(
        PackageItem[] packages,
        address[] recipients
    );

    address public immutable customerLogic;
    address public immutable REGISTRAR;
    uint256 public initialDeposit = 0.1 ether;

    address[] public paymentsDue;

    mapping(address => CustomerStruct) public customers;
    mapping(address => AssetContract) public assets;

    modifier equalAssetsAndTypes(address[] calldata assetContracts, ItemType[] calldata itemTypes) {
        require(
            assetContracts.length == itemTypes.length,
            "Missatch in asset addresses and itemtypes"
        );
        _;
    }

    constructor(address _registrar) {
        customerLogic = address(new Customer(address(this)));
        REGISTRAR = _registrar;
    }

    receive() external payable {}

    fallback() external payable {}

    // Note: For clone reasoning
    // May need to setup an invoice contract type
    // Where the user registers an invoice contract
    // Then pre-loads it with ethereum
    // The bill customer will then attempt to bill the invoice address
    // We can build like a clone factory for those invoiced wallets
    // Will only have 2 functions
    // Bill, deposit (later on we can add more for ERC20 payments, etc.)
    // But for now just eth is good

    // Register a customer
    // This creates a cloned customerLogic which will become their billing address
    function registerCustomer(
        address assetController
    ) public payable returns(address customer) {
        require(msg.value >= initialDeposit, "Incorrect msg.value, send >0.1 ether");
        
        customer = Clones.clone(customerLogic);
        ICustomer(customer).initialize(assetController);

        // Send some eth to the customer to initialize it
        customer.call{value: msg.value}("");

        // Finish adding the customer object to the registry
        customers[customer].eligible = true;
        emit CustomerRegistered(customer, assetController);
    }

    // TODO: Security concerns, require owner from Customer contract adding to invoice addr;
    //  require assets not already eligible
    //  require customer invoice isnt locked
    // Register an array of assets to your customer address
    function registerAssets(
        address assetController,
        address customerInvoice,
        address[] calldata assetContractAddresses, // Addresses of your Asset contracts
        ItemType[] calldata assetContractItemTypes // ItemTypes of your Asset contracts
    ) 
        public 
        payable 
        equalAssetsAndTypes(assetContractAddresses, assetContractItemTypes) 
    {
        // Check validity
        require(ICustomer(customerInvoice).getOwner() == msg.sender, "Not Invoice Owner");
        require(customers[customerInvoice].eligible, "Customer Invoice is not eligible.");


        uint256 len = assetContractAddresses.length;
        for(uint8 i = 0; i < len; i++) {
            // Add asset objects
            require(!assets[assetContractAddresses[i]].eligible, "Asset is already registered.");

            assets[assetContractAddresses[i]] = AssetContract({
                customer: customerInvoice, // Who gets billed
                executor: assetController, // Who controlls
                itemType: assetContractItemTypes[i], // What asset type
                eligible: true
            });
            customers[customerInvoice].assetContracts.push(assetContractAddresses[i]);
        }

        emit AddedAssetsToCustomer(
            customerInvoice, 
            assetContractAddresses, 
            customers[customerInvoice].assetContracts
        );
    }

    // Regiser and 
    function registerWithAssets(
        address assetController,
        address[] calldata assetContractAddresses, // Addresses of your Asset contracts
        ItemType[] calldata assetContractItemTypes // ItemTypes of your Asset contracts
    ) external payable returns(address customer) {
        customer = registerCustomer(assetController);
        registerAssets(assetController, customer, assetContractAddresses, assetContractItemTypes);
    }

    // Pretty much wondering what the best way to do this is
    // I think the SDK needs to consider 2 cases:
    // 1. Game developer has a single location with all assets that it is distributing
    // 2. Game developer wants basin to deal with the full distribution and minting
    // I think we'll need 2 functions and I think building out the mint one first
    // is going to be my approach
    function distributeAssets(
        PackageItem[] calldata packages,
        address[] calldata recipients
    ) public {}

    // Mint assets 
    function mintAssets(
        PackageItem[] calldata packages,
        address[] calldata recipients
    ) public 
    {
        uint256 packLen = packages.length;
        require(packLen == recipients.length, "Packages and recipients mismatch.");
        // Loop through all the packages
        for(uint256 i = 0; i<packLen; i++) {
            // Mint the package to the user
            require(assets[packages[i].token].eligible, "Contract not registered.");
            require(assets[packages[i].token].executor == msg.sender, "Not the asset executor.");
            _mintPackage(packages[i], recipients[i]);
        }
        emit MintedAssets(packages, recipients);
    }

    // Mint a singular package to a singular address
    function _mintPackage(PackageItem calldata package, address recipient) internal {
        uint256 gas = gasleft();
        address assetLocation = package.token;
        // NATIVE
        // if(packages[i].itemType == ItemType.NATIVE){
        //     //
        // }

        // ERC20
        if(package.itemType == ItemType.ERC20){
            bool success = IERC20(assetLocation).mint(recipient, package.amount);
            require(success, "Mint failed");
        }
        // ERC721
        if(package.itemType == ItemType.ERC721){
            bool success = IERC721(assetLocation).mint(recipient, package.identifier);
            require(success, "Mint failed");
        }
        // ERC1155
        // if(packages[i].itemType == ItemType.ERC1155){
            
        // }
        // // NONE
        // if(packages[i].itemType == ItemType.NONE){
        
        // }
        CustomerStruct storage c = customers[assets[package.token].customer];
        if(c.setToBill != true){
            c.setToBill = true;
            paymentsDue.push(assets[package.token].customer);
        }

        gas -= gasleft();
        customers[assets[assetLocation].customer].feesDue += gas;
    }

    function getCustomerContractsEncoded(address invoiceAddress)
        public
        view
        returns (bytes memory)
    {
        return abi.encode(customers[invoiceAddress].assetContracts);
    }

    function getCustomerContracts(address invoiceAddress)
        public
        view
        returns (address[] memory)
    {
        return customers[invoiceAddress].assetContracts;
    }

    function getEligibility(address invoiceAddress) public view returns (bool) {
        return customers[invoiceAddress].eligible;
    }

    function checkUpkeep(
        bytes memory /* checkData */
    )
        public
        view
        override
        returns (bool upkeepNeeded, bytes memory performData)
    {           
        // delete paymentsDue;
        return paymentsDue.length > 0 ?
            (true, abi.encode(paymentsDue)) :
            (false, abi.encode(paymentsDue));

        // If payments due has shit in it, return true and the list in perform data
        // If not we go no billing required

        // Checks if upkeep needs to happen
        // In this instance upkeep is going to be charging customers wallets
        // Essentially using Chainlink automation to bill our users for their
        // Transaction costs
    }

    function performUpkeep(
        bytes memory performData
    ) external override {
        // add some verification
        // (bool upkeepNeeded, ) = checkUpkeep("");
        // require(upkeepNeeded, "Not Upkeep");
        address[] memory billedCustomers = abi.decode(performData, (address[]));
        if(keccak256(abi.encode(paymentsDue)) != keccak256(performData)) {
            billedCustomers = paymentsDue;
        }

        delete paymentsDue;

        for(uint256 index = 0; index < billedCustomers.length; index++) {
            _billCustomer(billedCustomers[index]);    
        }
        
        // -----------------
        // Some issue here
        // So if a customer doesnt pay the bills
        // Then we still delete them from the payments due
        // Maybe we can return true of false,
        // If false we can push the address to a memory array
        // Come back and set payments due to the leftovers
        // If they're too high on value then lock em





        // get list of customers from the perform data
        // bill all them or lock their account

        // Transfers eth from the owners payable address to here
        // This is basically forcing people to pay their bills
        // pauses maintenance window and deletes balances for addrs billed
    }

    function _billCustomer(address customer) internal {
        bool success = ICustomer(customer).bill(customers[customer].feesDue);
        if(success) {
            customers[customer].feesDue = 0;
            customers[customer].setToBill = false;
        } else {
            paymentsDue.push(customer);

            // Maybe we add some logic to lock an account if its balance is too in debt

        }
    }

    function addFeesToCustomer(address customer, uint256 amount) external {
        require(msg.sender == REGISTRAR, "Not the registrar calling.");
        if(customers[customer].setToBill == false){
            customers[customer].setToBill = true;
            paymentsDue.push(customer);
        }
        customers[customer].feesDue += amount;
    }

    function getEncodedRequiredBills() public view returns(bytes memory) {
        return abi.encode(paymentsDue);
    }
}


    // function registerGame(
    //     address payable invoiceAddress, // Address to bill for contract execution
    //     address gameContract, // Overarching game contract if there is one (not sure why)
    //     address assetController, // Address of who controlls the asset, call gate (??)
    //     address[] calldata assetContractAddresses, // Addresses of your Asset contracts
    //     ItemType[] calldata assetContractItemTypes // ItemTypes of your Asset contracts
    // ) public {
    //     // Registers a customer (game)
    //     // Customers add their payable address for billing
    //     // Game address if they have an onchain game
    //     // Adds their game asset contracts, we'll enforce ownership
    //     // eventually through ZK proofs onchain
    //     require(
    //         customers[invoiceAddress].eligible == false,
    //         "Invoice Address already registered."
    //     );

    //     require(
    //         assetContractAddresses.length == assetContractItemTypes.length,
    //         "Mismatch in asset addresses and itemtypes"
    //     );

    //     //ToDo: Add details to storage mapping
    //     // Set the customers mapping with the invoice struct
    //     customers[invoiceAddress] = CustomerStruct({
    //         feesDue: 0, // 0 fees due to start
    //         gameContract: gameContract, 
    //         eligible: true,
    //         setToBill: false, // (???)
    //         assetContracts: assetContractAddresses
    //     });

    //     uint256 ctLength = assetContractAddresses.length;
    //     for (uint256 i = 0; i < ctLength; i++) {
    //         require(!assets[assetContractAddresses[i]].eligible, "Asset already registered.");
    //         // Add each contract to assets map
    //         assets[assetContractAddresses[i]] = AssetContract({
    //             customer: invoiceAddress, // Who gets billed
    //             executor: assetController, // Who controlls
    //             itemType: assetCexontractItemTypes[i], // What asset type
    //             eligible: true
    //         });
    //     }

    //     emit GameRegistered(invoiceAddress, ctLength);

    //     // Need to test all this shit
    // }