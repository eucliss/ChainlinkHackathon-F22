// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity >=0.8.14;

import {ERC721} from "@solmate/tokens/ERC721.sol";

contract GameERC721 is ERC721 {
    
    uint256 public nextTokenId = 0;

    constructor() ERC721("GameNFT", "NFT") {}

    modifier validTokenId(uint256 tokenId) {
        require(tokenId == nextTokenId);
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
    
    function mintNextToken(address to) public virtual {
        _mint(to, nextTokenId);
        nextTokenId++;
    }

    function mint(address to, uint256 tokenId) 
        public 
        virtual 
        validTokenId(tokenId)
        {
        _mint(to, tokenId);

    }

    function burn(uint256 tokenId) public virtual {
        _burn(tokenId);
    }

    function safeMint(address to, uint256 tokenId) 
        public 
        virtual 
        validTokenId(tokenId)
        {
        _safeMint(to, tokenId);
    }

    function safeMint(
        address to,
        uint256 tokenId,
        bytes memory data
    ) public virtual validTokenId(tokenId) {
        _safeMint(to, tokenId, data);
    }
}