# Circuit Breaker — Hackathon Judge Demo Runbook

> **Step-by-Step Instructions to Launch, Test, and Verify the Circuit Breaker Control Plane.**

---

## 1. Environment Setup & Verification

### Step 1: Python Virtual Environment & Dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

### Step 2: Environment Configuration
Copy placeholder configuration:
```bash
cp .env.example .env
```

---

## 2. Launch Commands

### Terminal 1: Backend API Control Plane (Port 8000)
```bash
PYTHONPATH=. ./venv/bin/python -m uvicorn backend.app.main:app --reload --port 8000
```
- API Health Check: `http://localhost:8000/api/health`
- OpenAPI Swagger Specs: `http://localhost:8000/docs`

### Terminal 2: Next.js Frontend Control Plane (Port 3000)
```bash
npm --prefix frontend run dev
```
- Control Plane Dashboard: `http://localhost:3000`

### Terminal 3 (Optional): TrueForge Agent Harness (Port 8790)
```bash
python scripts/verify_trueforge_live.py
```

---

## 3. Judge Navigation & Test Sequence

1. **Overview Landing (`http://localhost:3000`)**: Read system core message and Mermaid architecture map.
2. **TrueForge Agent Console (`http://localhost:3000/agent`)**:
   - Type prompt: `Send 0.01 MON to 0x57d1Cf3D387de087Eda90a1cC81eAc608F7a8f55`
   - Observe live real-time pipeline and Circuit Breaker security panel.
3. **MCP Tool Inspector (`http://localhost:3000/agent/tools`)**: Review 19 FastMCP tools categorized into READ ONLY, PREPARATION, and EXECUTION.
4. **Attack Lab (`http://localhost:3000/attacks`)**: Run one-click attack scenarios (Prompt Injection, Oversized Transfer, Replay, Concurrency Race).
5. **Wallet Overview (`http://localhost:3000/wallet`)**: Inspect Monad Testnet status, Chain ID 10143, and key isolation guarantees.
6. **Guided Demo (`http://localhost:3000/demo`)**: Follow the 60-second judge walkthrough.

---

## 4. One-Command Automated System Verification

To run the complete automated audit (pytest suite, MCP boundary, TrueForge spec, security demo, and frontend build):
```bash
python scripts/verify_all.py
```
