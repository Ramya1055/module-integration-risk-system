
 // SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract TestModule {
    uint256 public value;

    function succeed(uint256 newValue) external {
        value = newValue;
    }

    function fail() external pure {
        revert("Intentional test failure");
    }
}
