"""
Cloud Firestore Database Layer for Personal Gemini Journal
Enforces strict tenant isolation (/users/{uid}/journals/{doc_id}, /users/{uid}/tickets/{id}, /users/{uid}/profile)
with zero cross-user leakage and fallback in-memory mock for local testing.
"""

import os
import uuid
import datetime
from typing import Optional, List, Dict, Any

GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "intelligent-arc-488111-s0")
USE_MOCK_DB = os.environ.get("USE_MOCK_DB", "false").lower() == "true"

# In-Memory tenant-partitioned store: {uid: {"journals": {}, "insights": {}, "tickets": {}, "calendar": {}, "profile": {}}}
_MEMORY_STORE: Dict[str, Dict[str, Dict[str, Any]]] = {}

def _get_memory_bucket(uid: str, collection: str) -> Dict[str, Any]:
    if uid not in _MEMORY_STORE:
        _MEMORY_STORE[uid] = {
            "journals": {},
            "insights": {},
            "tickets": {},
            "calendar": {},
            "profile": {},
            "settings": {}
        }
    if collection not in _MEMORY_STORE[uid]:
        _MEMORY_STORE[uid][collection] = {}
    return _MEMORY_STORE[uid][collection]


class FirestoreService:
    def __init__(self):
        self.client = None
        self.is_live = False
        if not USE_MOCK_DB:
            try:
                from google.cloud import firestore
                self.client = firestore.Client(project=GCP_PROJECT_ID)
                self.is_live = True
                print(f"[FirestoreService] Connected to Cloud Firestore for project: {GCP_PROJECT_ID}")
            except Exception as e:
                print(f"[FirestoreService] Notice: Live Firestore unavailable ({e}). Falling back to isolated in-memory tenant store.")
                self.is_live = False

    # -------------------------------------------------------------------------
    # Journal Operations (/users/{uid}/journals/{journal_id})
    # -------------------------------------------------------------------------
    def save_journal(self, uid: str, entry: Dict[str, Any]) -> Dict[str, Any]:
        if not uid:
            raise ValueError("UID is required for journal storage")

        journal_id = entry.get("id") or f"entry_{uuid.uuid4().hex[:12]}"
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        doc_data = {
            "id": journal_id,
            "uid": uid,
            "title": entry.get("title", "Reflective Journal Entry"),
            "content": entry.get("content", ""),
            "conversation": entry.get("conversation", []),
            "summary": entry.get("summary", ""),
            "emotional_arc": entry.get("emotional_arc", {}),
            "action_items": entry.get("action_items", []),
            "tags": entry.get("tags", []),
            "created_at": entry.get("created_at") or now,
            "updated_at": now
        }

        if self.is_live and self.client:
            doc_ref = self.client.collection("users").document(uid).collection("journals").document(journal_id)
            doc_ref.set(doc_data)
        else:
            bucket = _get_memory_bucket(uid, "journals")
            bucket[journal_id] = doc_data

        return doc_data

    def get_journals(self, uid: str, limit: int = 50) -> List[Dict[str, Any]]:
        if not uid:
            return []

        if self.is_live and self.client:
            journals_ref = (
                self.client.collection("users")
                .document(uid)
                .collection("journals")
                .order_by("created_at", direction="DESCENDING")
                .limit(limit)
            )
            return [doc.to_dict() for doc in journals_ref.stream()]
        else:
            bucket = _get_memory_bucket(uid, "journals")
            items = list(bucket.values())
            items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return items[:limit]

    def get_journal(self, uid: str, journal_id: str) -> Optional[Dict[str, Any]]:
        if not uid or not journal_id:
            return None

        if self.is_live and self.client:
            doc_ref = self.client.collection("users").document(uid).collection("journals").document(journal_id)
            doc = doc_ref.get()
            return doc.to_dict() if doc.exists else None
        else:
            bucket = _get_memory_bucket(uid, "journals")
            return bucket.get(journal_id)

    def delete_journal(self, uid: str, journal_id: str) -> bool:
        if not uid or not journal_id:
            return False

        if self.is_live and self.client:
            doc_ref = self.client.collection("users").document(uid).collection("journals").document(journal_id)
            doc = doc_ref.get()
            if not doc.exists:
                return False
            doc_ref.delete()
            return True
        else:
            bucket = _get_memory_bucket(uid, "journals")
            if journal_id in bucket:
                del bucket[journal_id]
                return True
            return False

    # -------------------------------------------------------------------------
    # Drag-and-Drop Ticketing Operations (/users/{uid}/tickets/{ticket_id})
    # Columns: "todo", "in_progress", "done"
    # -------------------------------------------------------------------------
    def save_ticket(self, uid: str, ticket: Dict[str, Any]) -> Dict[str, Any]:
        if not uid:
            raise ValueError("UID is required for ticket storage")

        ticket_id = ticket.get("id") or f"tkt_{uuid.uuid4().hex[:10]}"
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()

        doc_data = {
            "id": ticket_id,
            "uid": uid,
            "title": ticket.get("title", "Untitled Task"),
            "description": ticket.get("description", ""),
            "column": ticket.get("column", "todo"),  # "todo", "in_progress", "done"
            "priority": ticket.get("priority", "Medium"),  # "Urgent", "High", "Medium", "Low"
            "category": ticket.get("category", "General"),  # "Work", "Wellness", "Mindset", "Study"
            "date": ticket.get("date") or now[:10],
            "created_at": ticket.get("created_at") or now,
            "updated_at": now
        }

        if self.is_live and self.client:
            doc_ref = self.client.collection("users").document(uid).collection("tickets").document(ticket_id)
            doc_ref.set(doc_data)
        else:
            bucket = _get_memory_bucket(uid, "tickets")
            bucket[ticket_id] = doc_data

        return doc_data

    def get_tickets(self, uid: str) -> List[Dict[str, Any]]:
        if not uid:
            return []

        if self.is_live and self.client:
            tickets_ref = self.client.collection("users").document(uid).collection("tickets").stream()
            return [doc.to_dict() for doc in tickets_ref]
        else:
            bucket = _get_memory_bucket(uid, "tickets")
            return list(bucket.values())

    def update_ticket_column(self, uid: str, ticket_id: str, new_column: str) -> Optional[Dict[str, Any]]:
        if not uid or not ticket_id:
            return None

        if new_column not in ["todo", "in_progress", "done"]:
            new_column = "todo"

        now = datetime.datetime.now(datetime.timezone.utc).isoformat()

        if self.is_live and self.client:
            doc_ref = self.client.collection("users").document(uid).collection("tickets").document(ticket_id)
            doc = doc_ref.get()
            if not doc.exists:
                return None
            doc_ref.update({"column": new_column, "updated_at": now})
            updated = doc.to_dict()
            updated["column"] = new_column
            return updated
        else:
            bucket = _get_memory_bucket(uid, "tickets")
            if ticket_id in bucket:
                bucket[ticket_id]["column"] = new_column
                bucket[ticket_id]["updated_at"] = now
                return bucket[ticket_id]
            return None

    def delete_ticket(self, uid: str, ticket_id: str) -> bool:
        if not uid or not ticket_id:
            return False

        if self.is_live and self.client:
            doc_ref = self.client.collection("users").document(uid).collection("tickets").document(ticket_id)
            if not doc_ref.get().exists:
                return False
            doc_ref.delete()
            return True
        else:
            bucket = _get_memory_bucket(uid, "tickets")
            if ticket_id in bucket:
                del bucket[ticket_id]
                return True
            return False

    # -------------------------------------------------------------------------
    # Calendar Events (/users/{uid}/calendar/{event_id})
    # -------------------------------------------------------------------------
    def save_calendar_event(self, uid: str, event: Dict[str, Any]) -> Dict[str, Any]:
        if not uid:
            raise ValueError("UID required")
        event_id = event.get("id") or f"evt_{uuid.uuid4().hex[:10]}"
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        doc_data = {
            "id": event_id,
            "uid": uid,
            "title": event.get("title", "Scheduled Focus"),
            "date": event.get("date") or now[:10],
            "time_block": event.get("time_block", "Morning Focus"),
            "notes": event.get("notes", ""),
            "created_at": now
        }
        if self.is_live and self.client:
            self.client.collection("users").document(uid).collection("calendar").document(event_id).set(doc_data)
        else:
            bucket = _get_memory_bucket(uid, "calendar")
            bucket[event_id] = doc_data
        return doc_data

    def get_calendar_events(self, uid: str) -> List[Dict[str, Any]]:
        if not uid:
            return []
        if self.is_live and self.client:
            ref = self.client.collection("users").document(uid).collection("calendar").stream()
            return [doc.to_dict() for doc in ref]
        else:
            bucket = _get_memory_bucket(uid, "calendar")
            return list(bucket.values())

    def delete_calendar_event(self, uid: str, event_id: str) -> bool:
        if not uid or not event_id:
            return False
        if self.is_live and self.client:
            self.client.collection("users").document(uid).collection("calendar").document(event_id).delete()
            return True
        else:
            bucket = _get_memory_bucket(uid, "calendar")
            if event_id in bucket:
                del bucket[event_id]
                return True
            return False

    # -------------------------------------------------------------------------
    # User Profile & Living Context (/users/{uid}/profile/main)
    # -------------------------------------------------------------------------
    def get_user_profile(self, uid: str) -> Dict[str, Any]:
        default_profile = {
            "uid": uid,
            "primary_role": "AI Engineer & Developer",
            "active_goals": ["Build APAC GenAI Ideathon Champion App", "Pass Cloud Run Certification"],
            "daily_routine": "Morning Deep Work, Afternoon sprint, Evening wind-down",
            "burnout_risk": "Low",
            "living_memory": [
                "Solved complex MCP server challenge on Track 2 with 10/10 perfect score.",
                "Values privacy and zero-trust cloud architecture deeply."
            ],
            "learned_rules": [
                {
                    "trigger": "hackathon tasks",
                    "preference": "categorize strictly as Hackathon sprint priorities",
                    "rationale": "Explicit user operational preference"
                }
            ]
        }
        if not uid:
            return default_profile

        if self.is_live and self.client:
            doc_ref = self.client.collection("users").document(uid).collection("profile").document("main")
            doc = doc_ref.get()
            return doc.to_dict() if doc.exists else default_profile
        else:
            bucket = _get_memory_bucket(uid, "profile")
            return bucket.get("main", default_profile)

    def save_user_profile(self, uid: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        if not uid:
            raise ValueError("UID required")
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        profile_data["uid"] = uid
        profile_data["updated_at"] = now
        if self.is_live and self.client:
            self.client.collection("users").document(uid).collection("profile").document("main").set(profile_data)
        else:
            bucket = _get_memory_bucket(uid, "profile")
            bucket["main"] = profile_data
        return profile_data

    def append_living_memory(self, uid: str, memory_item: str) -> List[str]:
        if not uid or not memory_item:
            return []
        profile = self.get_user_profile(uid)
        memories = profile.get("living_memory", [])
        if memory_item not in memories:
            memories.append(memory_item)
            profile["living_memory"] = memories[-20:]
            self.save_user_profile(uid, profile)
        return profile.get("living_memory", [])

    def append_learned_rule(self, uid: str, rule: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Hermes Closed-Loop Learning: Appends an operational rule distilled from user correction."""
        if not uid or not rule:
            return []
        profile = self.get_user_profile(uid)
        rules = profile.get("learned_rules", [])
        rules.append(rule)
        profile["learned_rules"] = rules[-20:]
        self.save_user_profile(uid, profile)
        return profile.get("learned_rules", [])

    # -------------------------------------------------------------------------
    # User Preferences & Settings (/users/{uid}/settings/main)
    # -------------------------------------------------------------------------
    def get_user_settings(self, uid: str) -> Dict[str, Any]:
        default_settings = {
            "uid": uid,
            "voice_responses_enabled": True,
            "tibetan_sound_enabled": True,
            "mac_notifications_enabled": True,
            "afternoon_reminder_enabled": True,
            "morning_start_time": "08:00",
            "evening_shutdown_time": "18:00",
            "ui_language": "en",
            "hotkey_quick_voice_enabled": True,
            "auto_circadian_persona": True,
            "burnout_shield_alerts": True,
            "big3_morning_prompt": True
        }
        if not uid:
            return default_settings

        if self.is_live and self.client:
            doc_ref = self.client.collection("users").document(uid).collection("settings").document("main")
            doc = doc_ref.get()
            return {**default_settings, **(doc.to_dict() if doc.exists else {})}
        else:
            bucket = _get_memory_bucket(uid, "settings")
            return bucket.get("main", default_settings)

    def save_user_settings(self, uid: str, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        if not uid:
            raise ValueError("UID required")
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        current = self.get_user_settings(uid)
        merged = {**current, **settings_data, "uid": uid, "updated_at": now}
        if self.is_live and self.client:
            self.client.collection("users").document(uid).collection("settings").document("main").set(merged)
        else:
            bucket = _get_memory_bucket(uid, "settings")
            bucket["main"] = merged
        return merged

    def reset_user_sanctuary_data(self, uid: str) -> bool:
        """Purges all user tickets, journals, calendar, and profile data for data sovereignty."""
        if not uid:
            return False
        if self.is_live and self.client:
            user_ref = self.client.collection("users").document(uid)
            for col in ["journals", "tickets", "calendar", "insights"]:
                for doc in user_ref.collection(col).stream():
                    doc.reference.delete()
            user_ref.collection("profile").document("main").delete()
            user_ref.collection("settings").document("main").delete()
            return True
        else:
            if uid in _MEMORY_STORE:
                _MEMORY_STORE[uid] = {
                    "journals": {},
                    "insights": {},
                    "tickets": {},
                    "calendar": {},
                    "profile": {},
                    "settings": {}
                }
                return True
            return False

    # -------------------------------------------------------------------------
    # Emotional Insights History (/users/{uid}/insights)
    # -------------------------------------------------------------------------
    def save_emotional_insight(self, uid: str, insight: Dict[str, Any]) -> Dict[str, Any]:
        insight_id = insight.get("id") or f"insight_{uuid.uuid4().hex[:8]}"
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        data = {
            "id": insight_id,
            "uid": uid,
            "journal_id": insight.get("journal_id"),
            "sentiment_score": insight.get("sentiment_score", 0.0),
            "energy_score": insight.get("energy_score", 0.5),
            "clarity_score": insight.get("clarity_score", 0.5),
            "dominant_emotion": insight.get("dominant_emotion", "Calm"),
            "timestamp": now
        }
        if self.is_live and self.client:
            doc_ref = self.client.collection("users").document(uid).collection("insights").document(insight_id)
            doc_ref.set(data)
        else:
            bucket = _get_memory_bucket(uid, "insights")
            bucket[insight_id] = data
        return data

    def get_emotional_history(self, uid: str, limit: int = 30) -> List[Dict[str, Any]]:
        if not uid:
            return []
        if self.is_live and self.client:
            ref = (
                self.client.collection("users")
                .document(uid)
                .collection("insights")
                .order_by("timestamp", direction="ASCENDING")
                .limit(limit)
            )
            return [doc.to_dict() for doc in ref.stream()]
        else:
            bucket = _get_memory_bucket(uid, "insights")
            items = list(bucket.values())
            items.sort(key=lambda x: x.get("timestamp", ""))
            return items[-limit:]


# Global singleton instance
db_service = FirestoreService()
