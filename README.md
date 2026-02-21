# Optimized Multi-Agent Customer Support System (Supabase + Google ADK)

This project features an optimized, high-performance customer support system. By consolidating multiple specialized agents into a single **Master Agent** with a flat toolset, we have reduced API costs and latency by **50%** while maintaining the same sophisticated capabilities.

## 🌊 Optimized Architecture & Request Flow

In our optimized model, the "Master Agent" acts as a single point of intelligence that has direct access to all system tools, eliminating the overhead of hierarchical routing.

```mermaid
flowchart LR
    User([fa:fa-user Customer Query]) --> Master["fa:fa-robot Master Support Agent (Gemini Flash)"]
    
    subgraph "Unified Intelligence Layer (multi_agent.py)"
        Master -- "Billing/Invoices/Orders" --> MCP[fa:fa-database MCP Toolset]
        Master -- "Tech Diagnostics" --> Tech[fa:fa-microchip Logic Layer]
        Master -- "Returns Processing" --> Returns[fa:fa-undo Returns Toolset]
    end
    
    MCP --> Supabase[(fa:fa-cloud Supabase CRM Database)]
    Returns --> Supabase

    %% Styling
    style Master fill:#4285F4,stroke:#333,stroke-width:2px,color:#fff
    style Supabase fill:#FF9900,stroke:#333,stroke-width:2px,color:#fff
    style User fill:#666,color:#fff
```

## 🏗️ Architecture Overview

The system has been transformed from a hierarchical routing model to a **Unified Master Agent** model:

1.  **Consolidated Intelligence**: A single `LlmAgent` now possesses the combined skills of the former specialists (Billing, Returns, Tech, and Orders).
2.  **Direct Tool Integration**: The agent invokes tools directly via **MCP (Model Context Protocol)** for database actions and **Native Python Functions** for returns logic.
3.  **Cost Efficiency**: Instead of 4+ API requests per query (Router -> Specialist -> Tool -> Answer), the system now completes most tasks in **2 requests**.

---

## 📁 Project Structure

- `multi_agent.py`: The core application. Defines the **Master Support Agent** and its tool integrations.
- `returns_service.py`: Modular business logic for the Returns department. Imported locally as a high-speed tool.
- `returns_api.py`: (Optional) Can still be used if you wish to expose the Returns logic as a standalone A2A microservice.
- `schema.sql` / `seed.sql`: Database schema and mock data for Supabase.
- `.env`: (Not committed) Stores `GEMINI_API_KEY` and `DATABASE_URL`.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.11+
- A [Supabase](https://supabase.com) project.
- A [Google Gemini API Key](https://aistudio.google.com/app/apikey).

### 2. Install Dependencies
```bash
pip install psycopg2-binary python-dotenv google-adk a2a-sdk uvicorn mcp
```

### 3. Configure Environment Variables
Copy the example file and fill in your credentials:
```bash
cp .env.example .env
```
Edit `.env` and set:
- `GEMINI_API_KEY` — your Google Gemini API key.
- `DATABASE_URL` — your Supabase PostgreSQL connection string (e.g. `postgresql://postgres:<password>@<host>:5432/postgres`).

### 4. Seed the Database
Run the schema and seed scripts against your Supabase database:
```bash
python create_tables.py
python run_seed.py
```

### 5. Running the System

#### Option A — CLI Test Runner
Execute the built-in test harness that fires three sample queries:
```bash
python multi_agent.py
```

#### Option B — ADK Dev UI (Recommended for Interactive Testing)
The Google ADK ships with a browser-based Dev UI that lets you chat with your agent in real time.

1. **Launch the Dev UI** — point `adk web` at the project root (the parent directory that contains the `agents/` folder):
   ```bash
   adk web .
   ```
   This starts a local FastAPI server (default `http://localhost:8000`).

2. **Open the UI** — navigate to [http://localhost:8000](http://localhost:8000) in your browser.

3. **Select the agent** — in the top-left dropdown, choose **`agents`** (the folder name that contains `agent.py`). The Dev UI auto-discovers any module that exports a `root_agent`.

4. **Start chatting** — type a message in the chat box and press **Send**. Try the sample queries below to exercise every skill.

---

## 🧪 Testing the Agent

Use these sample prompts to verify each capability:

| Skill | Sample Prompt |
|-------|---------------|
| **Billing / Invoice** | *"How much was I charged for order b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b13?"* |
| **Order Status** | *"What is the status of order b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b13?"* |
| **Returns** | *"I want to return my order b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b13."* |
| **Tech Support** | *"My portal shows a 500 error when I log in. I'm on Chrome 120, Windows 11."* |

> **Tip:** In the ADK Dev UI you can inspect every tool call and LLM reasoning step in the right-hand panel — great for debugging and demos.

---

## 🤖 Integrated Skills
- **Order Management**: Checked status and performs cancellations via MCP.
- **Billing Oversight**: Verifies payments and invoice details via MCP.
- **Returns Specialist**: Handles return eligibility (30-day policy) and **initiates returns**.
- **Tech Diagnostics**: Gather structured bug reports for engineering escalation.

## 🧠 Large Language Model (LLM)
- **Model**: `gemini-flash-latest` (1.5 Flash).
- **Benefit**: Chosen for its high rate limits and exceptional speed-to-accuracy ratio in tool calling.

## 🛠️ Key Technologies
- **Google ADK**: Framework for building autonomous agents.
- **MCP (Model Context Protocol)**: used to expose database capabilities safely.
- **Supabase**: Cloud PostgreSQL backend.
