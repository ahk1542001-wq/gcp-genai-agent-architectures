"""
FastAPI Application Entry Point for Personal Gemini Life Guardian & Executive Coach
Production Serverless Service deployed on Google Cloud Run.
Enforces Zero-Trust Architecture, strict tenant-isolated Firestore endpoints,
Drag-and-Drop Kanban Ticketing, Interactive Calendar, Obsidian Export,
and Autonomous Live Voice Tool Calling.
"""

import os
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Literal
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
    persona_mode: str = Field(default="balanced", pattern="^(balanced|actionable|philosophy|brainstorm|coach|guardian)$")

class SummarizeRequest(BaseModel):
    conversation: List[Dict[str, str]] = Field(default_factory=list)
    text: Optional[str] = None

class ActionProposal(BaseModel):
    tool: Literal[
        "create_ticket",
        "move_ticket",
        "schedule_calendar",
        "save_memory",
        "synthesize_learned_rule",
        "trigger_box_breathing",
        "trigger_shutdown_ritual"
    ]
    params: Dict[str, Any] = Field(default_factory=dict)

class ConfirmedActionRequest(BaseModel):
    action: ActionProposal
    confirmed: bool

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

class VoiceSynthesizeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)

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
# Live Conversational Voice Assistant with Human-in-the-Loop Tool Confirmation
# --------------------------------------------------------------------------
SUPPORTED_PERSISTENT_TOOLS = {
    "create_ticket",
    "move_ticket",
    "schedule_calendar",
    "save_memory",
    "synthesize_learned_rule"
}

SUPPORTED_UI_TOOLS = {
    "trigger_box_breathing",
    "trigger_shutdown_ritual"
}

def execute_persistent_action(uid: str, action: ActionProposal) -> Dict[str, Any]:
    """
    Typed helper that validates and executes exactly one persistent action
    for the authenticated user tenant.
    """
    tool = action.tool
    params = action.params or {}

    if tool in SUPPORTED_UI_TOOLS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"UI action '{tool}' does not execute persistent writes."
        )

    if tool == "create_ticket":
        title = str(params.get("title", "New Task")).strip()
        if not title:
            title = "New Task"
        priority = params.get("priority", "Medium")
        if priority not in ("Urgent", "High", "Medium", "Low"):
            priority = "Medium"
        category = params.get("category", "Work")
        if category not in ("Work", "Wellness", "Mindset", "Study", "Personal", "General"):
            category = "Work"
        column = params.get("column", "todo")
        if column not in ("todo", "in_progress", "done"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid ticket column: '{column}'. Must be 'todo', 'in_progress', or 'done'."
            )
        tkt = db_service.save_ticket(uid=uid, ticket={
            "title": title[:200],
            "priority": priority,
            "category": category,
            "column": column
        })
        latest_tickets = db_service.get_tickets(uid=uid)
        return {
            "status": "executed",
            "action": {"tool": tool, "params": params},
            "result": tkt,
            "tickets": latest_tickets
        }

    elif tool == "move_ticket":
        new_col = params.get("new_column", "done")
        if new_col not in ("todo", "in_progress", "done"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid column: '{new_col}'"
            )
        all_tkts = db_service.get_tickets(uid=uid)
        target = None
        term = str(params.get("ticket_title_or_id", "")).strip().lower()
        for t in all_tkts:
            if term and (term in t.get("title", "").lower() or term in t.get("id", "").lower()):
                target = t
                break
        if not target and all_tkts:
            target = all_tkts[0]

        if target:
            updated = db_service.update_ticket_column(uid=uid, ticket_id=target["id"], new_column=new_col)
            latest_tickets = db_service.get_tickets(uid=uid)
            return {
                "status": "executed",
                "action": {"tool": tool, "params": params},
                "result": updated,
                "tickets": latest_tickets
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No matching ticket found to move."
            )

    elif tool == "schedule_calendar":
        title = str(params.get("title", "Scheduled Focus")).strip() or "Scheduled Focus"
        date_str = str(params.get("date", "")).strip()
        if not date_str:
            date_str = datetime.date.today().isoformat()
        else:
            try:
                datetime.date.fromisoformat(date_str)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid date format '{date_str}', expected YYYY-MM-DD."
                )
        time_block = params.get("time_block", "Morning Focus")
        evt = db_service.save_calendar_event(uid=uid, event={
            "title": title[:200],
            "date": date_str,
            "time_block": time_block
        })
        return {
            "status": "executed",
            "action": {"tool": tool, "params": params},
            "result": evt
        }

    elif tool == "save_memory":
        mem = str(params.get("memory_item", "")).strip()
        if not mem:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="memory_item cannot be empty.")
        updated_mems = db_service.append_living_memory(uid=uid, memory_item=mem[:500])
        return {
            "status": "executed",
            "action": {"tool": tool, "params": params},
            "result": {"memory": mem, "living_memory": updated_mems}
        }

    elif tool == "synthesize_learned_rule":
        pref = str(params.get("learned_preference", "")).strip()
        if not pref:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="learned_preference cannot be empty.")
        rule_obj = {
            "trigger": str(params.get("trigger_context", "General interaction")).strip()[:200],
            "preference": pref[:500],
            "rationale": str(params.get("rationale", "")).strip()[:300],
            "learned_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        db_service.append_learned_rule(uid=uid, rule=rule_obj)
        return {
            "status": "executed",
            "action": {"tool": tool, "params": params},
            "result": rule_obj
        }

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=f"Unsupported tool action: '{tool}'"
    )

