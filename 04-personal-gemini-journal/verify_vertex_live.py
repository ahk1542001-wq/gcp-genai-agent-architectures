"""
Live Verification Script: Vertex AI Enterprise IAM Integration
Verifies that GeminiJournalService runs seamlessly on Vertex AI against intelligent-arc-488111-s0.
"""

import os
import sys
import json

# Force live AI execution
os.environ["FORCE_LIVE_AI"] = "true"
os.environ["USE_VERTEX_AI"] = "true"
os.environ["GCP_PROJECT_ID"] = "intelligent-arc-488111-s0"
os.environ["GEMINI_MODEL"] = "gemini-2.5-flash"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
if "GEMINI_API_KEY" in os.environ:
    del os.environ["GEMINI_API_KEY"]

from gemini_service import GeminiJournalService

def main():
    print("=" * 70)
    print("🚀 LIVE VERTEX AI VERIFICATION: intelligent-arc-488111-s0 (us-central1)")
    print("=" * 70)

    # 1. Initialize Service in Vertex AI mode
    svc = GeminiJournalService(use_vertex=True, project="intelligent-arc-488111-s0", location="us-central1")
    print(f"Active AI Engine: {svc.engine}")
    print(f"GCP Project:      {svc.project_id}")
    print(f"Vertex Region:    {svc.location}")
    print(f"Model Name:       {svc.model_name}")
    print(f"Client Type:      {type(svc.client).__name__}")
    assert svc.engine == "vertex_ai", f"Expected engine 'vertex_ai', got '{svc.engine}'"
    assert svc.client is not None, "Vertex AI client was not initialized!"
    print("  ✓ Service successfully bound to Vertex AI Enterprise IAM")

    # 2. Test Live Agent Turn (Conversational turn + Tool Action Proposal)
    print("\n" + "-" * 70)
    print("🧪 TEST 1: Live Conversational Turn with Autonomous Action Proposal")
    print("-" * 70)
    user_prompt = "ဒီနေ့အတွက် Cloud Run security audit လုပ်ဖို့ task အသစ်တစ်ခု ထည့်ပေးပါ။"
    history = [
        {"role": "user", "text": "မင်္ဂလာပါ Sanctuary Guardian"},
        {"role": "model", "text": "မင်္ဂလာပါခင်ဗျာ။ ဒီနေ့ ဘာတွေ ဆောင်ရွက်ဖို့ စီစဉ်ထားပါသလဲ?"}
    ]
    user_profile = {
        "name": "Victor",
        "primary_role": "Lead Cloud Architect",
        "active_goals": ["Win Hack2Skill APAC GenAI Hackathon"]
    }
    turn_res = svc.live_agent_turn(
        user_message=user_prompt,
        conversation_history=history,
        persona_mode="actionable",
        user_profile=user_profile
    )
    print("Live Turn Result:")
    print(json.dumps(turn_res, indent=2, ensure_ascii=False))

    assert "final_reply" in turn_res and len(turn_res["final_reply"]) > 0, "Missing final_reply!"
    assert "actions" in turn_res, "Missing actions list!"
    assert turn_res.get("detected_mode") in ("actionable", "coach", "balanced", "philosophy", "brainstorm"), f"Unexpected detected_mode: {turn_res.get('detected_mode')}"
    print("  ✓ Live agent turn successfully processed via Vertex AI!")

    # 3. Test Session Summarization (Structured JSON Synthesis)
    print("\n" + "-" * 70)
    print("🧪 TEST 2: Multi-Turn Session Summarization (Structured Takeaways)")
    print("-" * 70)
    sample_dialogue = [
        {"role": "user", "text": "I feel a huge sense of relief after verifying the Vertex AI dual-engine architecture."},
        {"role": "model", "text": "That is a significant architectural milestone. How does having both Vertex AI and Gemini API key empower your deployment?"},
        {"role": "user", "text": "It gives full enterprise flexibility. Judges can evaluate using either cloud IAM or their personal API Studio key without build halts."}
    ]
    summary_res = svc.summarize_session(sample_dialogue)
    print("Summarization Result:")
    print(json.dumps(summary_res, indent=2, ensure_ascii=False))

    assert "title" in summary_res and len(summary_res["title"]) > 0, "Missing title!"
    assert "summary" in summary_res and len(summary_res["summary"]) > 0, "Missing summary!"
    assert "breakthrough" in summary_res and len(summary_res["breakthrough"]) > 0, "Missing breakthrough!"
    assert "tags" in summary_res and isinstance(summary_res["tags"], list), "Missing tags!"
    print("  ✓ Session summarization successfully synthesized via Vertex AI!")

    # 4. Test Emotional Arc Analysis
    print("\n" + "-" * 70)
    print("🧪 TEST 3: Emotional & Cognitive Arc Visualizer via Vertex AI")
    print("-" * 70)
    arc_res = svc.analyze_emotional_arc(sample_dialogue)
    print("Emotional Arc Result:")
    print(json.dumps(arc_res, indent=2, ensure_ascii=False))
    assert "dominant_emotion" in arc_res, "Missing dominant_emotion!"
    assert "arc_progression" in arc_res, "Missing arc_progression!"
    print("  ✓ Emotional arc progression successfully analyzed via Vertex AI!")

    # 5. Test Pragmatic Action Items Distiller
    print("\n" + "-" * 70)
    print("🧪 TEST 4: Pragmatic Action Items Distiller via Vertex AI")
    print("-" * 70)
    journal_sample = (
        "Today was an intense sprint. We verified the dual-engine architecture for Vertex AI on Cloud Run. "
        "I need to finalize the README architecture guide tomorrow morning, review IAM role bindings for team members, "
        "and schedule a 15-minute shutdown ritual tonight to rest properly."
    )
    actions_res = svc.distill_action_items(journal_sample)
    print("Action Items Result:")
    print(json.dumps(actions_res, indent=2, ensure_ascii=False))
    assert isinstance(actions_res, list) and len(actions_res) > 0, "Expected non-empty actions list!"
    assert "task" in actions_res[0], "Missing 'task' field in action item!"
    print("  ✓ Action items distillation successfully synthesized via Vertex AI!")

    print("\n" + "=" * 70)
    print("✅ ALL LIVE VERTEX AI VERIFICATIONS PASSED 100% GREEN!")
    print("Project: intelligent-arc-488111-s0 | Region: us-central1 | Engine: Vertex AI")
    print("=" * 70)

if __name__ == "__main__":
    main()
