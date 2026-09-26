# Module Integration Observability & Security Data Collection System

## 1. Project Overview

This project implements **Stage 1 of a Module Integration Observability and Security Data Collection System** for smart-contract-based modular systems.

The purpose of Stage 1 is to observe what happens when a proposed module is integrated into an existing system and to collect structured evidence about:

* Module characteristics
* System performance
* Runtime behavior
* Blockchain transactions
* Security-rule findings
* Integration events
* Performance changes
* Final integration status

The collected information is stored in a **SQLite database** and can be exported as a structured integration report.

The system follows the workflow:

> **Observe → Measure → Detect → Record → Analyze → Store → Report**

This stage focuses on **data collection and evidence generation**. It does not perform machine-learning-based prediction.

---

# 2. Problem Statement

When a new module or smart contract is added to an existing system, it is important to understand what happened during the integration.

Simply checking whether the code compiles is not sufficient.

An integration can affect:

* CPU usage
* Memory usage
* Runtime errors
* Blockchain transactions
* Gas consumption
* Contract execution
* Security-related code patterns
* System behavior during integration

Therefore, this project provides a structured mechanism to observe the integration process and preserve the resulting evidence.

---

# 3. Objective

The main objective of Stage 1 is:

> **To build an observable and measurable integration pipeline that collects structured system, module, runtime, blockchain, performance, and security evidence during the integration of a proposed smart-contract module.**

The system produces a structured record for every integration using an integration identifier such as:

```text
INT-000001
```

---

# 4. Simple Explanation

Suppose an existing system already contains:

```text
SpendingLimitModule
```

and we want to introduce:

```text
SafeModule
```

The system does not simply assume that the new module is safe.

Instead, it observes the integration.

It first records the system's baseline condition.

Then it starts monitoring the integration.

During the integration, it records:

* CPU usage
* Memory usage
* Runtime errors
* Module characteristics
* Blockchain activity
* Security-rule findings
* Integration events

After the integration finishes, the system compares the observations and stores the results.

Finally, it produces an integration report.

Therefore, the system answers questions such as:

> What module was integrated?

> What did the module contain?

> What happened to system performance?

> Were any findings detected by the implemented security rules?

> Did a blockchain transaction occur?

> How much gas was used?

> What events occurred during the integration?

---

# 5. Technical Explanation

The system is implemented as a modular Python-based backend with a local Hardhat blockchain environment.

The major components are:

```text
Existing Module
       +
Proposed Module
       +
Smart Contract
       |
       v
Integration API
       |
       v
Integration Service
       |
       +------------------+
       |                  |
       v                  v
Module Profiler       Runtime Monitor
       |                  |
       +--------+---------+
                |
                v
        Blockchain Monitor
                |
                v
        Security Analyzer
                |
                v
       Performance Analyzer
                |
                v
          Event Recorder
                |
                v
            SQLite
                |
                v
         Final Integration
             Report
```

---

# 6. Core Workflow

The integration lifecycle implemented by the system is:

```text
CREATED
   ↓
INITIALIZING
   ↓
BASELINE_CAPTURED
   ↓
IN_PROGRESS
   ↓
COMPLETED
   ↓
POST_ANALYSIS
   ↓
FINALIZED
```

Each stage represents a specific point in the integration process.

### CREATED

A new integration record is created.

Example:

```text
Integration ID: INT-000006
Existing Module: SpendingLimitModule
Proposed Module: SafeModule
Network: local
```

### INITIALIZING

The integration process is prepared.

### BASELINE_CAPTURED

System performance is measured before runtime monitoring.

The baseline includes:

* CPU usage
* Memory usage
* Error count

### IN_PROGRESS

Runtime monitoring is performed.

Multiple runtime samples are collected.

### COMPLETED

The integration activity is completed.

### POST_ANALYSIS

Performance and security observations are analyzed.

### FINALIZED

All required information has been recorded and the integration report is finalized.

---

# 7. Technologies Used

## Backend

### Python

Python is the primary implementation language.

It is used for:

* API implementation
* Integration workflow
* Monitoring
* Module profiling
* Security analysis
* Blockchain interaction
* Database operations
* Report generation

### FastAPI

FastAPI provides the REST API used to control the integration lifecycle.

Examples of API operations include:

```text
POST /integrations
POST /integrations/{integration_id}/start
POST /integrations/{integration_id}/begin-monitoring
POST /integrations/{integration_id}/runtime-metric
POST /integrations/{integration_id}/runtime-samples
POST /integrations/{integration_id}/complete
POST /integrations/{integration_id}/analyze
POST /integrations/{integration_id}/security-analysis
POST /integrations/{integration_id}/finalize
GET  /integrations/{integration_id}/report
```

FastAPI also provides Swagger documentation for testing the API.

---

# 8. Database

## SQLite

SQLite is used as the local database.

A separate database server is not required.

The database stores the evidence collected during integration.

The main tables are:

```text
integrations
system_metrics
module_profiles
integration_events
performance_analysis
security_findings
blockchain_transactions
```

