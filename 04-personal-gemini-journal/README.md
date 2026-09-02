# 🛡️ Pattern 4: Secure Personal Gemini Journal
### Production AI Journaling Platform with Zero-Trust Multi-Tenant Isolation on Google Cloud Run

[![Google Cloud Run](https://img.shields.io/badge/Google_Cloud-Cloud_Run-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/run)
[![Firebase Auth](https://img.shields.io/badge/Firebase-Authentication-FFCA28?logo=firebase&logoColor=black)](https://firebase.google.com/docs/auth)
[![Cloud Firestore](https://img.shields.io/badge/Google_Cloud-Firestore-FFCA28?logo=firebase&logoColor=black)](https://firebase.google.com/docs/firestore)
[![Secret Manager](https://img.shields.io/badge/Google_Cloud-Secret_Manager-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/secret-manager)
[![Gemini 2.5 Flash](https://img.shields.io/badge/Gemini-2.5_Flash-8A2BE2?logo=google&logoColor=white)](https://ai.google.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Built for the **Hack2Skill APAC GenAI Academy (Cohort 3: Accelerate AI with Cloud Run)** Ideathon Challenge.  
> Directly solves the industry-wide failure mode: *"Most AI-generated apps look great in a demo and fall apart in production — hardcoded keys, no auth boundaries, shared databases with zero isolation."*

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph ClientLayer["💻 Web Client (Vanilla SPA + Tailwind + Chart.js)"]
        UI["Reflective Journaling Studio"]
        FBAuth["Firebase Auth (Google Sign-In / Token)"]
        ArcChart["Emotional & Cognitive Arc Visualizer"]
    end

    subgraph CloudRunService["☁️ Google Cloud Run Serverless Backend (FastAPI)"]
        AuthMiddleware["Token Validation Middleware\n(Cryptographic JWT / Audience Check)"]
        APIRouter["API Router (/api/chat, /api/journal, /api/actions)"]
        GeminiService["Gemini Service Engine\n(Delimiter Defense + Fail-Closed)"]
        ArcEngine["Cognitive & Emotional Arc Analyzer"]
        ActionDistiller["Executive Action Items Distiller"]
        TenantDB["Tenant-Isolated Firestore Layer\n(/users/{uid}/journals/{doc_id})"]
    end

    subgraph GCP_Security["🔒 Google Cloud Security & Data Plane"]
        SecretMgr["Secret Manager\n(GEMINI_API_KEY via ADC)"]
        GeminiAPI["Gemini 2.5 Flash API"]
        FirestoreDB[("Cloud Firestore\nStrict Tenant Rules")]
    end

    UI -->|1. Sign in & obtain ID Token| FBAuth
    FBAuth -->|2. Bearer Token Request| AuthMiddleware
    AuthMiddleware -->|3. Validated UID Scope| APIRouter
    APIRouter --> GeminiService
    APIRouter --> ArcEngine
    APIRouter --> ActionDistiller
    APIRouter --> TenantDB

    GeminiService <-->|4. ADC / Secret Manager| SecretMgr
    GeminiService <-->|5. Bounded Reflection Prompts| GeminiAPI
    TenantDB <-->|6. Scoped Tenant Read/Write| FirestoreDB
    ArcEngine -->|7. Turn-by-Turn Metrics| ArcChart
```

---

## 🛡️ The 4 Core Security Pillars

| Security Pillar | Production Implementation | Defense Mechanism |
| :--- | :--- | :--- |
| **1. User Authentication** | Firebase Authentication (Google Sign-In / Email) | Cryptographic JWT verification on backend via Google Identity Toolkit; validates issuer, audience, and expiry. |
| **2. Multi-turn AI Interaction** | Gemini 2.5 Flash with Delimiter Guardrails | User reflections are encapsulated within `<user_journal_reflection>` delimiters to prevent prompt injection and instruction overrides. |
| **3. Isolated Data Storage** | Cloud Firestore (`/users/{uid}/journals/{doc_id}`) | Strict user-scoped document hierarchy. User A cannot view, modify, or delete User B's entries (Zero Cross-User Leakage). Enforced via backend logic and `firestore.rules`. |
| **4. Secure Key Management** | Google Cloud Secret Manager + ADC | Zero hardcoded keys. API keys are loaded dynamically at runtime via Application Default Credentials (ADC). |

---

## ✨ Original Feature Enhancements (Phase 3 Innovation)

Beyond the baseline requirements, this application introduces three unique, high-impact features designed to foster emotional resilience and cognitive clarity:

### 1. 📈 Emotional & Cognitive Arc Visualizer
- Automatically extracts turn-by-turn **Sentiment Score** (-1.0 to +1.0), **Energy Level** (0.0 to 1.0), and **Cognitive Clarity** (0.0 to 1.0).
- Renders an interactive, real-time curve with Chart.js, revealing the user's emotional shift from initial tension to grounded resolution.

### 2. 💡 Semantic Memory & Past Wisdom Recall
- While journaling about a current challenge (e.g., career anxiety, decision fatigue), Gemini cross-references past journal entries and surfaces relevant breakthroughs:
  > *"On August 24, when navigating a similar roadblock, you realized that taking an intentional pause provided the breakthrough."*

### 3. ⚡ Executive Action Items Distiller
- One-click distillation of emotional stream-of-consciousness reflections into structured, prioritized tasks (`Urgent`, `High`, `Medium`) with categories (`Work`, `Wellness`, `Mindset`).
- Includes a **1-Click "Copy Markdown"** button for instant export into Obsidian, Notion, or task managers.

---

## 📸 Deliverable 1: Google AI Studio Security Constitution

As required by the Ideathon Challenge, Google AI Studio was pre-configured with the **Enterprise Security Constitution** before code generation.

See the full directives in [AI_STUDIO_SECURITY_CONSTITUTION.md](./AI_STUDIO_SECURITY_CONSTITUTION.md).

![AI Studio Security Constitution Configured](./assets/AI_Studio_Security_Constitution_Configured.png)

---

## 🧪 Security & Multi-Tenant Automated Test Suite

Run the automated pytest suite verifying cross-tenant isolation and security:

```bash
cd 04-personal-gemini-journal
python3 -m pytest tests/test_security_isolation.py -v
```

### Verified Test Cases:
- `test_health_endpoint`: Verifies service health probe.
- `test_unauthenticated_request_rejected`: Confirms unauthenticated requests fail with HTTP 401.
- `test_invalid_token_rejected`: Confirms forged tokens fail with HTTP 401.
- `test_user_profile_identification`: Verifies identity claims extraction.
- `test_cross_tenant_isolation_zero_leakage`: **Critical Gate** — Verifies User A's private entry cannot be viewed, listed, or deleted by User B (returns HTTP 404/403).
- `test_prompt_injection_defense_containment`: Confirms delimiter override attacks are safely contained.
- `test_feature_emotional_arc_endpoint`: Confirms dynamic sentiment & clarity scoring.
- `test_feature_action_items_distillation_endpoint`: Confirms structured task extraction.

---

## 🚀 Local Quickstart & Development

### 1. Prerequisites
- Python 3.11+
- Google Cloud SDK (`gcloud`) authenticated

### 2. Setup Environment
```bash
cd 04-personal-gemini-journal
pip install -r requirements.txt
```

### 3. Run Locally
```bash
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```
Open your browser at `http://localhost:8080` to access the journal studio.

---

## ☁️ Google Cloud Run Deployment

Deploy live to Google Cloud Run in one command:

```bash
chmod +x deploy.sh
./deploy.sh
```

Or deploy manually via `gcloud`:
```bash
gcloud run deploy personal-gemini-journal \
    --source . \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1
```

---

## 📜 License & Acknowledgements
Developed under the **MIT License** as part of the **Google Cloud GenAI Academy APAC Edition**.  
Hashtag: `#AccelerateAIwithCloudRun`
