# ⚙️ Pattern 3: Autonomous Operations Agent with Cloud Run Sandboxes

> **Core Focus:** Cloud Run Micro-Sandboxes (`--sandbox-launcher`), Dynamic Python Code Execution, Human-in-the-Loop (HITL) Governance, and Google Sheets API v4 Integration.

---

## 🏗️ Architecture

```mermaid
flowchart TD
    User([Operations Manager]) <-->|WebSocket Real-time UI| CloudRun[Cloud Run Service\ncoffee-mgr-agent]
    subgraph Cloud Run Environment
        FastAPI[FastAPI WebSocket Router] <--> ADK[Google ADK Runner]
        ADK <--> Gemini[Gemini 2.5 Flash / Vertex AI]
        ADK <--> SandboxTool[execute_sandbox_command]
        ADK <--> SheetsTool[Google Sheets API Tools]
        subgraph Isolated Micro-Sandbox
            SandboxTool <-->|/usr/local/gcp/bin/sandbox| PyEngine[Isolated Python Analytics Runtime]
        end
    end
    SheetsTool <-->|OAuth2 ADC / Read & Write| GSheets[(Google Sheets\nPOS Data & TODO Lists)]
```

## 🚀 Key Capabilities
1. **Cloud Run Native Micro-Sandboxing:** Dynamic execution of LLM-generated code in a pre-GA isolated sandbox runtime (`/usr/local/gcp/bin/sandbox`).
2. **Human-in-the-Loop Governance:** Strict behavioral directives preventing external state mutation without explicit user confirmation.
3. **Real-time Bidirectional UI:** WebSockets communication layer with client-side markdown and tabular data rendering.

## 💻 Deployment Command
```bash
gcloud beta run deploy coffee-mgr-agent \
    --source=. \
    --region=us-central1 \
    --sandbox-launcher \
    --max-instances=1 \
    --session-affinity \
    --allow-unauthenticated \
    --no-cpu-throttling \
    --set-env-vars GOOGLE_GENAI_USE_VERTEXAI=1,GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=global,SPREADSHEET_ID=$SPREADSHEET_ID \
    --service-account $SERVICE_ACCOUNT_ADDRESS
```
