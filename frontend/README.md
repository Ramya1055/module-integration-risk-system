# Module Integration Observability & Security Data Collection System
## Frontend Setup and Usage

### 1. Overview

The frontend provides a dashboard for viewing module integrations, monitoring progress, inspecting machine-generated evidence, reviewing security findings, and examining integration risk assessments.

It communicates with the FastAPI backend, which retrieves integration data and performs the available analysis.

**Important:** The preliminary rule-based assessment is not an ML prediction. The frontend must display ML results as unavailable until a trained model is connected.

### 2. Prerequisites

- Python 3.11
- The project's existing Python virtual environment
- Node.js is not required to run this standalone frontend.
- The FastAPI backend and its configured database
- A modern web browser

### 3. Project structure

```text
module-integration-risk-system/
├── backend/
│   └── app/
├── blockchain/
├── frontend/
│   ├── index.html
│   └── README.md
├── reports/
├── scripts/
├── tests/
└── .venv/
```

### 4. Start the backend

Open PowerShell in the project root:

```powershell
cd C:\Users\Ramya\module-integration-risk-system
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Start FastAPI on port 8010:

```powershell
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8010
```

Keep this terminal open.

If the command reports that `backend.app.main` cannot be imported, check the project's actual FastAPI application entry point and use that module path instead.

### 5. Verify the backend

Open another PowerShell terminal and run:

```powershell
Invoke-RestMethod http://127.0.0.1:8010/health
```

You can also open the API documentation:

http://127.0.0.1:8010/docs

The health endpoint should respond successfully, and the API documentation should load if the server is running correctly.

### 6. Start the frontend

Open a separate PowerShell terminal in the project root:

```powershell
python -m http.server 5500 --directory frontend
```

Keep this terminal open.

Open the frontend in your browser:

http://127.0.0.1:5500

The frontend and backend use separate ports:

- Frontend: `http://127.0.0.1:5500`
- Backend API: `http://127.0.0.1:8010`

### 7. Using the dashboard

1. Open the dashboard and verify the API connection.
2. View existing integrations and select an integration to inspect.
3. Review the existing and proposed modules and their available profiles.
4. Follow the integration lifecycle and review recorded runtime metrics.
5. Inspect security findings and on-chain observations.
6. Examine the preliminary assessment and its supporting evidence.
7. Review the machine-generated technical report.
8. Check the ML section for model availability.
9. Complete human assessment review when the relevant workflow is available.
10. Export or print the report when supported by the frontend.

### 8. Troubleshooting

#### Error: Cannot reach http://127.0.0.1:8010

1. Ensure the FastAPI server is running.
2. Confirm that it is listening on port 8010.
3. Open `http://127.0.0.1:8010/health`.
4. If the health endpoint works but the dashboard cannot fetch data, inspect browser developer tools for a CORS error.
5. If the API returns 404, verify the requested endpoint and integration ID.

#### Error: CORS policy blocked the request

Configure the FastAPI application's CORS middleware to allow the development frontend origin:

`http://127.0.0.1:5500`

Do not disable CORS security globally. Add the appropriate origin to the existing middleware configuration.

#### Error: Connection refused

Check whether the server is running and whether another process is using port 8010:

```powershell
Test-NetConnection 127.0.0.1 -Port 8010
```

#### Error: Frontend page does not load

Confirm that the frontend server is running and that `frontend/index.html` exists.

### 9. Research and security limitations

- A finalized integration does not automatically mean the proposed module is safe to integrate.
- A HIGH preliminary risk level is not proof of exploitability.
- Failed calls, invariant violations, and static-analysis findings must be interpreted using their evidence and context.
- Blockchain transaction success does not by itself prove that module execution was safe.
- ML predictions must only be displayed when an actual trained model produces them.
- Final approval should follow the project's assessment and human-review process.

### 10. Stop the development servers

In each server terminal, press `Ctrl+C`.

This stops the development server without deleting project data.