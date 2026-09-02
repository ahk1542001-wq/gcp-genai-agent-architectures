"""
FastAPI Application Entry Point for Personal Gemini Journal
Production Serverless Service deployed on Google Cloud Run.
Enforces Zero-Trust Architecture, strict tenant-isolated Firestore endpoints,
and integration with Gemini 2.5 Flash / Secret Manager.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from auth import get_current_user, AuthenticatedUser, enforce_user_isolation
from database import db_service
from gemini_service import gemini_service, GCP_PROJECT_ID, MODEL_NAME

app = FastAPI(
    title="Secure Personal Gemini Journal",
    description="Production-grade AI Journaling application built on Google Cloud Run, Firebase Auth, Cloud Firestore, and Gemini API.",
    version="1.0.0"
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

class SaveJournalRequest(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    content: str = Field(default="")
    conversation: List[Dict[str, str]] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

class DistillActionRequest(BaseModel):
    content: str = Field(..., min_length=5)

class EmotionalArcRequest(BaseModel):
    conversation: List[Dict[str, str]] = Field(..., min_length=1)

# --------------------------------------------------------------------------
# Health & Identity Endpoints
# --------------------------------------------------------------------------
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "personal-gemini-journal",
        "gcp_project": GCP_PROJECT_ID,
        "gemini_model": MODEL_NAME,
        "firestore_live": db_service.is_live,
        "secret_manager_integrated": gemini_service.api_key is not None
    }

@app.get("/api/auth/me")
def get_user_profile(user: AuthenticatedUser = Depends(get_current_user)):
    """Returns verified user token claims and identity."""
    return {
        "uid": user.uid,
        "email": user.email,
        "name": user.name,
        "auth_provider": user.auth_provider,
        "tenant_root": f"/users/{user.uid}"
    }

# --------------------------------------------------------------------------
# Core Journaling & Multi-turn Chat Endpoints
# --------------------------------------------------------------------------
@app.post("/api/chat")
def chat_with_gemini(
    req: ChatRequest,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Empathetic, multi-turn conversational journaling companion.
    Uses strict delimiter encapsulation against prompt injection.
    Optionally searches past journal reflections to inject wisdom.
    """
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
    """
    Saves or auto-saves a journal entry under /users/{uid}/journals/{id}.
    Automatically generates summary, emotional arc, and action items if not present.
    """
    # Auto-generate synthesis if conversation exists
    summary_data = {}
    if req.conversation and len(req.conversation) > 0:
        summary_data = gemini_service.summarize_session(req.conversation)
    
    title = req.title or summary_data.get("title") or "Evening Reflection"
    summary = summary_data.get("summary") or (req.content[:200] + "..." if len(req.content) > 200 else req.content)

    # Feature 1: Emotional Arc
    arc_data = {}
    if req.conversation and len(req.conversation) > 0:
        arc_data = gemini_service.analyze_emotional_arc(req.conversation)

    # Feature 3: Action Items
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

    # Save emotional insight aggregate
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
    """Retrieves journal entries strictly scoped to the authenticated user."""
    entries = db_service.get_journals(uid=user.uid, limit=limit)
    return {"entries": entries, "count": len(entries)}

@app.get("/api/journal/{journal_id}")
def get_single_journal(
    journal_id: str,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Retrieves a single journal document with strict ownership verification."""
    entry = db_service.get_journal(uid=user.uid, journal_id=journal_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found"
        )
    enforce_user_isolation(user, entry["uid"])
    return entry

@app.delete("/api/journal/{journal_id}")
def delete_journal(
    journal_id: str,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Deletes a journal entry within the authenticated user's isolated path."""
    success = db_service.delete_journal(uid=user.uid, journal_id=journal_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found or cannot be deleted"
        )
    return {"status": "deleted", "journal_id": journal_id}

# --------------------------------------------------------------------------
# Original Feature Endpoints
# --------------------------------------------------------------------------
@app.post("/api/insights/emotional-arc")
def get_emotional_arc(
    req: EmotionalArcRequest,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Evaluates emotional & cognitive trajectory across session turns."""
    arc = gemini_service.analyze_emotional_arc(req.conversation)
    return arc

@app.get("/api/insights/history")
def get_emotional_history(
    limit: int = 20,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Returns past emotional progression data points for trends/rewind."""
    history = db_service.get_emotional_history(uid=user.uid, limit=limit)
    return {"insights": history}

@app.post("/api/actions/distill")
def distill_action_items_endpoint(
    req: DistillActionRequest,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Converts stream-of-consciousness text into prioritized TODOs."""
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
    return JSONResponse({"message": "Personal Gemini Journal API is running. UI assets not found."})
