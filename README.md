📦 Serverless Function Execution Platform

A mini serverless platform to deploy, run, and monitor code functions using FastAPI, Docker, and React.

✅ Features

🔁 Deploy and manage serverless functions (create/update/delete)

🐳 Docker-based code execution engine (Python functions)

📊 Metrics Dashboard with charts, execution logs, and filters

📦 Pre-built container pool to reduce latency

⚙️ FastAPI backend, React frontend

🛠️ Technologies Used

Layer

Stack

Backend

FastAPI + SQLAlchemy + SQLite

Frontend

React + Axios + Chart.js

Execution

Docker (Python 3.9-slim base)

🚀 How to Run the Project

1. Clone the Repo & Navigate

cd ~/ccproject

2. Set Up Virtual Environment (Backend)

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

3. Start the Backend (FastAPI)

uvicorn src.main:app --reload

4. Start the Frontend (React)

cd frontend
npm install
npm start

Make sure React is running at http://localhost:3000 and FastAPI at http://127.0.0.1:8000

🔗 API Endpoints (FastAPI)

GET /functions/ → List all functions

POST /functions/ → Create new function

PUT /functions/{id} → Update function

DELETE /functions/{id} → Delete function

POST /execute/ → Execute function code

GET /metrics/ → Fetch execution metrics with optional filters:

runtime= (e.g., docker)

success=true/false

from_ts / to_ts

📊 Metrics JSON Format

{
  "timestamp": 1712080123.456,
  "runtime": "docker",
  "duration": 1.23,
  "success": true
}

Logged to metrics.json after every execution.

📁 Project Structure

ccproject/
├── src/
│   ├── main.py         # FastAPI app
│   ├── models.py       # DB Models
│   ├── executor.py     # Docker execution logic
│   ├── metrics.py      # Metric logger
├── docker_images/
│   └── python/Dockerfile
├── requirements.txt
├── client/           # React App
│   └── ...
└── README.md

