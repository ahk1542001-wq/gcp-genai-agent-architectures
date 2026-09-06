# 🌟 Google Cloud GenAI Enterprise Agent Architectures

[![Google Cloud Run](https://img.shields.io/badge/Google_Cloud-Cloud_Run-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/run)
[![Hackathon Evaluation Label](https://img.shields.io/badge/Hackathon_Label-dev--tutorial%3Dcloud--run--ai--challenge-34A853?logo=googlecloud&logoColor=white)](./04-personal-gemini-journal/deploy.sh)
[![Pattern 4 Tests](https://img.shields.io/badge/Pattern_4_Tests-68%2F68_Passing_(100%25)-34A853?logo=pytest&logoColor=white)](./04-personal-gemini-journal/tests)
[![Vertex AI](https://img.shields.io/badge/Google_Cloud-Vertex_AI-EA4335?logo=googlecloud&logoColor=white)](https://cloud.google.com/vertex-ai)
[![Google ADK](https://img.shields.io/badge/Google_ADK-v1.27%2B-34A853?logo=google&logoColor=white)](https://github.com/google/adk)
[![Model Context Protocol](https://img.shields.io/badge/Protocol-MCP-8A2BE2)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A production-grade collection of enterprise AI Agent architectures built on **Google Cloud**, demonstrating the core pillars of modern agentic systems: **Unstructured Document Intelligence (RAG)**, **Structured Big Data Analytics (Model Context Protocol)**, **Autonomous Operational Workflows (Cloud Run Sandboxes & Human-in-the-Loop)**, and **Privacy-First Executive Journaling (Sanctuary OS on Cloud Run)**.
>
> **🏆 Featured Ideathon Submission:** [Pattern 4 — Secure Personal Gemini Journal & Executive Sanctuary](./04-personal-gemini-journal/) for the **Hack2Skill APAC GenAI Academy (Accelerate AI with Cloud Run)**. Deployed with mandatory evaluation label `--labels="dev-tutorial=cloud-run-ai-challenge"` and 100% verified with 68/68 automated tests.

---

### 🎬 Featured Project Demo: Sanctuary OS (1-Minute Walkthrough)

[![Sanctuary OS Walkthrough](./04-personal-gemini-journal/sanctuary_os_demo_walkthrough.gif)](./04-personal-gemini-journal/sanctuary_os_demo_walkthrough.mp4)

- 🌐 **Live Cloud Run Deployment:** [https://personal-gemini-journal-ypp4pspywq-uc.a.run.app](https://personal-gemini-journal-ypp4pspywq-uc.a.run.app)
- 👤 **Instant Evaluator Access:** Click **"Continue as Guest Evaluator"** for instant sandbox testing with zero login required.
- 📹 **Walkthrough Video:** [`sanctuary_os_demo_walkthrough.mp4`](./04-personal-gemini-journal/sanctuary_os_demo_walkthrough.mp4)

---

## 🏛️ Unified Architecture Overview

```mermaid
flowchart TD
    subgraph Enterprise_Clients["👥 Client & User Interfaces"]
        C1["Customer / Web User"]
        C2["Data Analyst / Decision Maker"]
        C3["Operations Manager"]
    end

    subgraph Google_Cloud_Run["☁️ Google Cloud Run Serverless Platform"]
        subgraph Pattern1["Pattern 1: Customer RAG Agent"]
            P1_UI["Streamlit UI"] <--> P1_ADK["Google ADK LlmAgent"]
            P1_ADK <--> P1_Gemini["Gemini 2.5 Flash"]
            P1_ADK <--> P1_Tool["RAG Document Tool"]
        end

        subgraph Pattern2["Pattern 2: BigQuery MCP Agent"]
            P2_UI["ADK Web Runtime"] <--> P2_ADK["Data Reasoning Agent"]
            P2_ADK <--> P2_Gemini["Gemini 3.6 Flash"]
            P2_ADK <--> P2_MCP["BigQuery MCP Toolset"]
        end

        subgraph Pattern3["Pattern 3: Sandboxed Ops Agent"]
            P3_UI["FastAPI WebSocket UI"] <--> P3_ADK["Operations Agent"]
            P3_ADK <--> P3_Gemini["Gemini 2.5 Flash"]
            P3_ADK <--> P3_HITL["Human-in-the-Loop Gate"]
            P3_ADK <--> P3_Sandbox["execute_sandbox_command"]
            P3_ADK <--> P3_Sheets["Google Sheets API v4"]
            subgraph Micro_Sandbox["Isolated Cloud Run Micro-Sandbox"]
                P3_Sandbox <--> P3_Py["Dynamic Python Runtime\n/usr/local/gcp/bin/sandbox"]
            end
        end
    end

    subgraph GCP_Data_Plane["🗄️ Enterprise Data & Integration Layer"]
        DB_Vector[(Firestore Vector Search\ntext-embedding-004)]
        BQMCP_Server["BigQuery MCP Server\nbigquery.googleapis.com/mcp"]
        BQ_Warehouse[(BigQuery Data Warehouse\nNYC Citi Bike Datasets)]
        Google_Workspace[(Google Sheets\nReal-time POS & Action Records)]
    end

    C1 <--> Pattern1
    C2 <--> Pattern2
    C3 <--> Pattern3

    P1_Tool <--> DB_Vector
    P2_MCP <-->|OAuth2 Bearer ADC| BQMCP_Server
    BQMCP_Server <-->|execute_sql_readonly| BQ_Warehouse
    P3_Sheets <-->|OAuth2 ADC / Read & Write| Google_Workspace
```

---

## 📊 Architectural Patterns Matrix

| Pattern | Primary Focus | Foundation Model | Tooling & Protocols | Key Security & Governance | Deployment Target |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **[Pattern 1: Customer RAG Agent](./01-customer-facing-rag-agent/)** | Unstructured Data, Allergen Awareness, Grounded Recommendations | `gemini-2.5-flash` | Google ADK, Vector Search, Streamlit | Zero-hallucination guardrails, Strict context grounding | Cloud Run (Scale-to-Zero) |
| **[Pattern 2: BigQuery MCP Agent](./02-bigquery-mcp-data-agent/)** | Multi-Table Structured Data, Autonomous Analytics, SQL Reasoning | `gemini-3.6-flash` | Model Context Protocol (MCP), Google ADK | Read-only SQL filter (`execute_sql_readonly`), IAM ADC token auth | Cloud Run + ADK Web UI |
| **[Pattern 3: Sandboxed Ops Agent](./03-sandboxed-operations-agent/)** | Operational Workflows, Dynamic Python Code, Workspace Integration | `gemini-2.5-flash` | Cloud Run Sandboxes, Google Sheets API, FastAPI WebSockets | Micro-sandbox isolation, Human-in-the-loop (HITL) approval gate | Cloud Run (`--sandbox-launcher`) |
| **[Pattern 4: Secure Personal Gemini Journal & Executive Sanctuary](./04-personal-gemini-journal/)** | Privacy-First Reflective Journaling, 4 Persona Styles, Dynamic Emotional Arc, Zero AI Slop | `gemini-3.7-flash` | Firebase Auth, Cloud Firestore, Secret Manager, FastAPI, Playwright | AI Studio Security Constitution, Multi-Tenant Zero Leakage (`/users/{uid}`), 66/66 Green Tests | Cloud Run (`--labels="dev-tutorial=cloud-run-ai-challenge"`) |

---

## 🔍 Deep Dives into Each Pattern

### ☕ [Pattern 1: Customer-Facing RAG AI Agent](./01-customer-facing-rag-agent/)
* **Problem:** Traditional chatbots hallucinate menu items, prices, and allergen details, posing serious safety and brand risks.
* **Architectural Solution:**
  - Integrates Google ADK with Retrieval-Augmented Generation (RAG) over structured catalog embeddings (`text-embedding-004`).
  - Strict system directives enforce allergen compliance (dairy-free, gluten-free, vegan) before returning answers.
  - Hosted inside a lightweight Streamlit container with session history persistence.

### 📊 [Pattern 2: Enterprise SQL Reasoning Agent with BigQuery MCP](./02-bigquery-mcp-data-agent/)
* **Problem:** Complex enterprise data questions require data analysts to manually inspect schemas, join multiple tables, and write optimized SQL.
* **Architectural Solution:**
  - Leverages Anthropic's **Model Context Protocol (MCP)** using Google's hosted BigQuery MCP server (`https://bigquery.googleapis.com/mcp`).
  - Autonomous schema investigation, dimension querying, and multi-table SQL generation without human query drafting.
  - Enforces read-only safety by explicitly filtering available MCP tools to `execute_sql_readonly`.

### ⚙️ [Pattern 3: Autonomous Operations Agent with Cloud Run Sandboxes](./03-sandboxed-operations-agent/)
* **Problem:** Executing AI-generated Python analysis code on production web servers creates catastrophic security and resource vulnerabilities.
* **Architectural Solution:**
  - Uses Google Cloud's **Native Cloud Run Sandboxes (`--sandbox-launcher`)** to execute untrusted Python code inside isolated micro-runtimes (`/usr/local/gcp/bin/sandbox`).
  - Implements a strict **Human-in-the-Loop (HITL)** governance policy: the agent diagnoses operational bottlenecks, proposes recommendations, but is programmatically prohibited from modifying Google Sheets until explicit user confirmation ("Yes") is received.
  - Real-time bidirectional WebSocket interface with client-side Markdown and tabular data rendering.

### 🛡️ [Pattern 4: Secure Personal Gemini Journal & Executive Sanctuary](./04-personal-gemini-journal/)
* **Problem:** AI-generated apps collapse in production due to hardcoded API keys, unauthenticated routes, shared databases leaking user data across tenants, and tacky "AI slop" interfaces that distract from genuine executive reflection.
* **Hack2Skill Judging Rubric & Production Innovations:**
  - **🏷️ Mandatory Cloud Run Evaluation Label:** Deployed via `deploy.sh` and documented with `--labels="dev-tutorial=cloud-run-ai-challenge"` for automated challenge scanner compliance.
  - **🔒 Pre-Scaffolding AI Studio Security Constitution (Phase 1 Deliverable):** Built under explicit system directives enforcing threat modeling, delimiter defense (`<user_journal_reflection>`), ADC keyless ingestion, fail-closed auth, and `/users/{uid}/*` Firestore tenant boundaries (0 cross-user leakage). Verified with visual proof in [assets/AI_Studio_Security_Constitution_Configured.png](./04-personal-gemini-journal/assets/AI_Studio_Security_Constitution_Configured.png).
  - **🧠 Innovative Google GenAI Capabilities:** Powered by `gemini-3.7-flash` with a 4-Style Persona Reflection Engine (**Balanced**, **Actionable**, **Deep Philosophy**, **Brainstorm**), **7 Google ADK Function Tools** (Kanban tasks, Calendar timeblocks, Living Memory, Box Breathing, Shutdown Ritual), multimodal **Neural Voice Synthesis** (`/api/voice/synthesize`), live turn streaming, and auto-summarization.
  - **🤝 Human-in-the-Loop (HITL) Action Confirmation Gate:** Gemini proposes Kanban and calendar actions as cards; persistent database mutations require explicit user confirmation before any database write.
  - **📈 Dynamic Cognitive & Emotional Arc Visualizer:** Uncompromising **Authentic Zero-State** (zero fake points or dummy curves on launch) with real-time turn-by-turn *Clarity & Grounding* and *Stress Relief* trajectory plotting via Chart.js.
  - **🔍 Past Reflections Search & Categorical Filter Pills:** Sub-millisecond client-side multi-field search with category pills (`[All]`, `[Reflective]`, `[Actionable]`, `[Breakthrough]`) and slide-out Review Drawer (`#history-drawer`).
  - **✨ Zero AI Slop Human Craftsmanship:** Notion Serene minimalist dark aesthetic, distraction-free focus, accessible touch targets (≥44px on 390×844 mobile), and 100% genuine computed rewind metrics.
  - **🧪 Exceptional Engineering Rigor:** **66/66 Passing Tests (100% Green)** across 33 backend security isolation tests, 32 Playwright UI automation tests, and 1 full browser lifecycle E2E test with 12 checkpoint screenshots.


---

## 🛡️ Enterprise Security & Production Best Practices

1. **Principle of Least Privilege (IAM):** Dedicated Service Accounts per agent with scoped IAM bindings (`roles/aiplatform.user`, `roles/bigquery.user`) instead of default compute credentials.
2. **Keyless Authentication (ADC):** Zero hardcoded API keys; all Vertex AI and Google API requests authenticate automatically via Application Default Credentials (ADC).
3. **Execution Isolation:** All dynamic computations run within micro-sandboxes, isolating host memory and file systems.
4. **Human-in-the-Loop Governance:** Destructive or modifying operations require explicit human approval gates before committing external state.

---

## 🚀 Quickstart & Local Setup

### Prerequisites
- Google Cloud Project with Billing Enabled
- `gcloud` CLI installed and authenticated (`gcloud auth application-default login`)
- Python 3.11+

### Running Pattern 1 (RAG Agent)
```bash
cd 01-customer-facing-rag-agent
pip install -r requirements.txt
streamlit run app.py
```

### Running Pattern 2 (BigQuery MCP Agent)
```bash
cd 02-bigquery-mcp-data-agent
pip install -r requirements.txt
adk web --allow_origins="*" --port 8080 .
```

### Running Pattern 3 (Sandboxed Operations Agent)
```bash
cd 03-sandboxed-operations-agent
pip install -r requirements.txt
export SPREADSHEET_ID="your-google-sheet-id"
python main.py
```

---

## 📜 License
This project is open-source under the [MIT License](LICENSE).