## SQLAlchemy

SQLAlchemy is used as the ORM layer between Python and SQLite.

It allows the system to represent database tables as Python models and perform database operations programmatically.

---

# 9. Module Profiling

The module profiler extracts structural information from Solidity source code.

The current prototype records information such as:

* Source lines
* Number of functions
* State variables
* External calls
* Events
* Modifiers
* Payable functions
* Interfaces
* Dependencies

For example, a module profile can contain:

```text
Module Name       : SafeModule
Source Lines      : 51
Functions         : 2
State Variables   : 2
External Calls    : 0
Events            : 1
Modifiers         : 1
Payable Functions : 0
Dependencies      : 0
```

The current profiler is a **regex-based prototype for simple Solidity source files**. It is not intended to be a complete Solidity compiler/parser.

---

# 10. Runtime Monitoring

The runtime monitoring component uses `psutil`.

The system collects:

* CPU percentage
* Memory percentage
* Error count

Monitoring is performed in multiple samples rather than relying on a single measurement.

The demonstration integration collected five runtime samples.

Example:

```text
CPU     Memory     Errors
18.8    94.6       0
22.3    94.5       0
18.3    94.5       0
18.6    94.4       0
18.8    94.1       0
```

This provides evidence about system behavior during the integration.

---

# 11. Performance Analysis

After runtime monitoring, the system compares the baseline measurements with runtime observations.

For the demonstration integration:

```text
Baseline CPU            : 29.0%
Average Runtime CPU     : 19.36%
CPU Change              : -9.64%

Baseline Memory         : 94.9%
Average Runtime Memory  : 94.42%
Memory Change           : -0.48%

Runtime Samples         : 5
Runtime Errors          : 0
```

These values represent **observed measurements for the demonstration run**.

They should not be interpreted as a universal performance guarantee.

---

# 12. Security Analysis

The current security analyzer is an evidence-based prototype using source-code patterns.

It currently checks for patterns including:

```text
.delegatecall(
.call(
.send(
.transfer(
```

For example, the security test module contains a `delegatecall` pattern, which the analyzer can identify as:

```text
DELEGATECALL_USAGE
```

The analyzer therefore provides an indication that a particular code pattern exists.

It is **not a complete smart-contract vulnerability detector**.

A security finding is only recorded when one of the implemented analysis rules identifies supporting evidence.

The system therefore does not treat every transaction failure as a vulnerability.

---

# 13. Blockchain Monitoring

The blockchain component uses:

* Hardhat
* Web3.py
* Solidity

A local Hardhat blockchain is used for controlled testing.

The system can observe transaction information such as:

* Transaction hash
* Sender address
* Receiver address
* Block number
* Gas limit
* Gas used
* Transaction status

The project does not require Foundry tools such as:

```text
forge
cast
anvil
```

The local blockchain functionality is provided using Hardhat.

---

# 14. Smart Contract Demonstration

The demonstration uses:

### Existing Module

```text
SpendingLimitModule
```

It contains functionality related to managing a spending limit.

### Proposed Module

```text
SafeModule
```

It contains an owner-controlled value that can be updated through its functions.

The project does not assume that the name `SafeModule` means that the contract is universally secure.

The module is simply the proposed module used in the demonstration.

---

# 15. Demonstration Integration

The completed demonstration uses:

```text
Integration ID    : INT-000006
Existing Module   : SpendingLimitModule
Proposed Module   : SafeModule
Network           : local
Status            : FINALIZED
```

The deployed contract address was:

```text
0x5FbDB2315678afecb367f032d93F642f64180aa3
```

---

# 16. Blockchain Execution

A real transaction was executed against the deployed contract.

Recorded transaction:

```text
Transaction Hash:
ee64b5742dbed42ef4ede52423996e4c5b8dbe61f0a96dbc9ad002f9d63ef424

Block Number : 4
Gas Limit    : 200000
Gas Used     : 30379
Status       : 1
```

A status of `1` indicates that the transaction succeeded on the local test blockchain.

The transaction information was retrieved from the blockchain and stored in the SQLite database.

---

# 17. Integration Events

The system records important lifecycle events.

For `INT-000006`, the following events were recorded:

```text
BASELINE_CAPTURED
MONITORING_STARTED

RUNTIME_METRIC_COLLECTED
RUNTIME_METRIC_COLLECTED
RUNTIME_METRIC_COLLECTED
RUNTIME_METRIC_COLLECTED
RUNTIME_METRIC_COLLECTED

INTEGRATION_COMPLETED
POST_ANALYSIS_COMPLETED
SECURITY_ANALYSIS_COMPLETED
INTEGRATION_FINALIZED
```

A total of 11 events were recorded.

---

# 18. Database Verification

For the final demonstration integration:

```text
Integrations             : 1
Module Profiles          : 1
System Metrics           : 6
Integration Events       : 11
Performance Analyses     : 1
Security Findings        : 0
Blockchain Transactions  : 1
```

