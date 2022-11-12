// SPDX-License-Identifier: MIT
pragma solidity ^0.8.14;

import "@chainlink/contracts/src/v0.8/interfaces/KeeperCompatibleInterface.sol";
import "./lib/StructsAndEnums.sol";
import {ICustomer, Customer} from "./utils/Customer.sol";
import {Clones} from "@oz/proxy/Clones.sol";
import {SafeTransferLib} from "@solmate/utils/SafeTransferLib.sol";

/**
 * @title Coordinator
 * @author waint.eth
 * @notice This is the Coordinator for the CurrentSDK. What this contract allows you to do
 *      is register yourself as a customer and add assets to your customer profile. When you
 *      register as a customer a new Customer.sol contract is created and you must deposit
 *      funds into that. The coordinator can then be executed to mint and deliver assets
 *      to your users wallets from the SDK. The function will then add balance to your fees
 *      and automatically withdraw funds from your customer contract via the Bill method.
 *      Essentially what we're doing is obfuscating what would be user required transactions
 *      to your customer profile so we can provide a seemless experience for the end user and
 *      cover the costs of your transactions through your Customer contract.
 */
contract Coordinator is KeeperCompatibleInterface {
    using SafeTransferLib for address;

    // Event: New customer is registered
    event CustomerRegistered(address customer, address controller);

    // Event: Assets are added to a customer profile.
    event AddedAssetsToCustomer(
        address customer,
        address[] additionalContracts,
        address[] updatedContracts
    );
    
    // Event: Adding fees to a customer.
    event AddedFeesToCustomer(address customer, uint256 amount);

    // Assets are minted to recipients
    event MintedAssets(PackageItem[] packages, address[] recipients);

    // Funds are withdrawn from this contract
    event Withdraw(address withdrawAddress, uint256 amount);

    // The owner of this contract has changed
    event OwnerChange(address newOwner);

    // Address for the customer logic
    address public immutable customerLogic;

    // CurrentSDK Registrar address
    address public immutable REGISTRAR;

    // Owner for withdrawing funds
    address payable public OWNER;

    // Required deposit for customers
    uint256 public initialDeposit = 0.1 ether;

    // List of which customers have outstanding debt
    address[] public paymentsDue;

    // Mapping of customers
    mapping(address => CustomerStruct) public customers;

    // Mapping of assets
    mapping(address => AssetContract) public assets;

    /**
     * @notice Confirms equal length of assets and itemtypes
     *
     * @param assetContracts Array of asset contract addresses
     * @param itemTypes Array of itemtypes to assign to asset contracts
     *
     */
    modifier equalAssetsAndTypes(
        address[] calldata assetContracts,
        ItemType[] calldata itemTypes
    ) {
        require(
            assetContracts.length == itemTypes.length,
            "Missatch in asset addresses and itemtypes"
        );
        _;
    }

    /**
     * @notice Constructor, sets the customerLogic, REGISTRAR, and OWNER
     *
     * @param _registrar Address of the CurrentSDK REGISTRAR
     *
     */
    constructor(address _registrar) {
        customerLogic = address(new Customer(address(this)));
        REGISTRAR = _registrar;
        OWNER = payable(_registrar);
    }

    /**
     * @notice Registers a new customer. This function creates a cloned
     *      customer contract and pre-loads 0.1ether in it. This is to ensure
     *      funds for initial contract calls.
     *
     * @param assetController Controller address for the customer assets.
     *
     */
    function registerCustomer(address assetController)
        public
        payable
        returns (address customer)
    {
        require(
            msg.value >= initialDeposit,
            "Incorrect msg.value, send >0.1 ether"
        );

        // Clone the customer contract and initialize with assetController
        customer = Clones.clone(customerLogic);
        ICustomer(customer).initialize(assetController);

        // Send some eth to the customer to initialize it
        customer.call{value: msg.value}("");

        // Finish adding the customer object to the registry
        customers[customer].eligible = true;
        emit CustomerRegistered(customer, assetController);
    }

    /**
     * @notice Register assets to a customer. When assets are registered, each time
     *      a function interacts with them, the Customer contract will be billed accordingly.
     *
     * @param assetController Controller address for the customer assets.
     * @param customerInvoice Customer invoice address to add the assets to.
     * @param assetContractAddresses Addresses of your Asset contracts
     * @param assetContractItemTypes ItemTypes of your Asset contracts
     *
     */
    function registerAssets(
        address assetController,
        address customerInvoice,
        address[] calldata assetContractAddresses,
        ItemType[] calldata assetContractItemTypes
    )
        public
        payable
        equalAssetsAndTypes(assetContractAddresses, assetContractItemTypes)
    {
        // Check validity, must be owner and eligible to add assets
        require(
            ICustomer(customerInvoice).getOwner() == msg.sender,
            "Not Invoice Owner"
        );
        require(
            customers[customerInvoice].eligible,
            "Customer Invoice is not eligible."
        );

        // Loop through all the contracts
        uint256 len = assetContractAddresses.length;
        for (uint8 i = 0; i < len; i++) {
            // Make sure asset isnt already registered
            require(
                !assets[assetContractAddresses[i]].eligible,
                "Asset is already registered."
            );

            // Build the asset object and store it
            assets[assetContractAddresses[i]] = AssetContract({
                customer: customerInvoice, // Who gets billed
                executor: assetController, // Who controlls
                itemType: assetContractItemTypes[i], // What asset type
                eligible: true
            });

            // Set the address in the customers mapping
            customers[customerInvoice].assetContracts.push(
                assetContractAddresses[i]
            );
        }

        emit AddedAssetsToCustomer(
            customerInvoice,
            assetContractAddresses,
            customers[customerInvoice].assetContracts
        );
    }

    /**
     * @notice Register as a new customer with assets. Combination of the above
     *      two functions.
     *
     * @param assetController Controller address for the customer assets.
     * @param assetContractAddresses Addresses of your Asset contracts
     * @param assetContractItemTypes ItemTypes of your Asset contracts
     *
     */
    function registerWithAssets(
        address assetController,
        address[] calldata assetContractAddresses,
        ItemType[] calldata assetContractItemTypes
    ) external payable returns (address customer) {
        // Generate new customer contract
        customer = registerCustomer(assetController);

        // Register the assets
        registerAssets(
            assetController,
            customer,
            assetContractAddresses,
            assetContractItemTypes
        );
    }

    /**
     * @notice Distribute assets to the users.
     *      TODO: Build this out. This requires a bit more thought than just
     *      minting assets to a user from a defined interface, so that will
     *      be the next step, figuring out how to distribute assets easily.
     *
     * @param packages PackageItem assets to mint to the users
     * @param recipients Addresses of the users to distribute to
     *
     */
    function distributeAssets(
        PackageItem[] calldata packages,
        address[] calldata recipients
    ) public {}

    /**
     * @notice Mint the assets to the users.
     *
     * @param packages PackageItem assets to mint to the users
     * @param recipients Addresses of the users to distribute to
     *
     */
    function mintAssets(
        PackageItem[] calldata packages,
        address[] calldata recipients
    ) public {
        uint256 packLen = packages.length;
        require(
            packLen == recipients.length,
            "Packages and recipients mismatch."
        );
        // Loop through all the packages
        for (uint256 i = 0; i < packLen; i++) {
            // Mint the package to the user
            require(
                assets[packages[i].token].eligible,
                "Contract not registered."
            );
            require(
                assets[packages[i].token].executor == msg.sender,
                "Not the asset executor."
            );
            _mintPackage(packages[i], recipients[i]);
        }
        emit MintedAssets(packages, recipients);
    }

    /**
     * @notice Mint a single asset to a user
     *
     * @param package PackageItem asset to mint to the users
     * @param recipient Addresses of the user to distribute to
     *
     * @dev right now this function uses a specific mint function in the CurrentNFT
     *      and CurrentToken contracts. In the future we will allow customers to create
     *      new contracts from this factory contract. Those contracts will have defined
     *      functionality that we need for this. Additionally, we will build a common
     *      interface for customers to build their own custom logic to add in.
     *      TODO: I realized this is inside a for loop, thats wasting a ton of gas,
     *      especially the reading of the customer from storage. Might be able to do that
     *      outside the for loop, but have to think about potentially different assets
     *      having different owners in the minting call.
     */
    function _mintPackage(PackageItem calldata package, address recipient)
        internal
    {
        // Check how much gas the minting costs and add to the customer bill
        uint256 gas = gasleft();
        address assetLocation = package.token;

        // TODO: More asset types, right now its limited
        // NATIVE
        // ERC1155
        // NONE

        // ERC20
        if (package.itemType == ItemType.ERC20) {
            bool success = IERC20(assetLocation).mint(
                recipient,
                package.amount
            );
            require(success, "Mint failed");
        }
        // ERC721
        if (package.itemType == ItemType.ERC721) {
            bool success = IERC721(assetLocation).mint(
                recipient,
                package.identifier
            );
            require(success, "Mint failed");
        }

        // Pull down the customer struct to edit the details
        CustomerStruct storage c = customers[assets[package.token].customer];
        if (c.setToBill != true) {
            c.setToBill = true;
            paymentsDue.push(assets[package.token].customer);
        }

        // Check gas left and add it to the fees of the customer
        gas -= gasleft();
        customers[assets[assetLocation].customer].feesDue += gas;
    }

    /**
     * @notice Get the encoded customers contracts
     *
     * @param invoiceAddress Invoice address to pull asset list from
     *
     */
    function getCustomerContractsEncoded(address invoiceAddress)
        public
        view
        returns (bytes memory)
    {
        return abi.encode(customers[invoiceAddress].assetContracts);
    }

    /**
     * @notice Get the customers contracts
     *
     * @param invoiceAddress Invoice address to pull asset list from
     *
     * @dev TODO: Cleanup these
     */
    function getCustomerContracts(address invoiceAddress)
        public
        view
        returns (address[] memory)
    {
        return customers[invoiceAddress].assetContracts;
    }

    /**
     * @notice Check the eligibility of a customers invoice address
     *
     * @param invoiceAddress Invoice address to check
     *
     */
    function getEligibility(address invoiceAddress) public view returns (bool) {
        return customers[invoiceAddress].eligible;
    }

    /**
     * @notice Chainlink functionality for checking upkeep
     *
     * @param checkData bytes to check.
     *
     */
    function checkUpkeep(bytes memory checkData)
        public
        view
        override
        returns (bool upkeepNeeded, bytes memory performData)
    {
        // Return data for the perform upkeep function
        // Encoded paymentdsDue array and a bool whether to check or not.
        return
            paymentsDue.length > 0
                ? (true, abi.encode(paymentsDue))
                : (false, abi.encode(paymentsDue));

        // If payments due has addresses in it, return true and the list in perform data
        // If not we go no billing required
        // In this instance upkeep is going to be charging customers wallets
    }

    /**
     * @notice Chainlink functionality for performing upkeep
     *
     * @param performData encoded addresses to bill.
     *
     * @dev nervous about the cost of this function. Should be okay with 5mil gas
     */
    function performUpkeep(bytes memory performData) external override {
        // Decode customer list
        address[] memory billedCustomers = abi.decode(performData, (address[]));

        // Confirm they're equal and no extra customers snuck in between blocks
        if (keccak256(abi.encode(paymentsDue)) != keccak256(performData)) {
            billedCustomers = paymentsDue;
        }

        // delete the paymentsDue array in this transaction so any following get caught
        delete paymentsDue;

        // TODO:
        // If this function is close to running out of gas, we need to add the remaining
        // customers to  paymentsDue so we can get them next time
        // Assuming this is running a lot this should eventually even out.
        // Bill the customers
        for (uint256 index = 0; index < billedCustomers.length; index++) {
            _billCustomer(billedCustomers[index]);
        }
    }

    /**
     * @notice Bills the customers invoice address. Essentially transfers
     *      funds based on how much they used distributing assets
     *
     * @param customer Customer address to bill
     *
     */
    function _billCustomer(address customer) internal {
        // Bill them and confirm
        bool success = ICustomer(customer).bill(customers[customer].feesDue);

        if (success) {
            // Set feesDue to 0 and setToBill to false
            customers[customer].feesDue = 0;
            customers[customer].setToBill = false;
        } else {
            // If it failed, add them back to the paymentsDue array
            paymentsDue.push(customer);

            // TODO: Add some logic to lock an account if its balance is too in debt
        }
    }

    /**
     * @notice Add the ability to add funds to a customers fees from the Registrar account.
     *
     *
     * @param customer Customer address to bill
     *
     * @dev This will need to be looked at and edited later. This is specifically for txs that
     *      are generated through the SDK but arent the mint or distribute tasks. We'll need to
     *      come back to this to make sure it cant be manipulated and abused.
     */
    function addFeesToCustomer(address customer, uint256 amount) external {
        // TODO: Custom error
        require(msg.sender == REGISTRAR, "Not the registrar calling.");

        if (customers[customer].setToBill == false) {
            customers[customer].setToBill = true;
            paymentsDue.push(customer);
        }

        customers[customer].feesDue += amount;
        emit AddedFeesToCustomer(customer, amount);
    }

    /**
     * @notice Helper to get encoded paymentsDue
     */
    function getEncodedRequiredBills() public view returns (bytes memory) {
        return abi.encode(paymentsDue);
    }

    /**
     * @notice Set the owner of the contract for withdraw
     *
     *
     * @param newOwner address of the new owner of the contract
     *
     */
    function setOwner(address payable newOwner) public {
        require(msg.sender == OWNER, "Not the owner");
        OWNER = newOwner;
        emit OwnerChange(OWNER);
    }

    /**
     * @notice Withdraw funds from this contract
     *
     * @dev this contract should only hold funds from fees collected
     */
    function withdraw() public {
        emit Withdraw(OWNER, address(this).balance);
        address(OWNER).safeTransferETH(address(this).balance);
    }

    receive() external payable {}

    fallback() external payable {}
}

interface IERC20 {
    function mint(address to, uint256 amount) external returns (bool);
}

interface IERC721 {
    function mint(address to, uint256 identifier) external returns (bool);
}
