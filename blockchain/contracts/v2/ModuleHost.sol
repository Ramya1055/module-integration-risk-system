
 // SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title ModuleHost
/// @notice Sandbox host for observing module execution.
/// @dev Research prototype only. Not a production security boundary.
contract ModuleHost {
    address public owner;

    // Host storage used to test delegatecall storage corruption.
    uint256 public protectedSlotValue = 12345;

    // Execution tracking.
    uint256 public executionDepth;
    uint256 public callCount;

    bool private executing;

    event ModuleCallReport(
        uint256 indexed callId,
        address indexed module,
        bool success,
        uint256 gasUsed,
        uint256 maxDepth,
        int256 balanceDelta,
        bytes returnData
    );

    event InvariantViolation(
        uint256 indexed callId,
        address indexed module,
        string violation
    );

    event ReentryDetected(
        uint256 indexed callId,
        address indexed caller
    );

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    /// @notice Execute a module using a normal external call.
    /// @dev Records a failed module call instead of automatically reverting.
    function execute(
        address module,
        bytes calldata data
    ) external payable onlyOwner returns (bool success) {
        require(module != address(0), "Invalid module");
        require(module.code.length > 0, "Module has no code");
        require(!executing, "Execution already in progress");

        executing = true;
        executionDepth = 1;

        uint256 currentCallId = ++callCount;
        uint256 gasAtStart = gasleft();

        // Exclude msg.value from the starting balance.
        uint256 balanceBefore = address(this).balance - msg.value;

        uint256 originalCanary = protectedSlotValue;
        address originalOwner = owner;

        bytes memory returnData;

        (success, returnData) = module.call{value: msg.value}(data);

        uint256 gasUsed = gasAtStart - gasleft();
        uint256 maxDepth = executionDepth;

        // Net host balance change, including any ETH supplied with this call.
        int256 balanceDelta;

        if (address(this).balance >= balanceBefore) {
            balanceDelta = int256(
                address(this).balance - balanceBefore
            );
        } else {
            balanceDelta = -int256(
                balanceBefore - address(this).balance
            );
        }

        if (owner != originalOwner) {
            emit InvariantViolation(
                currentCallId,
                module,
                "OWNER_CHANGED"
            );
        }

        if (protectedSlotValue != originalCanary) {
            emit InvariantViolation(
                currentCallId,
                module,
                "STORAGE_CANARY_CHANGED"
            );
        }

        if (!success) {
            emit InvariantViolation(
                currentCallId,
                module,
                "MODULE_CALL_FAILED"
            );
        }

        executionDepth = 0;
        executing = false;

        emit ModuleCallReport(
            currentCallId,
            module,
            success,
            gasUsed,
            maxDepth,
            balanceDelta,
            returnData
        );
    }

    /// @notice Execute module code in the host's storage context.
    /// @dev Only use with controlled sandbox test modules.
    function executeDelegate(
        address module,
        bytes calldata data
    ) external onlyOwner returns (bool success) {
        require(module != address(0), "Invalid module");
        require(module.code.length > 0, "Module has no code");
        require(!executing, "Execution already in progress");

        executing = true;
        executionDepth = 1;

        uint256 currentCallId = ++callCount;
        uint256 gasAtStart = gasleft();

        uint256 originalCanary = protectedSlotValue;
        address originalOwner = owner;

        bytes memory returnData;

        (success, returnData) = module.delegatecall(data);

        uint256 gasUsed = gasAtStart - gasleft();

        // Capture depth before resetting execution state.
        uint256 maxDepth = executionDepth;

        if (owner != originalOwner) {
            emit InvariantViolation(
                currentCallId,
                module,
                "OWNER_CHANGED"
            );
        }

        if (protectedSlotValue != originalCanary) {
            emit InvariantViolation(
                currentCallId,
                module,
                "STORAGE_CANARY_CHANGED"
            );
        }

        if (!success) {
            emit InvariantViolation(
                currentCallId,
                module,
                "MODULE_CALL_FAILED"
            );
        }

        executionDepth = 0;
        executing = false;

        emit ModuleCallReport(
            currentCallId,
            module,
            success,
            gasUsed,
            maxDepth,
            0,
            returnData
        );
    }

    /// @dev Records ETH callbacks received during active execution.
    receive() external payable {
        if (executionDepth > 0) {
            emit ReentryDetected(callCount, msg.sender);
        }
    }

    fallback() external payable {
        if (executionDepth > 0) {
            emit ReentryDetected(callCount, msg.sender);
        }
    }
}
