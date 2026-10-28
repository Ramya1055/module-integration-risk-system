# Module Integration Observability & Security Data Collection System

A research prototype for observing smart-contract module integrations, collecting runtime and blockchain evidence, assessing integration risk, recording human-reviewed decisions, and preparing reviewed data for experimental machine-learning research.

**Repository:** [module-integration-risk-system](https://github.com/Ramya1055/module-integration-risk-system)

> **Research disclaimer:** Rule-based findings are not proof of exploitability. The Stage 3 ML pipeline is experimental and must not be treated as a production-validated security predictor.

## Documentation

- [Phase 1 README — Original implementation and setup](docs/PHASE1_README.md)
- Interactive API documentation: `http://127.0.0.1:8010/docs` when the backend is running.

## 1. Project Overview

When a smart-contract module is integrated into an existing system, successful compilation or transaction execution alone does not establish that the integration is safe.

This project provides a structured workflow to observe module integrations, collect execution evidence, analyze security-related behavior, assess risk, support human review, and generate reports.

The system follows:

**Observe → Measure → Detect → Record → Analyze → Assess → Review → Report**

The project extends basic integration observability with assessment management, local blockchain registry publication, and an experimental ML data-preparation pipeline.

### Objectives

- Profile existing and proposed Solidity modules.
- Collect runtime and system performance measurements.
- Record blockchain transactions and execution evidence.
- Identify security-related patterns and recorded invariant violations.
- Generate preliminary rule-based risk assessments.
- Record human review decisions and reviewer notes.
- Publish reviewed assessment information to a configured local blockchain registry.
- Prepare reviewed integration data for experimental ML research.
- Present integration information and findings through the frontend and REST API.

## 2. Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| Database | SQLite, SQLAlchemy |
| Runtime monitoring | psutil |
| Data processing | pandas |
| Smart contracts | Solidity |
| Local blockchain | Hardhat Network |
| Blockchain integration | Web3.py |
| Frontend | HTML, CSS, JavaScript |
| Testing | pytest |
| ML data preparation | Python and pandas |

A separate database server is not required. The blockchain demonstration uses a local Hardhat development network.

## 3. System Architecture

```text
Existing Module + Proposed Module
                |
                v
        Integration API
                |
                v
       Integration Workflow
                |
      +---------+----------+
      |         |          |
      v         v          v
   Profiling  Runtime   Blockchain
              Monitor    Evidence
      |         |          |
      +---------+----------+
                |
                v
       Security and Performance
              Analysis
                |
                v
        Evidence Stored in SQLite
                |
                v
       Rule-Based Risk Assessment
                |
                v
            Human Review
                |
         +------+------+
         |             |
         v             v
   Reports and     Registry
   Dashboard      Publication
         |
         v
   Reviewed Dataset
         |
         v
   Stage 3 ML Pipeline
```

## 4. Integration Lifecycle

The API supports a staged integration lifecycle. Depending on the operation and current state, the workflow includes:

1. **Create:** Record the integration metadata and module names.
2. **Initialize:** Prepare the integration and collect module information.
3. **Baseline:** Capture initial system measurements.
4. **Monitor:** Collect runtime samples and observe relevant execution activity.
5. **Complete:** Record completion of the integration activity.
6. **Analyze:** Evaluate performance and security-related evidence.
7. **Finalize:** Store the integration evidence and generate a report.
8. **Assess:** Generate a preliminary rule-based risk assessment.
9. **Review:** Record a human decision, reviewed risk level, and notes.
10. **Publish:** Where configured, publish reviewed assessment information to the local registry.
11. **Prepare research data:** Export reviewed records and check whether the dataset is suitable for experimental training.

The integration lifecycle and the assessment-review lifecycle are related but distinct.

## 5. Module Profiling

The module profiler extracts supported structural information from Solidity source files, such as:

- Source lines
- Functions and state variables
- External-call patterns
- Events and modifiers
- Payable functions
- Interfaces and dependencies

The current profiler is a prototype and may rely on source-pattern matching. It is not a complete Solidity parser or semantic analyzer.

## 6. Runtime Monitoring and Performance Analysis

Runtime monitoring uses `psutil` to collect system-level measurements such as CPU usage, memory usage, and available runtime error information.

Performance analysis compares baseline measurements with runtime observations. Depending on available data, reports may include:

- Baseline CPU and memory
- Average runtime CPU and memory
- Changes relative to baseline
- Number of runtime samples
- Recorded runtime errors

Measurements are environment-dependent and may include activity unrelated to the proposed module. They should not be interpreted as universal performance guarantees.

## 7. Security Analysis

The implemented analyzer checks supported source-code patterns and available execution evidence. Examples include:

- `delegatecall` usage
- Low-level call patterns
- Recorded execution failures
- Storage-canary invariant changes
- Reentrancy-related findings where supported by the implemented rules

Findings are recorded with supporting evidence where available.

**Interpretation matters:**

- `delegatecall` usage is not automatically a vulnerability.
- A storage-canary change indicates an invariant violation requiring investigation; it does not independently prove exploitability.
- A failed transaction does not automatically establish a security vulnerability.
- Zero findings means the implemented checks did not identify findings in that run. It is not proof that the contract is secure.

This prototype is not a replacement for comprehensive smart-contract auditing, formal verification, or a full vulnerability-analysis toolchain.

## 8. Rule-Based Assessment and Human Review

The assessment component derives a preliminary risk level from collected evidence using implemented rules. Supported risk levels include LOW, MEDIUM, and HIGH.

The preliminary assessment is distinct from a human-reviewed decision. The review workflow supports recording:

- Reviewed risk level
- Reviewer decision, such as `APPROVE` or `REJECT`
- Reviewer notes

Review status and preliminary risk must be interpreted alongside the available findings and evidence. A human decision is a recorded review outcome, not independent proof of security.

## 9. Blockchain Evidence and Assessment Registry

The blockchain integration uses Web3.py and a local Hardhat Network.

Depending on the operation, transaction evidence can include:

- Transaction hash
- Sender and receiver addresses
- Block number
- Gas limit and gas used
- Transaction execution status

The project also includes an assessment registry contract and publication service for recording reviewed assessment information on the configured blockchain.

Publication-related fields include registry address, transaction hash, report hash, publication status, and errors.

A report hash can help verify that a report matches a previously hashed version when the original report and hashing procedure are available. Blockchain publication does not independently prove that an assessment is correct or that a contract is secure.

The demonstration uses a local development blockchain, not a production network.

## 10. Frontend and Reports

The FastAPI application serves the frontend and exposes endpoints for integration and assessment workflows.

The interface supports presenting integration information, collected evidence, security findings, assessment status, and reports. Available information depends on the integration and assessment records.

The integration report endpoint provides structured evidence, including available integration metadata, module profiles, metrics, performance analysis, security findings, blockchain transactions, and lifecycle events.

Reports should distinguish observed measurements, rule-based findings, human decisions, blockchain publication records, and any experimental ML outputs.

## 11. Stage 3: Experimental ML Pipeline

Stage 3 prepares reviewed integration data for research into machine-learning-based security risk assessment.

The pipeline includes scripts for dataset export, review-queue generation, dataset preparation, readiness checks, and model training.

Relevant scripts include:

```text
scripts/
├── check_stage3_readiness.py
├── export_research_dataset.py
├── export_stage3_review_queue.py
├── prepare_stage3_dataset.py
└── train_stage3_model.py
```

Verify the current filenames in the repository before running a script.

### Pipeline

```text
Collected Integration Evidence
              |
              v
         Dataset Export
              |
              v
       Reviewed Labels
              |
              v
      Dataset Preparation
              |
              v
       Readiness Checks
              |
       +------+------+
       |             |
       v             v
    Blocked         Ready
                     |
                     v
               Model Training
                     |
                     v
             Model Evaluation
```

The training workflow checks reviewed-label availability and dataset readiness. It is designed to avoid treating unreviewed assessments as reliable ground-truth labels.

### ML limitations

- Training requires sufficient valid reviewed labels.
- Missing values must be handled using a documented preparation process fitted on training data only.
- Dataset readiness depends on the current data and the readiness-check results.
- Producing a model artifact does not establish predictive quality.
- Generalization, evaluation metrics, calibration, and suitability for security decisions require separate validation.

Do not interpret experimental outputs as validated vulnerability probabilities or guarantees that a module is safe to integrate.

## 12. API Reference

The backend provides the following principal endpoints. Consult Swagger UI for current request schemas, parameters, and responses.

| Endpoint | Purpose |
|---|---|
| `GET /health` | Check application health |
| `GET /integrations` | List integrations |
| `POST /integrations` | Create an integration |
| `POST /integrations/{integration_id}/start` | Start integration processing |
| `POST /integrations/{integration_id}/begin-monitoring` | Begin runtime monitoring |
| `POST /integrations/{integration_id}/runtime-metric` | Record a runtime measurement |
| `POST /integrations/{integration_id}/runtime-samples` | Collect multiple runtime samples |
| `POST /integrations/{integration_id}/complete` | Complete integration activity |
| `POST /integrations/{integration_id}/analyze` | Analyze performance |
| `POST /integrations/{integration_id}/security-analysis` | Run implemented security checks |
| `POST /integrations/{integration_id}/finalize` | Finalize integration evidence |
| `GET /integrations/{integration_id}/report` | Retrieve an integration report |
| `POST /integrations/{integration_id}/blockchain-transaction` | Record transaction evidence |
| `POST /integrations/{integration_id}/onchain/collect` | Collect configured on-chain evidence |
| `GET /assessments` | List assessments |
| `POST /assessments/{integration_id}` | Create an assessment |
| `GET /assessments/{assessment_id}` | Retrieve an assessment |
| `POST /assessments/{assessment_id}/review` | Record a human review |

## 13. Windows Setup

### Prerequisites

Install Python 3.11, Node.js/npm, and Git.

### Clone and install dependencies

```powershell
git clone https://github.com/Ramya1055/module-integration-risk-system.git
cd module-integration-risk-system

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
npm install
```

If PowerShell blocks virtual-environment activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Initialize the database and compile contracts

```powershell
python database\init_db.py
npx hardhat compile
```

If using an existing database, back it up before running any migration. Follow the relevant migration script's instructions when a schema update is required.

### Start Hardhat

Open a separate PowerShell terminal:

```powershell
npx hardhat node
```

Keep this terminal running. The default local RPC endpoint is:

`http://127.0.0.1:8545`

### Start FastAPI

In another terminal, from the repository root:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8010
```

Open:

- Dashboard: `http://127.0.0.1:8010/`
- Swagger UI: `http://127.0.0.1:8010/docs`
- Health check: `http://127.0.0.1:8010/health`

Use the configured port if it differs in your environment.

### Deploy and execute

Where required, deploy the test contract using the repository's deployment script:

```powershell
python scripts\deploy_test_contract.py
```

Use the address printed by the script in subsequent integration requests.

Execute the integration workflow through Swagger UI or the API, following the available endpoint schemas and lifecycle requirements. Retrieve the final report using:

```text
GET /integrations/{integration_id}/report
```

The previous Phase 1 walkthrough, including its detailed API sequence and demonstration notes, is preserved in [docs/PHASE1_README.md](docs/PHASE1_README.md).

## 14. Testing

Run the tests from the repository root:

```powershell
python -m pytest -q
```

A previous recorded test run completed with 10 passed and one warning. This is a historical result, not a guarantee about the current checkout. Run the command to verify the current state.

## 15. Project Structure

```text
module-integration-risk-system/
├── backend/
│   └── app/
│       ├── api/
│       ├── services/
│       └── main.py
├── blockchain/
│   └── contracts/
├── database/
│   ├── db.py
│   ├── models.py
│   └── init_db.py
├── docs/
│   └── PHASE1_README.md
├── frontend/
│   └── index.html
├── monitoring/
├── security/
├── scripts/
├── tests/
├── reports/
├── requirements.txt
├── package.json
├── hardhat.config.ts
└── README.md
```

This is a high-level overview; consult the repository for the complete current directory structure.

## 16. Reproducibility and Data Handling

- SQLite is used as the local database; a separate database server is not required.
- The local Hardhat node must remain running for blockchain-dependent operations.
- Contract addresses, transaction hashes, block numbers, and gas measurements may change between runs.
- Integration IDs depend on the records already stored in the database.
- CPU and memory measurements depend on the machine and current workload.
- Back up the SQLite database before migrations or destructive operations.
- Do not commit private keys, credentials, secrets, or sensitive local data.
- Review exported datasets and reports before sharing them publicly.

## 17. Research Direction

The broader research direction is **Multi-Modal Learning for Intelligent Security Risk Assessment of Smart Contracts**.

Potential research inputs include source-code characteristics, control-flow and data-flow representations, call-graph information, runtime observations, and on-chain execution evidence. Candidate approaches may include code transformers, recurrent neural networks, graph neural networks, and multimodal architectures.

These are research directions, not claims that every model or modality is already implemented in the current application.

## 18. Summary

The project provides a foundation for examining smart-contract module integrations through structured evidence collection, runtime monitoring, blockchain observations, rule-based assessments, human review, and report generation.

Its Stage 3 pipeline prepares reviewed integration data for experimental ML research.

The central principle is to distinguish **what was observed, what the implemented rules detected, what a human reviewer decided, and what an ML model can actually demonstrate**.
