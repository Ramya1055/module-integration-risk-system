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

# From-Scratch Setup and Implementation

This section explains how to clone the repository and run the complete Stage 1 system from a clean Windows environment.

The instructions below reproduce the implementation using the technologies and scripts included in this repository.

### 1. Prerequisites

Install the following software before starting:

* Python 3.11
* Node.js and npm
* Git

Verify the installations:

```powershell
python --version
node --version
npm --version
git --version
```

This project does **not** require Foundry, Forge, Cast, or Anvil.

The local blockchain is provided by **Hardhat Network**.

---

### 2. Clone the Repository

Open PowerShell and clone the repository:

```powershell
git clone https://github.com/Ramya1055/module-integration-risk-system.git
```

Move into the project directory:

```powershell
cd module-integration-risk-system
```

---

### 3. Create the Python Virtual Environment

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell shows that script execution is restricted, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again:

```powershell
.\.venv\Scripts\Activate.ps1
```

The terminal should now show:

```text
(.venv)
```

---

### 4. Install Python Dependencies

Install the dependencies recorded in `requirements.txt`:

```powershell
pip install -r requirements.txt
```

The main packages used by the Stage 1 implementation include:

* FastAPI
* Uvicorn
* SQLAlchemy
* Pydantic
* psutil
* Web3.py
* pandas
* pytest
* pytest-asyncio

The repository contains the complete `requirements.txt` generated from the development environment.

---

### 5. Install Node.js Dependencies

Install the Node.js and Hardhat dependencies:

```powershell
npm install
```

Verify Hardhat:

```powershell
npx hardhat --version
```

The project uses Hardhat for the local Ethereum-compatible blockchain environment and Solidity compilation.

---

### 6. Initialize the SQLite Database

Create the database tables:

```powershell
python database\init_db.py
```

Expected output:

```text
Database initialized successfully.
```

The SQLite database is:

```text
integration_system.db
```

The database contains the tables used for:

* integrations
* module profiles
* system metrics
* integration events
* performance analysis
* security findings
* blockchain transactions

---

### 7. Compile the Smart Contracts

Compile the Solidity contracts:

```powershell
npx hardhat compile
```

The contracts are located in:

```text
blockchain\contracts\
```

The compiled artifacts are generated under:

```text
artifacts\
```

---

### 8. Start the Local Hardhat Blockchain

Open a **new PowerShell terminal**.

Move to the project directory:

```powershell
cd module-integration-risk-system
```

Start the local blockchain:

```powershell
npx hardhat node
```

Keep this terminal running.

The application connects to:

```text
http://127.0.0.1:8545
```

Hardhat provides local test accounts that are used by the deployment and blockchain-monitoring components.

---

### 9. Start the FastAPI Application

Open another PowerShell terminal.

Move to the project directory:

```powershell
cd module-integration-risk-system
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Start FastAPI:

```powershell
uvicorn backend.app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

The interactive API documentation is available through Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Keep this terminal running as well.

At this point, two terminals should remain active:

```text
Terminal 1 → npx hardhat node
Terminal 2 → uvicorn backend.app.main:app --reload
```

---

### 10. Deploy the Test Smart Contract

Open a third PowerShell terminal.

Activate the virtual environment:

```powershell
cd module-integration-risk-system
.\.venv\Scripts\Activate.ps1
```

Deploy the included `SafeModule` contract:

```powershell
python scripts\deploy_test_contract.py
```

The deployment script:

1. connects to the local Hardhat blockchain
2. loads the compiled `SafeModule` artifact
3. obtains the first Hardhat account
4. deploys `SafeModule`
5. waits for the deployment transaction
6. prints the deployed contract address
7. prints the deployment transaction hash
8. prints the block number and gas used

Example output:

```text
Local contract deployment successful.
--------------------------------
Contract: SafeModule
Deployer: <Hardhat account>
Address: <deployed contract address>
Transaction hash: <deployment transaction hash>
Block number: <block number>
Gas used: <gas used>
```

**Important:** The contract address may be different on a fresh run. Use the address printed by this command in the integration creation step.

---

### 11. Open the API Documentation

Open:

```text
http://127.0.0.1:8000/docs
```

The Stage 1 workflow can be executed through the FastAPI endpoints shown in Swagger UI.

The complete workflow is:

```text
Create Integration
        ↓
Start Integration
        ↓
Begin Monitoring
        ↓
Collect Runtime Samples
        ↓
Complete Integration
        ↓
Performance Analysis
        ↓
Security Analysis
        ↓
Record Blockchain Transaction
        ↓
Finalize Integration
        ↓
Generate Final Report
```

---

### 12. Create a New Integration

In Swagger UI, use:

```text
POST /integrations
```

Select **Try it out** and provide:

```json
{
  "existing_module": "SpendingLimitModule",
  "proposed_module": "SafeModule",
  "contract_address": "<DEPLOYED_CONTRACT_ADDRESS>",
  "network": "local"
}
```

Replace `<DEPLOYED_CONTRACT_ADDRESS>` with the address printed by the deployment script.

The system automatically generates an integration ID.

For example:

```text
INT-000001
```

The newly created integration starts with:

```text
CREATED
```

Save the generated integration ID because it is required for the remaining API operations.

---

### 13. Start the Integration

Use:

