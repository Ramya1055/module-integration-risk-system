// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract SafeModule {
    uint256 public value;
    address public owner;

    event ValueChanged(
        uint256 oldValue,
        uint256 newValue
    );

    modifier onlyOwner() {
        require(
            msg.sender == owner,
            "Not owner"
        );
        _;
    }

    constructor(
        uint256 initialValue
    ) {
        owner = msg.sender;
        value = initialValue;
    }

    function setValue(
        uint256 newValue
    )
        external
        onlyOwner
    {
        uint256 oldValue = value;

        value = newValue;

        emit ValueChanged(
            oldValue,
            newValue
        );
    }

    function getValue()
        external
        view
        returns (uint256)
    {
        return value;
    }
}