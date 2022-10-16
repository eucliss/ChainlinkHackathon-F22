pragma solidity ^0.8.0;

// Bringing the basic asset structs from my protocol:
// https://github.com/eucliss/Basin/blob/master/src/contracts/lib/StructsAndEnums.sol
// https://github.com/eucliss/Basin/

enum ItemType {
    NATIVE,
    ERC20,
    ERC721,
    ERC1155,
    NONE
}

struct PackageItem {
    ItemType itemType;
    address token;
    uint256 identifier;
    uint256 amount;
}

struct CustomerStruct {
    uint256 feesDue;
    address gameContract;
    bool eligible;
    bool setToBill;
    address[] assetContracts;
}

struct AssetContract {
    address customer;
    address executor;
    ItemType itemType;
    bool eligible;
}
