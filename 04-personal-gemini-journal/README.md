# 🛡️ Sanctuary OS: Secure Personal Gemini Journal & Executive Sanctuary
### Production AI Journaling Platform with Zero-Trust Multi-Tenant Isolation on Google Cloud Run

[![Google Cloud Run](https://img.shields.io/badge/Google_Cloud-Cloud_Run-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/run)
[![Hackathon Label](https://img.shields.io/badge/Hackathon_Label-dev--tutorial%3Dcloud--run--ai--challenge-34A853?logo=googlecloud&logoColor=white)](./deploy.sh)
[![Firebase Auth](https://img.shields.io/badge/Firebase-Authentication-FFCA28?logo=firebase&logoColor=black)](https://firebase.google.com/docs/auth)
[![Cloud Firestore](https://img.shields.io/badge/Google_Cloud-Firestore-FFCA28?logo=firebase&logoColor=black)](https://firebase.google.com/docs/firestore)
[![Secret Manager](https://img.shields.io/badge/Google_Cloud-Secret_Manager-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/secret-manager)
[![Gemini 2.5 & 3.7 Flash](https://img.shields.io/badge/Gemini-2.5_%26_3.7_Flash-8A2BE2?logo=google&logoColor=white)](https://ai.google.dev)
[![Test Suite](https://img.shields.io/badge/Tests-67%2F67_Passing_(100%25)-34A853?logo=pytest&logoColor=white)](./tests)
[![Design](https://img.shields.io/badge/UI_Craft-Zero_AI_Slop-indigo)](./static)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Built for the **Hack2Skill APAC GenAI Academy (Cohort 3: Accelerate AI with Cloud Run)** Ideathon Challenge.  
> Directly solves the industry-wide failure mode: *"Most AI-generated apps look great in a demo and fall apart in production — hardcoded keys, no auth boundaries, shared databases with zero isolation, and tacky AI slop interfaces."*

---

## 🎯 Problem Statement & Executive Opportunity

Modern leaders, founders, and engineers operate under relentless cognitive overload:
1. **Cognitive Fragmentation & Burnout:** Executives juggle dozens of conflicting priorities across architecture, sprint milestones, and personal life. Existing journaling tools act as passive text dumps, failing to distill rambling reflections into actionable execution.
2. **The "AI Slop" Trap:** Consumer wellness apps rely on superficial "AI chat" gimmicks—fake meditation bubbles, canned affirmations, and synthetic sentiment curves that exist before a user even writes.
3. **The Production Security Deficit:** Typical AI hackathon prototypes collapse in production—exposing hardcoded API keys, leaking multi-tenant data in unpartitioned databases, accepting unvalidated mock tokens, or giving LLMs unconstrained autonomous write privileges.

**Sanctuary OS** redefines executive journaling as an **Enterprise-Grade Cognitive Sanctuary**:
- **Zero-Trust Multi-Tenancy:** 100% data isolation on Cloud Firestore (`/users/{uid}/*`) backed by Google AI Studio's pre-configured Security Constitution.
- **Human-in-the-Loop Sovereignty:** Gemini proposes structured action items (Kanban cards, calendar blocks), but NEVER mutates persistent databases without explicit human approval.
- **Serene Human Craftsmanship:** Replaces toxic gamification with authentic computed metrics (zero fake streaks, real word counts, real turn-by-turn emotional trajectories).

---

## 🏆 Hack2Skill APAC GenAI Academy Ideathon Evaluation Criteria Alignment

Sanctuary OS was architected specifically to maximize scoring across the four core pillars of the **Hack2Skill APAC GenAI Academy (Accelerate AI with Cloud Run)** evaluation criteria:

| Evaluation Pillar | Hackathon Judging Requirement | Sanctuary OS Implementation | Concrete Evidence |
| :--- | :--- | :--- | :--- |
| **1. Innovation** | Novel AI capabilities, creative GenAI patterns, multimodal interaction | • **4-Style Persona Engine** (`balanced`, `actionable`, `philosophy`, `brainstorm`)<br>• **7 Google ADK Function Tools** (`adk_create_ticket`, `adk_move_ticket`, `adk_schedule_calendar`, `adk_save_memory`, etc.)<br>• **Dynamic Emotional Arc Visualizer** with Authentic Zero-State<br>• **Multimodal Neural Voice Synthesis** (`/api/voice/synthesize`)<br>• **Burmese Multilingual Reflection** with cultural nuance & dialect grounding<br>• **Continuous Self-Evolution** via 3-Tier Living Memory | [gemini_service.py](gemini_service.py#L93-L148)<br>[main.py](main.py#L650-L685)<br>[simulate_real_user.py](tests/simulate_real_user.py)<br>22 Screenshots in `real_user_verification/` |
| **2. Technical Architecture** | Scalable GCP serverless design, clean code, ADC integration | • **Google Cloud Run** containerized FastAPI backend (scale-to-zero, 512Mi/1CPU)<br>• **Cloud Firestore** partitioned at `/users/{uid}/*` (zero cross-user leakage)<br>• **Keyless Secret Management** via Vertex AI ADC & Secret Manager<br>• **Non-root Container** execution (`USER appuser`, UID 1000)<br>• **Offline & 401 Draft Resilience** in vanilla JS SPA | [Dockerfile](Dockerfile#L20-L21)<br>[database.py](database.py#L45-L210)<br>[auth.py](auth.py#L20-L65)<br>[static/app.js](static/app.js#L140-L180)<br>[deploy.sh](deploy.sh#L34-L45) |
| **3. Real-World Impact** | Solves practical problems, authentic user value, high UX craft | • **4-Step Focused Sanctuary Loop** (`Reflect ➔ Approve ➔ Act ➔ Rewind`)<br>• **Human-in-the-Loop Action Confirmation Gate** (0 unconfirmed DB writes)<br>• **Grounded Life Rewind** (100% genuine computed stats; zero fake metrics)<br>• **Data Portability** (1-click Markdown export `sanctuary-executive-report.md`)<br>• **Mobile-First Accessibility** (390×844 responsive shell, ≥44px touch targets) | [ARCHITECTURE.md](ARCHITECTURE.md#L53-L77)<br>[DESIGN_AND_DECISION_LOG.md](DESIGN_AND_DECISION_LOG.md#L65-L92)<br>[static/style.css](static/style.css#L180-L240)<br>12 E2E Checkpoint Screenshots |
| **4. Enterprise Security** | Pre-scaffolding security prompt, fail-closed auth, prompt defense | • **Google AI Studio Security Constitution** (Phase 1 deliverable)<br>• **Fail-Closed Auth Matrix** (`ENVIRONMENT=production` forbids all test tokens with HTTP 401)<br>• **Delimiter Prompt Injection Defense** (`<user_journal_reflection>` boundaries)<br>• **Client-Side Secret Redactor** (`redactSecrets()`) scrubbing keys before send | [AI_STUDIO_SECURITY_CONSTITUTION.md](AI_STUDIO_SECURITY_CONSTITUTION.md)<br>[SECURITY_REVIEW.md](SECURITY_REVIEW.md)<br>[auth.py](auth.py#L40-L60)<br>33/33 Pytest Security Tests Pass |

---

## 🏷️ Mandatory Automated Verification Label
Per Hack2Skill & Google Cloud guidelines, this Cloud Run service is deployed with the required label for automated evaluation:
```yaml
labels:
  dev-tutorial: cloud-run-ai-challenge
```

---

## 🏛️ System Architecture & Workflow Models

### 1. Cloud Run & Google Cloud Platform Infrastructure
```mermaid
flowchart TD
    subgraph ClientLayer["💻 Web Client (Vanilla SPA + Tailwind + Chart.js + Inter Typography)"]
        UI["Reflective Journaling Studio\n(Notion Serene Dark Aesthetic)"]
        StyleSelector["Reflection Style Engine\n(Balanced | Actionable | Philosophy | Brainstorm)"]
        MultiTurn["Multi-Turn Dialogue Stream\n(Gemini 2.5 / 3.7 Flash Badges + Timestamps)"]
        HistoryDrawer["History Search & Filter\n([All] [Reflective] [Actionable] [Breakthrough])"]
        ArcChart["Dynamic Cognitive & Emotional Arc Visualizer\n(Zero Fake Points • Live Turn Plotting)"]
        FBAuth["Firebase Auth (Google Sign-In / Token)"]
    end

    subgraph CloudRunService["☁️ Google Cloud Run Serverless Backend (FastAPI + Python 3.11)"]
        AuthMiddleware["Token Validation Middleware\n(Cryptographic JWT / Audience & Expiry Check)"]
        APIRouter["API Router (/api/agent/live-turn, /api/journal, /api/tickets, /api/calendar)"]
        GeminiService["Gemini Service Engine\n(Persona System Directives + Delimiter Defense)"]
        ArcEngine["Cognitive & Emotional Arc Sentiment Engine"]
        ActionDistiller["Executive Action Items Distiller (Human-in-the-Loop Gate)"]
        TenantDB["Tenant-Isolated Firestore Service\n(/users/{uid}/* Hierarchy)"]
    end

    subgraph GCP_Security["🔒 Google Cloud Security & Data Plane"]
        SecretMgr["Secret Manager / Vertex AI ADC\n(Zero Hardcoded Keys)"]
        GeminiAPI["Gemini 2.5 / 3.7 Flash API"]
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

### 2. The 4-Step Focused Sanctuary Loop
Rather than overwhelming the user with fragmented tools, Sanctuary OS guides the user through a serene, cyclic 4-step workflow:
```mermaid
graph LR
    A["1. REFLECT (Studio)<br/>• Unfiltered voice / text dump<br/>• 4 Socratic persona styles<br/>• Multi-turn conversational flow"] --> B["2. APPROVE ACTION<br/>• Gemini proposes structured cards<br/>• Human-in-the-Loop approval<br/>• 0 unconfirmed DB mutations"]
    B --> C["3. ACT (Kanban & Cal)<br/>• Drag-and-drop task execution<br/>• Mindful calendar focus blocks<br/>• Living Memory sync"]
    C --> D["4. REWIND (Growth)<br/>• Grounded genuine metrics<br/>• Real words & completed tasks<br/>• Evening shutdown ritual"]
    D --> A
```

### 3. Human-in-the-Loop (HITL) Action Confirmation State Machine
To uphold user sovereignty and prevent unintended automated mutations, Sanctuary OS strictly separates conversational intelligence from persistent database execution:
```mermaid
stateDiagram-v2
    [*] --> Listening: User speaks or types reflection
    Listening --> Analyzing: POST /api/agent/live-turn
    Analyzing --> Proposing: Gemini detects action intent

    state Proposing {
        UI_Action: Immediate UI Execution (e.g. Box Breathing)
        Persistent_Action: Queue in pendingProposals (0 DB Writes)
    }

    Proposing --> RenderProposalCard: Display Active Proposal in UI

    RenderProposalCard --> UserChoice
    state UserChoice <<choice>>

    UserChoice --> Dismissed: User clicks [Dismiss]
    UserChoice --> Approved: User clicks [Approve]

    Dismissed --> QueueDrained: Discard proposal with 0 API writes

    Approved --> Confirming: POST /api/agent/actions/confirm {action, confirmed: true}
    Confirming --> Executed: Server executes verified mutation
    Executed --> Feedback: Render success feedback & refresh affected view
    Feedback --> QueueDrained: Advance proposal queue

    QueueDrained --> [*]
```

---

## 🛡️ The 4 Core Security Pillars

| Security Pillar | Production Implementation | Defense Mechanism |
| :--- | :--- | :--- |
| **1. User Authentication** | Firebase Authentication (Google Sign-In / Email) | Cryptographic JWT verification on backend via Google Identity Toolkit; validates issuer, audience, and expiry. Reject all deterministic test tokens in production. |
| **2. Multi-turn AI Interaction** | Gemini 2.5 / 3.7 Flash with Delimiter Guardrails | User reflections are encapsulated within `<user_journal_reflection>` delimiters to prevent prompt injection, privilege escalation, and jailbreaks. |
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
- Distinctive User vs Guardian dialogue bubbles with authentic timestamps and `gemini-2.5-flash` / `gemini-3.7-flash` model badges.
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

## 🧪 Complete Test Suite & Verification Guide

Sanctuary OS enforces a two-tier verification methodology: a 67-test automated pytest suite for continuous integration and an automated, human-fidelity browser simulation via Playwright.

### 1. Automated Hermetic Test Suite (67/67 Tests Passing • 100% Green)

Run the full hermetic test suite across security isolation, Playwright browser UI automation, and full E2E user lifecycles:

```bash
cd /Users/mac/Projects/code/apac_genai_academy/04-personal-gemini-journal
source .venv/bin/activate
ENVIRONMENT=test ALLOW_TEST_AUTH=true USE_MOCK_DB=true GEMINI_API_KEY=placeholder_key pytest tests/test_security_isolation.py tests/test_ui_playwright.py tests/test_live_browser_automation_e2e.py -v
```

#### Test Coverage Breakdown:
1. **`tests/test_security_isolation.py` (34 Tests):**
   - Cryptographic JWT verification, forged token rejection (401), expired token rejection.
   - Cross-tenant zero-leakage isolation (User A cannot access User B journals, tickets, or calendar events).
   - Delimiter prompt injection containment (`<user_journal_reflection>` boundaries).
   - Production fail-closed authentication gate matrix (`ENVIRONMENT=production` forbids all deterministic test tokens).
   - Deployment configuration & project guard (`deploy.sh` strict project halt & Secret Manager binding).
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
   - Automated browser lifecycle executing a realistic user journey with real typing, button clicks, and screenshot captures across 12 checkpoints (`tests/screenshots/*.png`).

---

### 2. Realistic Human User Simulation (`tests/simulate_real_user.py`)

In addition to the 67 automated pytest units, Sanctuary OS provides an automated human-fidelity browser simulation that drives a real Chromium browser through an authentic executive session as user "Victor Kyaw":

```bash
# Terminal 1: Launch Local Server (if not already running)
cd /Users/mac/Projects/code/apac_genai_academy/04-personal-gemini-journal
ENVIRONMENT=development ALLOW_TEST_AUTH=true USE_MOCK_DB=true uvicorn main:app --host 127.0.0.1 --port 8080

# Terminal 2: Run Real User Simulation
cd /Users/mac/Projects/code/apac_genai_academy/04-personal-gemini-journal
source .venv/bin/activate
python3 tests/simulate_real_user.py
```

#### Simulation Verification Lifecycle:
1. **Pristine State Prep:** Cleans up any prior test tickets via authenticated API.
2. **Authenticated Access:** Logs in as "Victor Kyaw", validates executive header and subtitle.
3. **Dropdown Elevation & Collision:** Confirms Export menu dropdown sits above the callout card with zero bounding-box collision.
4. **Persona Mode Switching:** Tests `Actionable` mode activation and returns to `Auto-Detect`.
5. **Multi-Turn Burmese Dialogue:**
   - **Turn 1 (Greeting):** Sends `"ဟိုင်း မင်္ဂလာပါ Gemini ရေ"`, validates contextual Burmese response.
   - **Turn 2 (Task Proposal):** Discusses Sanctuary OS architecture; Gemini proposes structured Kanban ticket via HITL Action Card; simulation clicks `[Approve]`.
   - **Turn 3 (Sprint Scheduling):** Requests afternoon deep work sprint focus.
   - **Turn 4 (Cognitive Balance):** Deep reflection on cognitive stamina; asserts dynamic, non-canned Burmese advice.
6. **Auto-Summarize & Persistence:** Distills session into Executive Summary and saves to Firestore.
7. **Execution Studio (Kanban):** Creates ticket and transitions it to `Done & Celebrated`.
8. **Mindful Calendar:** Loads 3 focus blocks and schedules hackathon architecture block.
9. **Grounded Life Rewind:** Verifies genuine non-zero reflection, word, and task completion metrics.
10. **Evening Shutdown Ritual:** Confirms Tibetan singing bowl sound and Burmese gratitude affirmation.
11. **Past Reflections Drawer:** Inspects saved session in slide-out wisdom drawer.
12. **Automated Teardown:** Purges test calendar events and tickets, proving 0 remaining kanban cards.

#### Verified Visual Proof Artifacts (`tests/screenshots/real_user_verification/`):

| Screenshot Artifact | Lifecycle Stage & Verified Capability |
| :--- | :--- |
| `01_export_dropdown_clean_elevation.png` | Export menu clean elevation above callout card with zero bounding box collision |
| `02_scenario_mode_selection.png` | Reflection style selector toggling dynamically to Actionable Focus mode |
| `03_burmese_turn1_greeting.png` | Turn 1 authentic Burmese greeting and Gemini Guardian response |
| `04_burmese_turn2_task_proposal.png` | Turn 2 project priorities discussion and HITL Action Proposal Card |
| `05_burmese_turn3_schedule_focus.png` | Turn 3 deep work sprint scheduling and cognitive direction |
| `06_burmese_turn4_deep_reflection.png` | Turn 4 cognitive stamina reflection and non-canned Socratic guidance |
| `07_saved_session_sidebar.png` | Auto-summarize summary card and Firestore synchronization confirmation |
| `08_kanban_board_done.png` | Tactile Kanban task progression to `Done & Celebrated` column |
| `09_calendar_with_activities.png` | Mindful Calendar with scheduled focus blocks and hackathon sync |
| `10_life_rewind_view.png` | Grounded Life Rewind metrics reflecting genuine user activity |
| `11_evening_shutdown_modal.png` | Evening Shutdown ritual modal with Zen Burmese gratitude affirmation |
| `12_past_reflection_wisdom_drawer.png` | Slide-out review drawer with full multi-turn transcript and action items |
| `13_clean_state_verified.png` | Post-simulation automated teardown verifying 0 lingering test artifacts |

---

## 🚀 Local Quickstart & Development

### 1. Prerequisites
- Python 3.11+
- Google Cloud SDK (`gcloud`) authenticated (`gcloud auth application-default login`)
- Node.js & npm (optional, for Playwright Chromium driver)

### 2. Setup Environment
```bash
cd 04-personal-gemini-journal
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 3. Environment Configuration Guide

| Variable | Development / Test Value | Production Cloud Run Value | Purpose |
| :--- | :--- | :--- | :--- |
| `ENVIRONMENT` | `development` or `test` | `production` | Enables fail-closed auth; disables all test tokens in production |
| `ALLOW_TEST_AUTH` | `true` | `false` | Enables deterministic developer tokens for testing and automation |
| `USE_MOCK_DB` | `true` | `false` | In-memory mock Firestore for hermetic offline testing |
| `GEMINI_MODEL` | `gemini-2.5-flash` / `gemini-3.7-flash` | `gemini-2.5-flash` / `gemini-3.7-flash` | Selected Gemini foundation model |
| `GCP_PROJECT_ID` | Local project name | Google Cloud Project ID | Bound to Vertex AI ADC and Secret Manager |

### 4. Run Locally
```bash
ENVIRONMENT=development ALLOW_TEST_AUTH=true USE_MOCK_DB=true uvicorn main:app --host 127.0.0.1 --port 8080 --reload
```
Open your browser at `http://localhost:8080`.

---

## ☁️ Google Cloud Run Deployment

### Automated One-Click Deployment
```bash
chmod +x deploy.sh
./deploy.sh
```

### Manual gcloud Deployment (with Mandatory Challenge Label)
```bash
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
SERVICE_NAME="personal-gemini-journal"

gcloud run deploy "${SERVICE_NAME}" \
    --source . \
    --region="${REGION}" \
    --project="${PROJECT_ID}" \
    --allow-unauthenticated \
    --labels="dev-tutorial=cloud-run-ai-challenge" \
    --set-env-vars="GCP_PROJECT_ID=${PROJECT_ID},ENVIRONMENT=production,GEMINI_MODEL=gemini-2.5-flash" \
    --memory="512Mi" \
    --cpu="1" \
    --min-instances="0" \
    --max-instances="5"
```

### Automated Evaluation Label Verification
Judges and automated evaluation scanners can independently verify the required label on the deployed service:
```bash
gcloud run services describe personal-gemini-journal \
    --region us-central1 \
    --format 'value(metadata.labels.dev-tutorial)'
# Expected Output: cloud-run-ai-challenge
```

---

## 📜 License & Acknowledgements
Developed under the **MIT License** as part of the **Google Cloud GenAI Academy APAC Edition**.  
Hashtag: `#AccelerateAIwithCloudRun`
