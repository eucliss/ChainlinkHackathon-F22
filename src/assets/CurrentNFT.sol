// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity >=0.8.14;

import {ERC721} from "@solmate/tokens/ERC721.sol";

contract CurrentNFT is ERC721 {
    
    uint256 public nextTokenId = 0;

    constructor() ERC721("CurrentNFT", "CURR") {}

    modifier validTokenId(uint256 tokenId) {
        require(tokenId == nextTokenId, "Token ID incorrect.");
        _;
    }

    function tokenURI(uint256)
        public
        pure
        virtual
        override
        returns (string memory)
    {
        return "TokenURI";
    }
    function mint(address to, uint256 tokenId) 
        public 
        virtual 
        validTokenId(tokenId)
        returns(bool)
        {
        _mint(to, tokenId);
        nextTokenId++;
        return true;
    }

    function burn(uint256 tokenId) public virtual {
        _burn(tokenId);
    }
}
