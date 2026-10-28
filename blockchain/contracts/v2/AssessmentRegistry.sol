// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title AssessmentRegistry
/// @notice Stores report fingerprints and module approval verdicts.
/// @dev Research prototype; not a production security boundary.
contract AssessmentRegistry {
    address public owner;

    enum RiskLevel {
        UNKNOWN,
        LOW,
        MEDIUM,
        HIGH,
        CRITICAL
    }

    struct Assessment {
        bytes32 reportHash;
        RiskLevel riskLevel;
        bool approved;
        address module;
        uint256 updatedAt;
        bool exists;
    }

    mapping(bytes32 => Assessment) private assessments;
    mapping(address => bool) public approvedModule;

    event AssessmentRecorded(
        bytes32 indexed integrationKey,
        string integrationId,
        bytes32 reportHash,
        RiskLevel riskLevel,
        address indexed module,
        bool approved
    );

    event ModuleApprovalChanged(address indexed module, bool approved);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function recordAssessment(
        string calldata integrationId,
        bytes32 reportHash,
        RiskLevel riskLevel,
        address module,
        bool requestApproval
    ) external onlyOwner {
        require(bytes(integrationId).length > 0, "Empty integration ID");
        require(reportHash != bytes32(0), "Empty report hash");
        require(riskLevel != RiskLevel.UNKNOWN, "Unknown risk");

        // This prototype permits approval only for explicitly LOW risk.
        bool approved = requestApproval
    && riskLevel == RiskLevel.LOW
    && module != address(0);

        bytes32 key = keccak256(bytes(integrationId));

        assessments[key] = Assessment({
            reportHash: reportHash,
            riskLevel: riskLevel,
            approved: approved,
            module: module,
            updatedAt: block.timestamp,
            exists: true
        });

        approvedModule[module] = approved;

        emit AssessmentRecorded(
            key,
            integrationId,
            reportHash,
            riskLevel,
            module,
            approved
        );

        emit ModuleApprovalChanged(module, approved);
    }

    function getAssessment(
        string calldata integrationId
    ) external view returns (
        bytes32 reportHash,
        RiskLevel riskLevel,
        bool approved,
        address module,
        uint256 updatedAt,
        bool exists
    ) {
        Assessment storage a = assessments[
            keccak256(bytes(integrationId))
        ];

        return (
            a.reportHash,
            a.riskLevel,
            a.approved,
            a.module,
            a.updatedAt,
            a.exists
        );
    }

    function isModuleApproved(address module) external view returns (bool) {
        return approvedModule[module];
    }

    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Invalid owner");
        owner = newOwner;
    }
}
