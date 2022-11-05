
pragma solidity ^0.8.14;

import "@oz/proxy/utils/Initializable.sol";

// Customer interface
interface ICustomer {

    function initialize(address owner) external;

    function deposit() external payable;

    function bill(uint256 amount) external returns(bool success);

    function getOwner() external returns(address owner);

}

/**
 * @title Customer
 * @author waint.eth
 * @notice This contract is the Customer contract for the CurrentSDK Coordinator. New customers
 *      are registered and it creates a clone of this contract. This contract allows a customer
 *      to fund through the deposit function, and allows the Coordinator to bill them through
 *      the bill function for their usage on Coordinator or in the SDK. Customers must fund
 *      this contract in order to use the Coordinator and the functionality in the SDK. 
 */
contract Customer is ICustomer, Initializable {

    // @notice event for when a deposit occurs and who sent it.
    event DepositSuccessful(address sender, uint256 amount);

    // Immutable address for the coordinator
    address public immutable coordinator;

    // Address of who owns this contract
    address public owner;

    // balance of this contract
    // @dev I dont think this is necessary, may come back after hackathon.
    uint256 public balance = 0;

    /**
     * @notice Constructor sets the immutable coordinator address.
     */
    constructor(
        address _coordinator
    ) {
        coordinator = _coordinator;
    }

    /**
     * @notice Initialization function
     *
     * @param _owner Owner of the contract, this is set from Coordinator.sol
     *
     */
    function initialize(
        address _owner
    ) initializer override public {
        owner = _owner;
    }

    /**
     * @notice Deposit function for depositing ether into this contract.
     *
     */
    function deposit() public override payable {
        // Maybe want to expand to other ERCs?
        balance += msg.value;
        emit DepositSuccessful(msg.sender, msg.value);
    }

    /**
     * @notice Billing function for Coordinator to withdraw funds for usage.
     *
     * @param amount how much needs to be withdrawn from this contract.
     *
     */
    function bill(uint256 amount) external override returns(bool success) {
        require(msg.sender == coordinator, "NOT COORDINATOR");
        if(amount > balance) {
            return false;
        } else {
            // No re-entry cause we know what coordinator does on recieve.
            (success, ) = address(coordinator).call{value: amount}("");
            if(success) {
                balance -= amount;
            }
            return true;
        }
    }

    /**
     * @notice Gets the owner of this contract.
     *
     * @dev probably can be deleted...
     */
    function getOwner() external view returns(address) {
        return owner;
    }

    /**
     * @dev just in case someone sends to the address instead of using deposit.
     */
    receive() external payable {
        require(msg.value > 0, "NO ETH SENT");
        deposit();
    }

}

