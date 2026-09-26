// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract SecurityTestModule {

    address public target;

    constructor(address _target) {
        target = _target;
    }

    function execute(bytes calldata data)
        external
    {
        target.delegatecall(data);
    }
}