@app.post("/api/agent/live-turn")
def live_agent_conversational_turn(
    req: LiveTurnRequest,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Core Live Agentic Endpoint:
    Receives voice transcript / chat message, parses intent via Gemini,
    proposes persistent actions for human confirmation, and returns immediate
    spoken feedback + final conversational response.
    """
    profile = db_service.get_user_profile(uid=user.uid)
    result = gemini_service.live_agent_turn(
        user_message=req.message,
        conversation_history=req.history,
        persona_mode=req.persona_mode,
        user_profile=profile
    )

    proposed_actions = []
    ui_actions = []

    # Non-persistent UI actions run directly; persistent actions require approval
    for act in result.get("actions", []):
        tool = act.get("tool")
        params = act.get("params", {})
        if tool in SUPPORTED_UI_TOOLS:
            ui_actions.append({"tool": tool, "params": params})
        elif tool in SUPPORTED_PERSISTENT_TOOLS:
            proposed_actions.append({"tool": tool, "params": params})

    latest_tickets = db_service.get_tickets(uid=user.uid)

    return {
        "spoken_ack": result.get("spoken_ack", ""),
        "final_reply": result.get("final_reply", ""),
        "proposed_actions": proposed_actions,
        "ui_actions": ui_actions,
        "actions_executed": [],
        "sentiment": result.get("sentiment", 0.5),
        "detected_mode": result.get("detected_mode", req.persona_mode),
        "tickets": latest_tickets
    }

@app.post("/api/agent/summarize")
def agent_summarize_reflection(
    req: SummarizeRequest,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Distills structured takeaways, title, tags, and cognitive realization from multi-turn dialogue.
    """
    history = req.conversation
    if not history and req.text:
        history = [{"role": "user", "text": req.text}]
    summary_data = gemini_service.summarize_session(history)
    return summary_data

@app.post("/api/agent/actions/confirm")
def confirm_agent_action(
    req: ConfirmedActionRequest,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Executes exactly one validated persistent action for the authenticated tenant
    only after explicit human user confirmation.
    """
    if not req.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action must be confirmed=true to execute."
        )
    return execute_persistent_action(uid=user.uid, action=req.action)

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

@app.delete("/api/calendar/events/{event_id}")
def delete_calendar_event_endpoint(
    event_id: str,
    user: AuthenticatedUser = Depends(get_current_user)
):
    success = db_service.delete_calendar_event(uid=user.uid, event_id=event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"status": "deleted", "id": event_id}

# --------------------------------------------------------------------------
# Life Rewind & Real Statistics (/api/rewind)
# --------------------------------------------------------------------------
@app.get("/api/rewind")
def get_rewind_metrics(user: AuthenticatedUser = Depends(get_current_user)):
    """
    Calculates genuine user metrics grounded strictly in authenticated tenant data:
    - total journal entries
    - total words written
    - real consecutive habit streak days
    - completed vs open tickets
    - living memory insights
    - real recent tags and reflections
    """
    journals = db_service.get_journals(uid=user.uid)
    tickets = db_service.get_tickets(uid=user.uid)
    profile = db_service.get_user_profile(uid=user.uid)

    total_entries = len(journals)
    total_words = sum(len((j.get("content") or "").split()) for j in journals)
    completed_tickets = sum(1 for t in tickets if t.get("column") == "done")
    open_tickets = sum(1 for t in tickets if t.get("column") in ("todo", "in_progress"))

    # Real streak calculation: consecutive days ending today or yesterday
    entry_dates = set()
    for j in journals:
        d = j.get("date") or (j.get("created_at") or "")[:10]
        if d:
            entry_dates.add(d)

    streak_days = 0
    today = datetime.date.today()
    check_date = today
    if check_date.isoformat() not in entry_dates:
        check_date = today - datetime.timedelta(days=1)
    while check_date.isoformat() in entry_dates:
        streak_days += 1
        check_date -= datetime.timedelta(days=1)

    recent_tags = list({tag for j in journals for tag in j.get("tags", [])})[:10]
    recent_reflections = [
        {
            "id": j.get("id"),
            "title": j.get("title") or "Reflection",
            "date": j.get("date") or (j.get("created_at") or "")[:10],
            "excerpt": (j.get("content") or "")[:150]
        }
        for j in journals[:5]
    ]

    return {
        "total_entries": total_entries,
        "total_words": total_words,
        "streak_days": streak_days,
        "completed_tickets": completed_tickets,
        "open_tickets": open_tickets,
        "living_memories_count": len(profile.get("living_memory", [])),
        "recent_tags": recent_tags,
        "recent_reflections": recent_reflections
    }

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
@app.get("/api/journals")
def list_journal_entries(
    limit: int = 50,
    user: AuthenticatedUser = Depends(get_current_user)
):
    entries = db_service.get_journals(uid=user.uid, limit=limit)
    return {"entries": entries, "count": len(entries)}

@app.get("/api/report/executive")
def get_executive_data_report(user: AuthenticatedUser = Depends(get_current_user)):
    """
    Calculates authentic, tenant-isolated Executive Cognitive & Productivity Data Report.
    Strict zero-hardcode policy: aggregates real Firestore journals, tickets, calendar focus blocks, and living profile.
    """
    journals = db_service.get_journals(uid=user.uid, limit=100)
    tickets = db_service.get_tickets(uid=user.uid)
    calendar_events = db_service.get_calendar_events(uid=user.uid)
    profile = db_service.get_user_profile(uid=user.uid)

    total_words = sum(len((j.get("content") or "").split()) for j in journals)
    total_entries = len(journals)
    done_tickets = [t for t in tickets if t.get("column") == "done"]
    in_progress_tickets = [t for t in tickets if t.get("column") == "in_progress"]
    todo_tickets = [t for t in tickets if t.get("column") == "todo"]
    focus_blocks = len(calendar_events)
    living_memories = profile.get("living_memory", [])
    learned_rules = profile.get("learned_rules", [])

    return {
        "user_name": user.name or "Journaler",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "productivity": {
            "total_words_written": total_words,
            "total_reflections": total_entries,
            "completed_tasks": len(done_tickets),
            "in_progress_tasks": len(in_progress_tickets),
            "todo_tasks": len(todo_tickets),
            "focus_blocks_scheduled": focus_blocks
        },
        "living_intelligence": {
            "memories_count": len(living_memories),
            "learned_rules_count": len(learned_rules),
            "recent_rules": learned_rules[:5],
            "burnout_risk": profile.get("burnout_risk", "Low")
        },
        "recent_reflections": [
            {
                "id": j.get("id"),
                "title": j.get("title", "Reflection"),
                "date": (j.get("created_at") or "")[:10],
                "summary": j.get("summary", "")
            }
            for j in journals[:10]
        ]
    }

@app.post("/api/voice/synthesize")
def synthesize_voice_response(
    req: VoiceSynthesizeRequest,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Synthesizes speech audio using Google Cloud Text-to-Speech API with Application Default Credentials.
    Uses high-fidelity Studio/Journey neural voice (en-US-Journey-F) for soothing, authentic live voice response.
    Returns base64-encoded MP3 audio for live browser playback.
    """
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    # In test mode, return valid mock base64 audio gracefully
    if os.environ.get("ENVIRONMENT") == "test" or os.environ.get("IS_TEST_MODE") == "true":
        return {
            "status": "success",
            "audio_base64": "UklGRjIAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=",
            "format": "mp3",
            "voice": "mock-test-voice",
            "text": text
        }

    try:
        from google.cloud import texttospeech
        import base64
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text[:1500])
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Journey-F",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.95,
            pitch=0.0
        )
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        audio_b64 = base64.b64encode(response.audio_content).decode("utf-8")
        return {
            "status": "success",
            "audio_base64": audio_b64,
            "format": "mp3",
            "voice": "en-US-Journey-F",
            "text": text
        }
    except Exception as e:
        print(f"[TextToSpeech] Synthesis fallback: {e}")
        return {
            "status": "fallback",
            "audio_base64": None,
            "error": str(e),
            "text": text
        }

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
