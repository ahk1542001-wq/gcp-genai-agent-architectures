import os
import asyncio
import subprocess
from pathlib import Path
from typing import List
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from google.adk.agents import LlmAgent as Agent
from google.adk.tools import FunctionTool
from google.adk.apps import App
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Native Cloud Run Sandbox Execution Layer
SANDBOX_CLI = '/usr/local/gcp/bin/sandbox'
IS_LOCAL_MODE = not Path(SANDBOX_CLI).exists()

active_connections: list[WebSocket] = []
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")

def run_sandbox_process(args: list[str]):
    cmd = args[2:] if IS_LOCAL_MODE and args[:2] == ['do', '--'] else ([SANDBOX_CLI] + args if not IS_LOCAL_MODE else args)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=10)

def execute_sandbox_command(command: str) -> str:
    """Executes arbitrary dynamic Python/shell commands inside isolated Cloud Run sandbox."""
    mode = "LOCAL" if IS_LOCAL_MODE else "CLOUD RUN SANDBOX"
    print(f"[ADK Sandbox Tool] Running command in {mode}...")
    try:
        res = run_sandbox_process(['do', '--', '/bin/sh', '-c', command])
        if res.returncode != 0:
            return f"Execution Failed (Exit {res.returncode}):\n{res.stderr}\n{res.stdout}"
        return res.stdout
    except Exception as err:
        return f"Internal Sandbox Error: {str(err)}"

def get_sheets_service():
    """Initializes Google Sheets client with Application Default Credentials."""
    from google.auth import default
    from googleapiclient.discovery import build
    credentials, _ = default(scopes=[
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/cloud-platform'
    ])
    return build('sheets', 'v4', credentials=credentials)

def read_spreadsheet_values(spreadsheet_id: str, range_name: str) -> str:
    """Reads a range of cells from Google Sheets."""
    try:
        service = get_sheets_service()
        result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        rows = result.get('values', [])
        return str(rows) if rows else "No data found."
    except Exception as e:
        return f"Read Error: {str(e)}"

def update_spreadsheet_values(spreadsheet_id: str, range_name: str, values: List[List[str]]) -> str:
    """Appends/Updates values in Google Sheets."""
    try:
        service = get_sheets_service()
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption="USER_ENTERED", body={'values': values}).execute()
        return f"Successfully updated {result.get('updatedCells')} cells in {range_name}."
    except Exception as e:
        return f"Write Error: {str(e)}"

def create_spreadsheet_tab(spreadsheet_id: str, tab_name: str) -> str:
    """Creates a new worksheet tab if it does not already exist."""
    try:
        service = get_sheets_service()
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        for sheet in spreadsheet.get('sheets', []):
            if sheet.get('properties', {}).get('title') == tab_name:
                return f"Sheet tab '{tab_name}' already exists."
        body = {'requests': [{'addSheet': {'properties': {'title': tab_name}}}]}
        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
        return f"Successfully created new sheet tab '{tab_name}'."
    except Exception as e:
        return f"Error creating sheet tab: {str(e)}"

# ==========================================
# ADK AGENT SETUP & HUMAN-IN-THE-LOOP POLICY
# ==========================================

instruction = (
    f'You are an expert AI Business Operations Analyst.\n'
    f'Spreadsheet ID: "{SPREADSHEET_ID}".\n'
    '1. Analysis Protocol:\n'
    f'   - Read POS historical records from "POS-2025" tab via read_spreadsheet_values.\n'
    '   - Ingest schedule from user prompt and run dynamic Python code inside the sandbox to correlate beverage spikes and wait-time bottlenecks.\n'
    '2. Diagnostics Playbook:\n'
    '   - If complex items surge and Cashiers == 2 with Wait_Time > 10 min: Recommend adding a Support Barista role.\n'
    '3. Human-in-the-Loop Governance:\n'
    '   - Present findings and suggested TODO items to the manager.\n'
    '   - Explicitly ask: "Would you like me to add these tasks to your \'TODO-2026\' TODO list?"\n'
    '   - STRICT RULE: Do NOT execute update_spreadsheet_values or create_spreadsheet_tab until explicit user approval is received.\n'
    '4. Post-Approval Execution:\n'
    f'   - Upon user "Yes", verify/create "TODO-2026" tab and append tasks under Task, Category, Ceremony, Date_Added.'
)