```text
POST /integrations/{integration_id}/start
```

For example:

```text
POST /integrations/INT-000001/start
```

This starts the integration and captures the baseline system measurements.

The lifecycle moves from:

```text
CREATED
    ↓
INITIALIZING
    ↓
BASELINE_CAPTURED
```

The baseline records CPU usage, memory usage, and error information.

---

### 14. Begin Runtime Monitoring

Use:

```text
POST /integrations/{integration_id}/begin-monitoring
```

For example:

```text
POST /integrations/INT-000001/begin-monitoring
```

This begins the runtime monitoring phase.

---

### 15. Collect Runtime Samples

Use:

```text
POST /integrations/{integration_id}/runtime-samples
```

The endpoint accepts:

```text
sample_count
interval_seconds
```

The demonstration uses:

```text
sample_count = 5
interval_seconds = 2
```

Therefore, the request can be made as:

```text
POST /integrations/INT-000001/runtime-samples?sample_count=5&interval_seconds=2
```

The system records CPU, memory, and runtime error observations for each sample.

Each sample is stored as a system metric and associated with the integration.

---

### 16. Complete the Integration

Use:

```text
POST /integrations/{integration_id}/complete
```

For example:

```text
POST /integrations/INT-000001/complete
```

This completes the integration phase and records the integration end time.

---

### 17. Perform Performance Analysis

Use:

```text
POST /integrations/{integration_id}/analyze
```

For example:

```text
POST /integrations/INT-000001/analyze
```

The performance analyzer compares the baseline observations with the runtime observations.

It calculates measurements such as:

* baseline CPU
* baseline memory
* average runtime CPU
* average runtime memory
* CPU change
* memory change
* runtime sample count
* runtime error count

These results are stored in the `performance_analysis` table.

---

### 18. Perform Security Analysis

Use:

```text
POST /integrations/{integration_id}/security-analysis
```

For example:

```text
POST /integrations/INT-000001/security-analysis
```

The current Stage 1 security analyzer is a prototype rule/pattern detector.

It checks the Solidity source for implemented patterns such as:

```text
delegatecall
call
send
transfer
```

Any detected pattern is recorded as a security finding with supporting evidence.

A result containing zero findings means:

> No findings were detected by the implemented security analysis rules.

It does **not** mean that the smart contract has been proven completely secure.

---

### 19. Record the Blockchain Transaction

The blockchain execution can be observed and stored as part of the integration.

Use:

```text
POST /integrations/{integration_id}/blockchain-transaction
```

Provide the transaction hash produced by the blockchain execution.

For example:

```text
POST /integrations/INT-000001/blockchain-transaction?transaction_hash=<TRANSACTION_HASH>
```

The system retrieves the transaction details from the local Hardhat blockchain and stores:

* transaction hash
* sender address
* receiver address
* block number
* gas limit
* gas used
* transaction status

The transaction is linked to the integration ID.

---

### 20. Finalize the Integration

After the analysis and blockchain transaction have been recorded, use:

```text
POST /integrations/{integration_id}/finalize
```

For example:

```text
POST /integrations/INT-000001/finalize
```

The integration reaches:

```text
FINALIZED
```

---

### 21. Generate the Final Integration Report

Use:

```text
GET /integrations/{integration_id}/report
```

For example:

```text
GET /integrations/INT-000001/report
```

The report combines the collected Stage 1 evidence, including:

* integration information
* module profile
* system metrics
* performance analysis
* security findings
* blockchain transactions
* integration event history
* final lifecycle status

The report can be saved as a JSON file under the `reports` directory.

For example, in PowerShell:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/integrations/INT-000001/report" |
ConvertTo-Json -Depth 20 |
Set-Content "reports\INT-000001_report.json" -Encoding UTF8
```

Replace `INT-000001` with the integration ID generated during your run.

---

### 22. Run the Demonstration Script

After generating the report, run:

```powershell
python scripts\demo.py
```

The demonstration script reads the generated report and displays:

* integration information
* proposed module profile
* performance observations
* security analysis
* blockchain transaction
* event history
* final report status

---

### 23. Expected Stage 1 Result

A successful execution should produce evidence corresponding to the following lifecycle:

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

The database should contain the corresponding records for the integration, measurements, events, analyses, security findings, and blockchain transactions.

The exact numeric measurements, transaction hash, contract address, gas usage, and integration ID can differ between runs because they depend on the local machine and the fresh Hardhat blockchain state.

---

### 24. Reproducibility Notes

The following points are important when reproducing the project:

* The project uses SQLite; no separate database server is required.
* Hardhat provides the local blockchain; Forge, Cast, and Anvil are not required.
* The local blockchain must remain running while blockchain-related operations are performed.
* FastAPI must remain running while Swagger/API operations are performed.
* A fresh Hardhat node can generate different contract addresses and transaction hashes.
* Integration IDs are generated automatically from the integrations currently stored in the database.
* The current security analyzer is a prototype pattern-based detector and should not be interpreted as a complete smart-contract vulnerability scanner.
* Stage 1 collects and analyzes evidence. It does not train a machine-learning model or generate ML-based risk predictions.

This procedure allows another user to clone the repository, install the required dependencies, initialize the database, compile and deploy the smart contract, execute the Stage 1 integration workflow, store the observations, and generate the final integration report.




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
