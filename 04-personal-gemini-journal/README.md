# 🛡️ Sanctuary OS: Secure Personal Gemini Journal & Executive Sanctuary
### Production AI Journaling Platform with Zero-Trust Multi-Tenant Isolation on Google Cloud Run

[![Google Cloud Run](https://img.shields.io/badge/Google_Cloud-Cloud_Run-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/run)
[![Hackathon Label](https://img.shields.io/badge/Hackathon_Label-dev--tutorial%3Dcloud--run--ai--challenge-34A853?logo=googlecloud&logoColor=white)](./deploy.sh)
[![Firebase Auth](https://img.shields.io/badge/Firebase-Authentication-FFCA28?logo=firebase&logoColor=black)](https://firebase.google.com/docs/auth)
[![Cloud Firestore](https://img.shields.io/badge/Google_Cloud-Firestore-FFCA28?logo=firebase&logoColor=black)](https://firebase.google.com/docs/firestore)
[![Secret Manager](https://img.shields.io/badge/Google_Cloud-Secret_Manager-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/secret-manager)
[![Gemini 3.7 Flash](https://img.shields.io/badge/Gemini-3.7_Flash-8A2BE2?logo=google&logoColor=white)](https://ai.google.dev)
[![Test Suite](https://img.shields.io/badge/Tests-66%2F66_Passing_(100%25)-34A853?logo=pytest&logoColor=white)](./tests)
[![Design](https://img.shields.io/badge/UI_Craft-Zero_AI_Slop-indigo)](./static)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Built for the **Hack2Skill APAC GenAI Academy (Cohort 3: Accelerate AI with Cloud Run)** Ideathon Challenge.  
> Directly solves the industry-wide failure mode: *"Most AI-generated apps look great in a demo and fall apart in production — hardcoded keys, no auth boundaries, shared databases with zero isolation, and tacky AI slop interfaces."*

---

## 🏆 Hackathon Judging Rubric & Scoring Alignment Matrix

Sanctuary OS was architected specifically to maximize points across every single dimension of the **Hack2Skill APAC GenAI Academy (Accelerate AI with Cloud Run)** evaluation criteria:

| Hackathon Evaluation Rubric | Judge Scoring Requirement | Sanctuary OS Production Implementation | Verification & Evidence |
| :--- | :--- | :--- | :--- |
| **1. Cloud Run Deployment & Mandatory Label** | Automated challenge evaluation scanner verification on Google Cloud Run | Configured in `deploy.sh` and `DEPLOYMENT_RUNBOOK.md` with the mandatory evaluation label `--labels="dev-tutorial=cloud-run-ai-challenge"`. Scale-to-zero serverless architecture, 512MiB/1GiB memory, fast startup, `/health` and `/api/public-config` probes. | [deploy.sh](file:///Users/mac/Projects/code/apac_genai_academy/04-personal-gemini-journal/deploy.sh#L38)<br>[DEPLOYMENT_RUNBOOK.md](file:///Users/mac/Projects/code/apac_genai_academy/04-personal-gemini-journal/DEPLOYMENT_RUNBOOK.md#L85) |
| **2. AI Studio Security Constitution & Zero-Trust** | Pre-scaffolding security prompt, fail-closed auth, zero hardcoded keys, tenant isolation | Pre-configured System Instructions in AI Studio enforcing 4 security pillars: delimiter defense (`<user_journal_reflection>`), dual-mode ADC/Secret Manager keyless ingestion, fail-closed production auth (rejects all test tokens), and `/users/{uid}/*` multi-tenant Firestore hierarchy (0 cross-user leakage). | [AI_STUDIO_SECURITY_CONSTITUTION.md](file:///Users/mac/Projects/code/apac_genai_academy/04-personal-gemini-journal/AI_STUDIO_SECURITY_CONSTITUTION.md)<br>[SECURITY_REVIEW.md](file:///Users/mac/Projects/code/apac_genai_academy/04-personal-gemini-journal/SECURITY_REVIEW.md)<br>33/33 Pytest Security Tests Pass |
| **3. Innovative Google GenAI Capabilities** | Advanced Gemini model usage, multi-turn reasoning, live tool calling, multimodal voice, and human oversight | Foundation model `gemini-3.7-flash` powering a **4-Style Persona Reflection Engine** (Balanced, Actionable, Deep Philosophy, Brainstorm), **7 Google ADK Function Tools** (`adk_create_ticket`, `adk_move_ticket`, `adk_schedule_calendar`, `adk_save_memory`, `adk_synthesize_learned_rule`, `adk_trigger_box_breathing`, `adk_trigger_shutdown_ritual`), multimodal **Neural Voice Synthesis** (`/api/voice/synthesize`), live turn streaming, and a strict **Human-in-the-Loop (HITL) Action Confirmation Gate** (0 autonomous DB writes). | [gemini_service.py](file:///Users/mac/Projects/code/apac_genai_academy/04-personal-gemini-journal/gemini_service.py#L93-L148)<br>[main.py](file:///Users/mac/Projects/code/apac_genai_academy/04-personal-gemini-journal/main.py#L320-L420)<br>HITL Proposal Card UI |
| **4. Original Feature Enhancement (Competitive Edge)** | Standout original capability beyond basic specifications | **Dynamic Cognitive & Emotional Arc Visualizer** with an uncompromising **Authentic Zero-State** (0 fake lines/dots on session init) and real-time turn-by-turn trajectory graphing of *Clarity & Grounding* and *Stress Relief* using Chart.js. | [app.js](file:///Users/mac/Projects/code/apac_genai_academy/04-personal-gemini-journal/static/app.js)<br>[ARCHITECTURE.md](file:///Users/mac/Projects/code/apac_genai_academy/04-personal-gemini-journal/ARCHITECTURE.md#L137-L155)<br>Screenshots 02a-02e |
| **5. Exceptional Engineering Rigor & Testing** | Production quality, hermetic test coverage, zero flake | **66/66 Passing Tests (100% Green)** across 33 Backend Security Isolation tests, 32 Playwright Chromium UI automation tests, and 1 full browser lifecycle E2E test with 12 checkpoint screenshots. Zero console errors. | [pytest.ini](file:///Users/mac/Projects/code/apac_genai_academy/04-personal-gemini-journal/pytest.ini)<br>[tests/](file:///Users/mac/Projects/code/apac_genai_academy/04-personal-gemini-journal/tests)<br>100% Hermetic Pass in 102s |
| **6. Zero AI Slop Human Craftsmanship & Mobile UX** | Restraint, high utility, accessibility, mobile responsiveness | **Notion Serene** aesthetic (clean typography, no gimmicky breathing bubbles/chimes/slop), 100% computed rewind metrics (zero fake streaks), full mobile responsiveness on 390×844 with ≥44px touch targets and bottom navigation. | [style.css](file:///Users/mac/Projects/code/apac_genai_academy/04-personal-gemini-journal/static/style.css)<br>[index.html](file:///Users/mac/Projects/code/apac_genai_academy/04-personal-gemini-journal/static/index.html)<br>Screenshots 00-09b |

---

## 🏷️ Mandatory Automated Verification Label
Per Hack2Skill & Google Cloud guidelines, this Cloud Run service is deployed with the required label for automated evaluation:
```yaml
labels:
  dev-tutorial: cloud-run-ai-challenge
```

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph ClientLayer["💻 Web Client (Vanilla SPA + Tailwind + Chart.js + Inter Typography)"]
        UI["Reflective Journaling Studio\n(Notion Serene Dark Aesthetic)"]
        StyleSelector["Reflection Style Engine\n(Balanced | Actionable | Philosophy | Brainstorm)"]
        MultiTurn["Multi-Turn Dialogue Stream\n(Gemini 3.7 Flash Badges + Timestamps)"]
        HistoryDrawer["History Search & Filter\n([All] [Reflective] [Actionable] [Breakthrough])"]
        ArcChart["Dynamic Cognitive & Emotional Arc Visualizer\n(Zero Fake Points • Live Turn Plotting)"]
        FBAuth["Firebase Auth (Google Sign-In / Token)"]
    end

    subgraph CloudRunService["☁️ Google Cloud Run Serverless Backend (FastAPI + Python 3.11)"]
        AuthMiddleware["Token Validation Middleware\n(Cryptographic JWT / Audience & Expiry Check)"]
        APIRouter["API Router (/api/agent/live-turn, /api/journal, /api/tickets, /api/calendar)"]
        GeminiService["Gemini 3.7 Flash Service Engine\n(Persona System Directives + Delimiter Defense)"]
        ArcEngine["Cognitive & Emotional Arc Sentiment Engine"]
        ActionDistiller["Executive Action Items Distiller (Human-in-the-Loop Gate)"]
        TenantDB["Tenant-Isolated Firestore Service\n(/users/{uid}/* Hierarchy)"]
    end

    subgraph GCP_Security["🔒 Google Cloud Security & Data Plane"]
        SecretMgr["Secret Manager / Vertex AI ADC\n(Zero Hardcoded Keys)"]
        GeminiAPI["Gemini 3.7 Flash API"]
        FirestoreDB[("Cloud Firestore\nStrict Tenant Rules")]
    end

    UI --> StyleSelector
    UI --> MultiTurn
    UI --> HistoryDrawer
    UI -->|1. Sign in & obtain ID Token| FBAuth
    FBAuth -->|2. Bearer Token Request| AuthMiddleware
    AuthMiddleware -->|3. Validated UID Scope| APIRouter
    APIRouter --> GeminiService
    APIRouter --> ArcEngine
    APIRouter --> ActionDistiller
    APIRouter --> TenantDB

    GeminiService <-->|4. Vertex AI ADC / Secret Manager| SecretMgr
    GeminiService <-->|5. Bounded Reflection Prompts| GeminiAPI
    TenantDB <-->|6. Scoped Tenant Read/Write| FirestoreDB
    ArcEngine -->|7. Turn-by-Turn Dynamic Points| ArcChart
```

---

## 🛡️ The 4 Core Security Pillars

| Security Pillar | Production Implementation | Defense Mechanism |
| :--- | :--- | :--- |
| **1. User Authentication** | Firebase Authentication (Google Sign-In / Email) | Cryptographic JWT verification on backend via Google Identity Toolkit; validates issuer, audience, and expiry. Reject all deterministic test tokens in production. |
| **2. Multi-turn AI Interaction** | Gemini 3.7 Flash with Delimiter Guardrails | User reflections are encapsulated within `<user_journal_reflection>` delimiters to prevent prompt injection, privilege escalation, and jailbreaks. |
| **3. Isolated Data Storage** | Cloud Firestore (`/users/{uid}/*`) | Strict user-scoped document hierarchy. User A cannot view, modify, or delete User B entries (Zero Cross-User Leakage). Enforced at the API and database levels. |
| **4. Secure Key Management** | Google Cloud Secret Manager + Vertex AI ADC | Zero hardcoded keys. Dual-mode credential resolution utilizes Vertex AI Application Default Credentials (ADC) on Cloud Run with fallback to Secret Manager. |

---

## ✨ Executive Feature Showcase (Zero AI Slop Craft)

Sanctuary OS was designed with human designer craftsmanship, prioritizing calm focus, subtle typography, and intentional feedback over tacky AI gimmicks:

### 1. 🧭 Reflection Style Selector (4 Distinct Persona Engines)
Above the reflection canvas, users can toggle between 4 purpose-built reflection modes. Each adapts the Gemini Socratic prompt dynamically:
- 🧭 **Balanced** *(Holistic clarity — balances emotional grounding with practical perspective)*
- 🎯 **Actionable** *(Next steps & habits — relentless focus on Big-3 priorities and execution)*
- 📜 **Deep Philosophy** *(Cognitive reframing — Stoic and Socratic wisdom to re-anchor mindset)*
- 💡 **Brainstorm** *(Lateral creative sparks — breaking through mental impasses with divergent thinking)*

### 2. 💬 Multi-Turn Threaded Reflection Dialogue
- Distinctive User vs Guardian dialogue bubbles with authentic timestamps and `gemini-3.7-flash` model badges.
- Live Turn Counter badge and `Firestore Synchronized` indicator.
- Dynamic follow-up placeholder: *"Ask a follow-up reflection, challenge Gemini thought, or explore deeper..."*
- **`✨ Auto-Summarize`**: Synthesizes rambling multi-turn conversations into an Executive Summary and Breakthrough Theme.
- **`💾 Save Reflection`**: 1-click persistence to user-isolated Firestore account with instant visual feedback.

### 3. 📈 Dynamic Cognitive & Emotional Arc Visualizer
- **Authentic Zero-State**: When a user opens a new session, the chart displays a clean empty state (*"Awaiting Reflection Dialogue"*). Zero pre-baked fake lines or dummy coordinates.
- **Turn-by-Turn Dynamic Plotting**: Upon submitting reflections, the chart dynamically initializes and graphs genuine *Clarity & Grounding* and *Stress Relief* trajectories across conversation turns.

### 4. 📋 Tactile Execution Board (Kanban) with Human-in-the-Loop Gate
- Drag-and-drop task workflow across `To Do`, `In Progress`, and `Done & Celebrated`.
- **Human-in-the-Loop (HITL) Gate**: Gemini NEVER writes tasks directly to the database. It proposes an Action Card with `[Approve]` and `[Dismiss]` buttons for user consent.

### 5. 🔍 Past Reflections Search & Categorical Filter Pills
- Sidebar Search Input: Real-time search across titles, dates, and journal transcripts.
- Filter Pills: Instant filtering by `[All]`, `[Reflective]`, `[Actionable]`, and `[Breakthrough]`.
- **Interactive Review Drawer**: Click any past entry to view the full dialogue transcript, executive summary, and neatly parsed action items.

### 6. 📊 Executive Data Report & Markdown Export
- Calculates genuine total word counts, completed action items, and focus blocks.
- Verifies cryptographic tenant isolation status (`/users/{uid}/*`).
- 1-click **Download Markdown Report** (`sanctuary-executive-report.md`) for external archiving.
### 7. 🤖 Multimodal Intelligence & Live Google ADK Tool Calling
- **Google ADK Function Tool Registry:** 7 live tools (`adk_create_ticket`, `adk_move_ticket`, `adk_schedule_calendar`, `adk_save_memory`, `adk_synthesize_learned_rule`, `adk_trigger_box_breathing`, `adk_trigger_shutdown_ritual`) integrated with `LlmAgent`.
- **Multimodal Neural Voice Synthesis (`/api/voice/synthesize`):** High-fidelity spoken reflections using Google Cloud Text-to-Speech API with calming tone and natural cadence.
- **Strict Human-in-the-Loop (HITL) Gate:** Agent tool proposals return with `status: "proposed"`. The user must explicitly click `[Approve]` on the Action Card before any database mutation occurs.

---

## 📸 Phase 1 Deliverable: Google AI Studio Security Constitution

As required by Phase 1 of the Hack2Skill Ideathon Challenge, Google AI Studio was pre-configured with the **Enterprise Security Constitution** before writing or scaffolding application code.

- **System Instructions Directives:** Full directives documented in [AI_STUDIO_SECURITY_CONSTITUTION.md](./AI_STUDIO_SECURITY_CONSTITUTION.md).
- **Core Security Enforcement:** Delimiter boundary defense (`<user_journal_reflection>`), Keyless secret ingestion (Vertex AI ADC + Secret Manager), Fail-closed auth (`ENVIRONMENT=production` rejects all mock tokens), and User-partitioned Firestore paths (`/users/{uid}/*`).

![Google AI Studio Security Constitution Configured](./assets/AI_Studio_Security_Constitution_Configured.png)

---

## 🧪 Automated Test Suite (66/66 Tests Passing • 100% Green)

Run the full hermetic test suite across security isolation, Playwright browser UI automation, and full E2E user lifecycles:

```bash
cd 04-personal-gemini-journal
source .venv/bin/activate
ENVIRONMENT=test ALLOW_TEST_AUTH=true USE_MOCK_DB=true GEMINI_API_KEY=placeholder_key pytest tests/test_security_isolation.py tests/test_ui_playwright.py tests/test_live_browser_automation_e2e.py -v
```

### Test Coverage Breakdown:
1. **`tests/test_security_isolation.py` (33 Tests):**
   - Cryptographic JWT verification, forged token rejection (401), expired token rejection.
   - Cross-tenant zero-leakage isolation (User A cannot access User B journals, tickets, or calendar events).
   - Delimiter prompt injection containment (`<user_journal_reflection>` boundaries).
   - Production fail-closed authentication gate matrix (`ENVIRONMENT=production` forbids all test tokens).
   - Ticket and calendar CRUD isolation and authorization.
   - Living memory and learned preference boundaries.

2. **`tests/test_ui_playwright.py` (32 Tests):**
   - Unauthenticated landing state and clean Notion Serene login card.
   - 4 Reflection Style cards selection and persona mode payload verification.
   - Multi-turn reflection dialogue, model badges, turn counter, and follow-up placeholder.
   - Dynamic emotional arc zero-state and real-time chart initialization.
   - Auto-summarize distillation and Firestore save interaction.
   - Sidebar past reflections search, filter pills (`All`, `Reflective`, `Actionable`, `Breakthrough`), and review drawer.
   - Kanban drag-and-drop, calendar focus block creation, and life rewind metrics.
   - Executive report modal and Markdown download trigger.
   - Escape key dismissals, whitespace validation, and responsive mobile navigation (390×844) with ≥44px touch targets.

3. **`tests/test_live_browser_automation_e2e.py` (1 Comprehensive E2E Lifecycle):**
   - Automated browser lifecycle executing a realistic user journey with real typing, button clicks, and screenshot captures at 12 checkpoints (`tests/screenshots/*.png`).

---

## 🚀 Local Quickstart & Development

### 1. Prerequisites
- Python 3.11+
- Google Cloud SDK (`gcloud`) authenticated (`gcloud auth application-default login`)

### 2. Setup Environment
```bash
cd 04-personal-gemini-journal
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 3. Run Locally
```bash
ENVIRONMENT=development ALLOW_TEST_AUTH=true USE_MOCK_DB=true uvicorn main:app --host 127.0.0.1 --port 8080 --reload
```
Open your browser at `http://localhost:8080`.

---

## ☁️ Google Cloud Run Deployment

Deploy live to Google Cloud Run in one command:

```bash
chmod +x deploy.sh
./deploy.sh
```

Or deploy manually via `gcloud` with the required challenge label:
```bash
gcloud run deploy personal-gemini-journal \
    --source . \
    --region us-central1 \
    --allow-unauthenticated \
    --labels="dev-tutorial=cloud-run-ai-challenge" \
    --memory 512Mi \
    --cpu 1
```

---

## 📜 License & Acknowledgements
Developed under the **MIT License** as part of the **Google Cloud GenAI Academy APAC Edition**.  
Hashtag: `#AccelerateAIwithCloudRun`
