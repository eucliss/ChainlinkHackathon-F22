
pragma solidity ^0.8.14;

import "@oz/proxy/utils/Initializable.sol";

interface ICustomer {

    function initialize(address owner) external;

    function deposit() external payable;

    function bill(uint256 amount) external returns(bool success);

    function getOwner() external returns(address owner);

}


contract Customer is ICustomer, Initializable {

    event DepositSuccessful(address sender, uint256 amount);

    address public immutable coordinator;
    address public owner;
    uint256 public balance = 0;

    constructor(
        address _coordinator
    ) {
        coordinator = _coordinator;
    }

    function initialize(
        address _owner
    ) initializer override public {
        owner = _owner;
    }

    function deposit() public override payable {
        // Maybe want to expand to other ERCs?
        balance += msg.value;
        emit DepositSuccessful(msg.sender, msg.value);
    }

    function bill(uint256 amount) external override returns(bool success) {
        require(msg.sender == coordinator, "NOT COORDINATOR");
        if(amount > balance) {
            return false;
        } else {
            (success, ) = address(coordinator).call{value: amount}("");
            if(success) {
                balance -= amount;
            }
        }
    }

    function getOwner() external view returns(address) {
        return owner;
    }

    receive() external payable {
        require(msg.value > 0, "NO ETH SENT");
        deposit();
    }

}

