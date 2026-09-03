"""
FastAPI Application Entry Point for Personal Gemini Life Guardian & Executive Coach
Production Serverless Service deployed on Google Cloud Run.
Enforces Zero-Trust Architecture, strict tenant-isolated Firestore endpoints,
Drag-and-Drop Kanban Ticketing, Interactive Calendar, Obsidian Export,
and Autonomous Live Voice Tool Calling.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from auth import get_current_user, AuthenticatedUser, enforce_user_isolation, test_auth_enabled
from database import db_service
from gemini_service import gemini_service, GCP_PROJECT_ID, MODEL_NAME

app = FastAPI(
    title="Personal Gemini Life Guardian & Executive Coach",
    description="Notion-style AI Journaling & Life Guardian Workspace with Live Voice Tool Calling, Kanban Ticketing, and Cloud Run deployment.",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------------
# Request & Response Schemas
# --------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    history: List[Dict[str, str]] = Field(default_factory=list)
    enable_memory_recall: bool = True

class LiveTurnRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    history: List[Dict[str, str]] = Field(default_factory=list)
    persona_mode: str = "coach"  # "coach" or "guardian"

class SaveJournalRequest(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    content: str = Field(default="")
    conversation: List[Dict[str, str]] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

class TicketRequest(BaseModel):
    id: Optional[str] = None
    title: str = Field(..., min_length=1)
    description: Optional[str] = ""
    column: str = "todo"  # "todo", "in_progress", "done"
    priority: str = "Medium"  # "Urgent", "High", "Medium", "Low"
    category: str = "General"  # "Work", "Wellness", "Mindset", "Study"
    date: Optional[str] = None

class TicketColumnUpdate(BaseModel):
    column: str = Field(..., pattern="^(todo|in_progress|done)$")

class CalendarEventRequest(BaseModel):
    id: Optional[str] = None
    title: str = Field(..., min_length=1)
    date: str = Field(..., min_length=10)
    time_block: str = "Morning Focus"
    notes: Optional[str] = ""

class ProfileRequest(BaseModel):
    primary_role: Optional[str] = None
    active_goals: Optional[List[str]] = None
    daily_routine: Optional[str] = None
    living_memory: Optional[List[str]] = None

class DistillActionRequest(BaseModel):
    content: str = Field(..., min_length=5)

class EmotionalArcRequest(BaseModel):
    conversation: List[Dict[str, str]] = Field(..., min_length=1)

class SettingsRequest(BaseModel):
    voice_responses_enabled: Optional[bool] = None
    tibetan_sound_enabled: Optional[bool] = None
    mac_notifications_enabled: Optional[bool] = None
    afternoon_reminder_enabled: Optional[bool] = None
    evening_shutdown_time: Optional[str] = None
    morning_start_time: Optional[str] = None
    ui_language: Optional[str] = None
    hotkey_quick_voice_enabled: Optional[bool] = None
    auto_circadian_persona: Optional[bool] = None
    burnout_shield_alerts: Optional[bool] = None
    big3_morning_prompt: Optional[bool] = None

# --------------------------------------------------------------------------
# Health & Identity Endpoints
# --------------------------------------------------------------------------
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "personal-gemini-journal-guardian",
        "version": "2.0.0",
        "gcp_project": GCP_PROJECT_ID,
        "gemini_model": MODEL_NAME,
        "firestore_live": db_service.is_live,
        "secret_manager_integrated": gemini_service.api_key is not None
    }

@app.get("/api/public-config")
def get_public_config():
    """
    Public configuration endpoint supplying non-secret Firebase client settings.
    Never exposes private keys, secrets, service account tokens, or emails.
    """
    env = os.environ.get("ENVIRONMENT", "production").strip().lower()
    auth_mode = "test" if test_auth_enabled() else "firebase"
    gcp_project = os.environ.get("GCP_PROJECT_ID", "intelligent-arc-488111-s0")

    firebase_config = {
        "apiKey": os.environ.get("FIREBASE_API_KEY", ""),
        "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN", f"{gcp_project}.firebaseapp.com"),
        "projectId": gcp_project,
        "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET", f"{gcp_project}.appspot.com"),
        "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID", ""),
        "appId": os.environ.get("FIREBASE_APP_ID", ""),
    }

    config_error = None
    if auth_mode == "firebase" and env == "production":
        missing = [k for k, v in [("apiKey", firebase_config["apiKey"]), ("appId", firebase_config["appId"])] if not v]
        if missing:
            config_error = f"Missing required production Firebase Web config: {', '.join(missing)}"

    return {
        "auth_mode": auth_mode,
        "environment": env,
        "firebase": firebase_config,
        "config_error": config_error,
    }

@app.get("/api/auth/me")
def get_user_profile(user: AuthenticatedUser = Depends(get_current_user)):
    return {
        "uid": user.uid,
        "email": user.email,
        "name": user.name,
        "auth_provider": user.auth_provider,
        "tenant_root": f"/users/{user.uid}"
    }

# --------------------------------------------------------------------------
# Live Conversational Voice Assistant with Autonomous Tool Execution
# --------------------------------------------------------------------------
@app.post("/api/agent/live-turn")
def live_agent_conversational_turn(
    req: LiveTurnRequest,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Core Live Agentic Endpoint:
    Receives voice transcript / chat message, parses intent, executes tool calls,
    and returns immediate spoken feedback + final conversational response.
    """
    profile = db_service.get_user_profile(uid=user.uid)
    result = gemini_service.live_agent_turn(
        user_message=req.message,
        conversation_history=req.history,
        persona_mode=req.persona_mode,
        user_profile=profile
    )

    executed_side_effects = []
    # Execute detected tools in real time
    for act in result.get("actions", []):
        tool = act.get("tool")
        params = act.get("params", {})

        if tool == "create_ticket":
            tkt = db_service.save_ticket(uid=user.uid, ticket={
                "title": params.get("title", "New Task"),
                "priority": params.get("priority", "Medium"),
                "category": params.get("category", "Work"),
                "column": params.get("column", "todo")
            })
            executed_side_effects.append({"action": "ticket_created", "ticket": tkt})

        elif tool == "move_ticket":
            new_col = params.get("new_column", "done")
            # Find matching ticket or update the most recent one
            all_tkts = db_service.get_tickets(uid=user.uid)
            target = None
            term = params.get("ticket_title_or_id", "").lower()
            for t in all_tkts:
                if term and (term in t.get("title", "").lower() or term in t.get("id", "").lower()):
                    target = t
                    break
            if not target and all_tkts:
                target = all_tkts[0]

            if target:
                updated = db_service.update_ticket_column(uid=user.uid, ticket_id=target["id"], new_column=new_col)
                executed_side_effects.append({"action": "ticket_moved", "ticket": updated})

        elif tool == "schedule_calendar":
            evt = db_service.save_calendar_event(uid=user.uid, event={
                "title": params.get("title", "Scheduled Focus"),
                "date": params.get("date"),
                "time_block": params.get("time_block", "Morning Focus")
            })
            executed_side_effects.append({"action": "calendar_scheduled", "event": evt})

        elif tool == "trigger_box_breathing":
            executed_side_effects.append({"action": "trigger_box_breathing"})

        elif tool == "trigger_shutdown_ritual":
            executed_side_effects.append({"action": "trigger_shutdown_ritual"})

        elif tool == "save_memory":
            mem = params.get("memory_item")
            if mem:
                updated_mems = db_service.append_living_memory(uid=user.uid, memory_item=mem)
                executed_side_effects.append({"action": "memory_saved", "memory": mem})

        elif tool == "synthesize_learned_rule":
            rule_obj = {
                "trigger": params.get("trigger_context", "General interaction"),
                "preference": params.get("learned_preference", ""),
                "rationale": params.get("rationale", ""),
                "learned_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            if rule_obj["preference"]:
                db_service.append_learned_rule(uid=user.uid, rule=rule_obj)
                executed_side_effects.append({"action": "rule_synthesized", "rule": rule_obj})

    # Fetch latest tickets to keep client in sync
    latest_tickets = db_service.get_tickets(uid=user.uid)

    return {
        "spoken_ack": result.get("spoken_ack", ""),
        "final_reply": result.get("final_reply", ""),
        "actions_executed": executed_side_effects,
        "sentiment": result.get("sentiment", 0.5),
        "detected_mode": result.get("detected_mode", req.persona_mode),
        "tickets": latest_tickets
    }

# --------------------------------------------------------------------------
# Drag-and-Drop Kanban Ticketing Endpoints (/api/tickets)
# --------------------------------------------------------------------------
@app.get("/api/tickets")
def list_tickets(user: AuthenticatedUser = Depends(get_current_user)):
    """Retrieves all tickets for the authenticated tenant."""
    tickets = db_service.get_tickets(uid=user.uid)
    return {"tickets": tickets, "count": len(tickets)}

@app.post("/api/tickets")
def create_ticket(
    req: TicketRequest,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Creates a new Kanban ticket in the user's isolated partition."""
    tkt = db_service.save_ticket(uid=user.uid, ticket=req.model_dump())
    return {"status": "created", "ticket": tkt}

@app.put("/api/tickets/{ticket_id}/column")
def move_ticket_column(
    ticket_id: str,
    req: TicketColumnUpdate,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Updates the ticket's column ('todo', 'in_progress', 'done') via drag & drop."""
    updated = db_service.update_ticket_column(uid=user.uid, ticket_id=ticket_id, new_column=req.column)
    if not updated:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"status": "updated", "ticket": updated}

@app.delete("/api/tickets/{ticket_id}")
def delete_ticket(
    ticket_id: str,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Deletes a ticket strictly from the user's partition."""
    success = db_service.delete_ticket(uid=user.uid, ticket_id=ticket_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"status": "deleted", "ticket_id": ticket_id}

# --------------------------------------------------------------------------
# Calendar Endpoints (/api/calendar/events)
# --------------------------------------------------------------------------
@app.get("/api/calendar/events")
def list_calendar_events(user: AuthenticatedUser = Depends(get_current_user)):
    events = db_service.get_calendar_events(uid=user.uid)
    return {"events": events}

@app.post("/api/calendar/events")
def create_calendar_event(
    req: CalendarEventRequest,
    user: AuthenticatedUser = Depends(get_current_user)
):
    evt = db_service.save_calendar_event(uid=user.uid, event=req.model_dump())
    return {"status": "created", "event": evt}

# --------------------------------------------------------------------------
# User Profile & Living Context Endpoints (/api/profile)
# --------------------------------------------------------------------------
@app.get("/api/profile")
def get_profile(user: AuthenticatedUser = Depends(get_current_user)):
    profile = db_service.get_user_profile(uid=user.uid)
    return profile

@app.post("/api/profile")
def save_profile(
    req: ProfileRequest,
    user: AuthenticatedUser = Depends(get_current_user)
):
    existing = db_service.get_user_profile(uid=user.uid)
    updated_data = {**existing, **{k: v for k, v in req.model_dump().items() if v is not None}}
    saved = db_service.save_user_profile(uid=user.uid, profile_data=updated_data)
    return {"status": "saved", "profile": saved}

# --------------------------------------------------------------------------
# User Settings Endpoints (/api/settings)
# --------------------------------------------------------------------------
@app.get("/api/settings")
def get_user_settings_endpoint(user: AuthenticatedUser = Depends(get_current_user)):
    return db_service.get_user_settings(uid=user.uid)

@app.post("/api/settings")
def save_user_settings_endpoint(
    req: SettingsRequest,
    user: AuthenticatedUser = Depends(get_current_user)
):
    clean_dict = {k: v for k, v in req.model_dump().items() if v is not None}
    saved = db_service.save_user_settings(uid=user.uid, settings_data=clean_dict)
    return {"status": "saved", "settings": saved}

@app.delete("/api/data/reset")
def reset_sanctuary_data(user: AuthenticatedUser = Depends(get_current_user)):
    """Wipes all tickets, journals, and calendar items for full user data sovereignty."""
    success = db_service.reset_user_sanctuary_data(uid=user.uid)
    return {"status": "reset", "success": success}

# --------------------------------------------------------------------------
# Obsidian Markdown Export (/api/export/obsidian/{journal_id})
# --------------------------------------------------------------------------
@app.get("/api/export/obsidian/{journal_id}")
def export_obsidian_markdown(
    journal_id: str,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Generates clean Obsidian Markdown with YAML frontmatter for instant vault import."""
    entry = db_service.get_journal(uid=user.uid, journal_id=journal_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Journal not found")
    tickets = db_service.get_tickets(uid=user.uid)
    md_content = gemini_service.format_obsidian_markdown(entry, tickets)
    return Response(
        content=md_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=journal-{journal_id[:8]}.md"}
    )

# --------------------------------------------------------------------------
# Core Journaling Endpoints
# --------------------------------------------------------------------------
@app.post("/api/chat")
def chat_with_gemini(
    req: ChatRequest,
    user: AuthenticatedUser = Depends(get_current_user)
):
    past_wisdom_text = None
    matched_past_entry = None

    if req.enable_memory_recall:
        past_journals = db_service.get_journals(uid=user.uid, limit=10)
        recalled = gemini_service.recall_past_wisdom(req.message, past_journals)
        if recalled and recalled.get("past_wisdom"):
            past_wisdom_text = f"{recalled.get('past_wisdom')} ({recalled.get('encouragement', '')})"
            matched_past_entry = recalled

    ai_reply = gemini_service.chat_turn(
        conversation_history=req.history,
        user_message=req.message,
        past_wisdom=past_wisdom_text
    )

    return {
        "reply": ai_reply,
        "matched_past_wisdom": matched_past_entry
    }

@app.post("/api/journal/save")
def save_journal_entry(
    req: SaveJournalRequest,
    user: AuthenticatedUser = Depends(get_current_user)
):
    summary_data = {}
    if req.conversation and len(req.conversation) > 0:
        summary_data = gemini_service.summarize_session(req.conversation)
    
    title = req.title or summary_data.get("title") or "Evening Reflection"
    summary = summary_data.get("summary") or (req.content[:200] + "..." if len(req.content) > 200 else req.content)

    arc_data = {}
    if req.conversation and len(req.conversation) > 0:
        arc_data = gemini_service.analyze_emotional_arc(req.conversation)

    action_text = req.content or "\n".join([m.get("text", "") for m in req.conversation])
    action_items = []
    if action_text and len(action_text.strip()) > 10:
        action_items = gemini_service.distill_action_items(action_text)

    entry_payload = {
        "id": req.id,
        "title": title,
        "content": req.content,
        "conversation": req.conversation,
        "summary": summary,
        "breakthrough": summary_data.get("breakthrough", ""),
        "emotional_arc": arc_data,
        "action_items": action_items,
        "tags": req.tags or summary_data.get("tags", ["Reflection"])
    }

    saved_doc = db_service.save_journal(uid=user.uid, entry=entry_payload)

    if arc_data:
        db_service.save_emotional_insight(uid=user.uid, insight={
            "journal_id": saved_doc["id"],
            "sentiment_score": arc_data.get("overall_sentiment", 0.0),
            "energy_score": arc_data.get("overall_energy", 0.5),
            "clarity_score": arc_data.get("overall_clarity", 0.5),
            "dominant_emotion": arc_data.get("dominant_emotion", "Reflective")
        })

    return {
        "status": "success",
        "entry": saved_doc
    }

@app.get("/api/journal/entries")
def list_journal_entries(
    limit: int = 50,
    user: AuthenticatedUser = Depends(get_current_user)
):
    entries = db_service.get_journals(uid=user.uid, limit=limit)
    return {"entries": entries, "count": len(entries)}

@app.get("/api/journal/{journal_id}")
def get_single_journal(
    journal_id: str,
    user: AuthenticatedUser = Depends(get_current_user)
):
    entry = db_service.get_journal(uid=user.uid, journal_id=journal_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    enforce_user_isolation(user, entry["uid"])
    return entry

@app.delete("/api/journal/{journal_id}")
def delete_journal(
    journal_id: str,
    user: AuthenticatedUser = Depends(get_current_user)
):
    success = db_service.delete_journal(uid=user.uid, journal_id=journal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return {"status": "deleted", "journal_id": journal_id}

@app.post("/api/insights/emotional-arc")
def get_emotional_arc(
    req: EmotionalArcRequest,
    user: AuthenticatedUser = Depends(get_current_user)
):
    arc = gemini_service.analyze_emotional_arc(req.conversation)
    return arc

@app.get("/api/insights/history")
def get_emotional_history(
    limit: int = 20,
    user: AuthenticatedUser = Depends(get_current_user)
):
    history = db_service.get_emotional_history(uid=user.uid, limit=limit)
    return {"insights": history}

@app.post("/api/actions/distill")
def distill_action_items_endpoint(
    req: DistillActionRequest,
    user: AuthenticatedUser = Depends(get_current_user)
):
    actions = gemini_service.distill_action_items(req.content)
    return {"action_items": actions}

# --------------------------------------------------------------------------
# Static Assets & Frontend Web Application
# --------------------------------------------------------------------------
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return JSONResponse({"message": "Personal Gemini Life Guardian is running. UI assets not found."})