root_agent = Agent(
    name='secure_operations_agent',
    model=os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash'),
    instruction=instruction,
    description='Operations AI Assistant utilizing Cloud Run Sandboxes and Google Sheets API.',
    tools=[
        FunctionTool(func=execute_sandbox_command),
        FunctionTool(func=read_spreadsheet_values),
        FunctionTool(func=update_spreadsheet_values),
        FunctionTool(func=create_spreadsheet_tab)
    ]
)

adk_app = App(name="sandboxed_app", root_agent=root_agent)
runner = Runner(app=adk_app, session_service=InMemorySessionService(), auto_create_session=True)
app = FastAPI(title="Secure Sandboxed Operations Agent")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    await websocket.send_text("🔌 System: Connected. Agent is ready...")
    try:
        while True:
            owner_reply = await websocket.receive_text()
            await websocket.send_text("_Agent is executing tools in sandbox and reasoning..._")
            new_message = types.Content(parts=[types.Part(text=owner_reply)])
            events = await asyncio.to_thread(
                runner.run,
                user_id="manager",
                session_id="session_default",
                new_message=new_message
            )
            final_response = "".join(
                part.text
                for event in events
                if event.content and event.content.parts
                for part in event.content.parts
                if part.text
            ) or "Updates completed."
            await websocket.send_text(final_response.strip())
    except WebSocketDisconnect:
        active_connections.remove(websocket)

@app.get("/", response_class=HTMLResponse)
async def get_chat_ui():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Operations Monitor</title>
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <style>
            body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; display: flex; height: 100vh; }
            #sidebar { width: 260px; background: #2D3748; color: #E2E8F0; padding: 24px; box-sizing: border-box; }
            #main { flex: 1; display: flex; flex-direction: column; background: #F7FAFC; }
            #chat-history { flex: 1; padding: 24px; overflow-y: auto; }
            #input-area { padding: 16px 24px; background: #FFF; border-top: 1px solid #E2E8F0; display: flex; gap: 12px; }
            input { flex: 1; padding: 12px 16px; border: 1px solid #CBD5E0; border-radius: 8px; font-size: 15px; }
            button { padding: 12px 24px; background: #3182CE; color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
            .message { margin-bottom: 16px; padding: 16px; border-radius: 8px; max-width: 80%; line-height: 1.6; }
            .user-msg { background: #EBF8FF; color: #2B6CB0; margin-left: auto; }
            .agent-msg { background: #FFF; color: #2D3748; border: 1px solid #E2E8F0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
            table { border-collapse: collapse; width: 100%; margin: 12px 0; }
            th, td { border: 1px solid #E2E8F0; padding: 8px 12px; text-align: left; }
            th { background: #EDF2F7; }
        </style>
    </head>
    <body>
        <div id="sidebar">
            <h2>⚙️ Ops Assistant</h2>
            <p>Cloud Run Sandboxes & Google Sheets Integration</p>
        </div>
        <div id="main">
            <div id="chat-history"></div>
            <div id="input-area">
                <input type="text" id="msg" placeholder="Type instructions..." onkeypress="if(event.key==='Enter') send()">
                <button onclick="send()">Send</button>
            </div>
        </div>
        <script>
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            const history = document.getElementById('chat-history');
            ws.onmessage = (e) => {
                history.innerHTML += `<div class="message agent-msg">${marked.parse(e.data)}</div>`;
                history.scrollTop = history.scrollHeight;
            };
            function send() {
                const el = document.getElementById('msg');
                if(!el.value) return;
                history.innerHTML += `<div class="message user-msg">${marked.parse(el.value)}</div>`;
                ws.send(el.value);
                el.value = '';
                history.scrollTop = history.scrollHeight;
            }
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