The six system metrics consist of:

```text
1 baseline measurement
+
5 runtime measurements
```

---

# 19. Security Result

For `INT-000006`:

```text
Findings Detected : 0
Findings Stored   : 0
```

This means:

> No findings were detected by the implemented security analysis rules for this particular integration.

It does **not** mean that the smart contract has been mathematically or universally proven to be secure.

---

# 20. Final Report

The system generates a structured JSON report containing:

```text
Integration Information
Module Profiles
System Metrics
Performance Analysis
Security Findings
Blockchain Transactions
Integration Events
```

The final demonstration report is:

```text
reports/INT-000006_report.json
```

The report status is:

```text
FINALIZED
```

---

# 21. Running the Demonstration

After setting up the Python environment and local Hardhat blockchain, the demonstration output can be viewed using:

```powershell
python scripts\demo.py
```

The demonstration reads the finalized integration report and displays:

```text
1. Integration
2. Proposed Module Profile
3. Performance Observation
4. Security Analysis
5. Blockchain Transaction
6. Event History
7. Final Report
```

---

# 22. Project Structure

```text
module-integration-risk-system/
│
├── backend/
│   └── app/
│       ├── api/
│       ├── services/
│       └── main.py
│
├── blockchain/
│   ├── contracts/
│   ├── connection.py
│   ├── monitor.py
│   └── transaction_service.py
│
├── monitoring/
│   ├── baseline.py
│   ├── runtime_monitor.py
│   ├── monitoring_loop.py
│   ├── module_profiler.py
│   └── performance_analyzer.py
│
├── security/
│   ├── analyzer.py
│   └── finding_service.py
│
├── database/
│   ├── db.py
│   ├── models.py
│   └── init_db.py
│
├── reports/
│   └── INT-000006_report.json
│
├── scripts/
│   ├── demo.py
│   └── ...
│
├── tests/
│
├── README.md
├── requirements.txt
├── package.json
├── hardhat.config.ts
├── tsconfig.json
└── .gitignore
```

---

# 23. Implementation Flow

The complete Stage 1 implementation can be summarized as:

```text
1. Define an integration
        ↓
2. Capture integration metadata
        ↓
3. Profile the proposed module
        ↓
4. Capture baseline system metrics
        ↓
5. Start runtime monitoring
        ↓
6. Execute/observe integration activity
        ↓
7. Record runtime measurements
        ↓
8. Monitor blockchain transactions
        ↓
9. Apply security analysis rules
        ↓
10. Analyze performance
        ↓
11. Record lifecycle events
        ↓
12. Store evidence in SQLite
        ↓
13. Generate final integration report
        ↓
14. Finalize integration
```

---

# 24. Why This Stage Is Important

This Stage 1 system creates the **evidence collection layer** required before building an intelligent risk-assessment model.

Instead of immediately training a model, the system first establishes a structured way to collect observations.

This allows future data to contain information such as:

```text
Module characteristics
+
Runtime behavior
+
Performance measurements
+
Blockchain behavior
+
Security evidence
+
Integration outcome
```

These structured observations can later become inputs for a machine-learning-based security risk assessment system.

---

# 25. Current Scope and Limitations

This implementation is a Stage 1 prototype.

### Current limitations

#### Module profiling

The module profiler uses regex-based extraction and therefore does not represent a complete Solidity parser.

#### Security analysis

The security analyzer currently uses a limited set of source-code patterns.

It should not be treated as a complete vulnerability detection system.

#### Runtime measurements

CPU and memory values are environment-dependent and can change between executions.

#### Blockchain

The current demonstration uses a local Hardhat blockchain rather than a production blockchain network.

#### Risk prediction

No machine-learning risk prediction is performed in Stage 1.

There is currently no:

* ML model
* vulnerability probability
* risk score
* automated risk classification
* exploitability prediction

---

# 26. Future Stage 2

Stage 2 is intended to build on the structured evidence generated by Stage 1.

The conceptual workflow will become:

```text
Stage 1

Observe → Measure → Detect → Record → Analyze → Store
                         ↓
                    Dataset
                         ↓
Stage 2

Learn → Predict → Explain
```

Stage 2 may use the collected multimodal information for intelligent smart-contract security risk assessment.

Stage 2 is outside the implementation scope of this repository version.

---

# 27. Summary

This project implements a modular **Stage 1 integration observability and security data collection system**.

It provides a complete pipeline for:

```text
Module Integration
        ↓
Observation
        ↓
Measurement
        ↓
Security Evidence
        ↓
Blockchain Evidence
        ↓
Performance Analysis
        ↓
Event Recording
        ↓
SQLite Storage
        ↓
Structured Report
```

The system has been demonstrated using:

```text
Existing Module : SpendingLimitModule
Proposed Module : SafeModule
Integration     : INT-000006
Blockchain      : Local Hardhat Network
Status          : FINALIZED
```

The resulting system provides a reproducible evidence-collection foundation for future intelligent security-risk assessment research.
