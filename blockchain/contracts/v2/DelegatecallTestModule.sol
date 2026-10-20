
 // SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @notice Test-only module that deliberately overwrites a host storage slot.
/// @dev Never deploy this test module in a production environment.
contract DelegatecallTestModule {
    // These slots intentionally match ModuleHost's first two storage slots.
    address public owner;
    uint256 public value;

    function corruptCanary(uint256 newValue) external {
        value = newValue;
    }
}
