
pragma solidity ^0.8.14;

import "@oz/proxy/utils/Initializable.sol";

interface ICustomer {

    function deposit() external payable;

    function bill() external;

}


contract Customer is ICustomer, Initializable {

    event DepositSuccessful(address sender, uint256 amount);

    address public immutable coordinator;
    address public owner;
    uint256 balance = 0;

    function initialize(
        address _owner,
        address _coordinator
    ) initializer public {
        owner = _owner;
        coordinator = _coordinator;
    }

    receive() {
        require(msg.value > 0, "NO ETH SENT");
        deposit();
    }


    function deposit() external override payable {
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



}

