// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract SpendingLimitModule {
    uint256 public spendingLimit;
    address public owner;

    event SpendingLimitChanged(
        uint256 oldLimit,
        uint256 newLimit
    );

    modifier onlyOwner() {
        require(
            msg.sender == owner,
            "Not owner"
        );
        _;
    }

    constructor(
        uint256 initialLimit
    ) {
        owner = msg.sender;
        spendingLimit = initialLimit;
    }

    function setSpendingLimit(
        uint256 newLimit
    )
        external
        onlyOwner
    {
        uint256 oldLimit = spendingLimit;

        spendingLimit = newLimit;

        emit SpendingLimitChanged(
            oldLimit,
            newLimit
        );
    }

    function getSpendingLimit()
        external
        view
        returns (uint256)
    {
        return spendingLimit;
    }
}