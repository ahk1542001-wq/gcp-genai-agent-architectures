"""
Cloud Firestore Database Layer for Personal Gemini Journal
Enforces strict tenant isolation (/users/{uid}/journals/{doc_id})
with zero cross-user leakage and fallback in-memory mock for local testing.
"""

import os
import uuid
import datetime
from typing import Optional, List, Dict, Any

GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "intelligent-arc-488111-s0")
USE_MOCK_DB = os.environ.get("USE_MOCK_DB", "false").lower() == "true"

# In-Memory tenant-partitioned store: {uid: {"journals": {id: doc}, "insights": {id: doc}}}
_MEMORY_STORE: Dict[str, Dict[str, Dict[str, Any]]] = {}

def _get_memory_bucket(uid: str, collection: str) -> Dict[str, Any]:
    if uid not in _MEMORY_STORE:
        _MEMORY_STORE[uid] = {"journals": {}, "insights": {}}
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

    def save_journal(self, uid: str, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Saves or updates a journal entry strictly under /users/{uid}/journals/{journal_id}.
        Zero cross-user leakage guaranteed by path scoping.
        """
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
        """
        Retrieves journal entries strictly for the authenticated user.
        """
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
        """
        Retrieves a single journal entry strictly from the user's isolated path.
        Returns None if not found or if attempting cross-tenant access.
        """
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
        """
        Deletes a journal entry strictly within the user's isolated collection.
        """
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

    def save_emotional_insight(self, uid: str, insight: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stores aggregated emotional progression data under /users/{uid}/insights/
        """
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
        """
        Returns recent emotional insights for rendering the Emotional Arc chart.
        """
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
