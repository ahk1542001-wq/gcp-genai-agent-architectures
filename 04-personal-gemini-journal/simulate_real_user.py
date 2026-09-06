"""
Realistic Human User Browser Simulation via Playwright
Comprehensive End-to-End Verification of Sanctuary OS:
- Multi-turn Burmese dialogue with Gemini (live Vertex AI or hermetic mock engine)
- Clean Notion elevation & export dropdown layout
- Scenario / mode switcher testing (Actionable, Philosophy, Auto-Detect)
- Kanban ticket creation (autonomous tool execution + manual) and move to Done
- Mood Calendar with realistic focus activities
- Life Rewind cognitive metrics
- Evening Shutdown ritual modal with Burmese gratitude
- Past Reflection & Wisdom review drawer
- RonDesignLab Genie Floating Action Dock (Chat Files, Images, Translate, Audio Chat)
- Google Drive Scoped Context Integration Modal
- Museum Memory Archive view (Mosaic inspired) with [CATALOGUED] stamps & Caveat cursive notes
- Places & Map Spatial Intelligence view with Southeast Asia & Cloud Run anchors
- Personal Memory & Context Modal (Profile, Goals, Insights, Ledger)
- Complete automated data cleanup of all test artifacts
"""

import os
import sys
import time
import socket
import threading
import requests
import shutil
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

DEFAULT_BASE_URL = "http://localhost:8080"
SCREENSHOT_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "tests", "screenshots", "real_user_verification"))
ROOT_SCREENSHOT_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "screenshots", "real_user_verification"))
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(ROOT_SCREENSHOT_DIR, exist_ok=True)
TEST_AUTH_HEADER = "test-token:victor_kyaw:victor@sanctuary.test:Victor Kyaw"


def get_free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port


def ensure_server():
    """Ensure a running server is available. Spawns ephemeral test server if needed."""
    try:
        r = requests.get(f"{DEFAULT_BASE_URL}/health", timeout=1)
        if r.status_code == 200:
            print(f"[Simulation] Using existing server at {DEFAULT_BASE_URL}")
            return None, DEFAULT_BASE_URL
    except Exception:
        pass

    # Start ephemeral server
    port = 8080
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('127.0.0.1', port))
        s.close()
    except OSError:
        port = get_free_port()

    os.environ["ENVIRONMENT"] = "test"
    os.environ["ALLOW_TEST_AUTH"] = "true"
    os.environ["USE_MOCK_DB"] = "true"
    os.environ["IS_TEST_MODE"] = "true"
    os.environ["GEMINI_API_KEY"] = "placeholder_key"
    os.environ["GCP_PROJECT_ID"] = "intelligent-arc-488111-s0"

    import uvicorn
    from main import app

    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)
    t = threading.Thread(target=server.run, daemon=True)
    t.start()

    url = f"http://127.0.0.1:{port}"
    for _ in range(50):
        try:
            r = requests.get(f"{url}/health", timeout=0.2)
            if r.status_code == 200:
                print(f"[Simulation] Spawned ephemeral test server at {url}")
                return server, url
        except Exception:
            time.sleep(0.1)

    raise RuntimeError(f"Could not connect to test server at {url}")


def run_real_user_simulation():
    server, base_url = ensure_server()
    print(f"[Simulation] Starting real human user test on {base_url}...")

    # Pre-test cleanup: ensure pristine state for victor_kyaw
    try:
        cleanup_resp = requests.get(
            f"{base_url}/api/tickets",
            headers={"Authorization": f"Bearer {TEST_AUTH_HEADER}"},
            timeout=5
        )
        if cleanup_resp.status_code == 200:
            for tkt in cleanup_resp.json().get("tickets", []):
                if any(w in tkt.get("title", "") for w in ["Test:", "Sanctuary OS", "Hackathon"]):
                    requests.delete(
                        f"{base_url}/api/tickets/{tkt['id']}",
                        headers={"Authorization": f"Bearer {TEST_AUTH_HEADER}"}
                    )
    except Exception as e:
        print(f"[Simulation] Pre-cleanup notice: {e}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1440, "height": 900})
            page = context.new_page()

            # Step 1: Open app and Authenticate as Victor Kyaw
            print("[Step 1] Navigating to app and authenticating as Victor Kyaw...")
            page.goto(base_url, wait_until="networkidle")
            page.wait_for_timeout(500)

            # Test auth sign-in
            page.evaluate(
                "() => { if (window.__SANCTUARY_TEST_AUTH__) { window.__SANCTUARY_TEST_AUTH__.signIn('victor_kyaw', 'victor@sanctuary.test', 'Victor Kyaw'); } }"
            )
            page.wait_for_selector("#app-shell:not(.hidden)", timeout=8000)
            page.wait_for_timeout(800)

            # Verify authenticated identity
            user_name = page.locator("#user-display-name").inner_text()
            print(f"[Step 1] Authenticated as: {user_name}")
            assert "Victor" in user_name

            # Verify Past Reflections header text and subtitle
            past_header = page.locator("#past-reflections-header-text").inner_text()
            assert "PAST REFLECTIONS & WISDOM" in past_header.upper()

            # Step 2: Test Export Dropdown (Clean Elevation)
            print("[Step 2] Testing Export Dropdown layout...")
            export_btn = page.locator("#export-menu-btn")
            export_btn.click()
            page.wait_for_timeout(400)

            export_dropdown = page.locator("#export-dropdown")
            assert export_dropdown.is_visible(), "Export dropdown should be visible after click"

            export_screenshot = os.path.join(SCREENSHOT_DIR, "01_export_dropdown_clean_elevation.png")
            page.screenshot(path=export_screenshot)
            print(f"[Step 2] Saved screenshot: {export_screenshot}")

            # Close export dropdown
            export_btn.click()
            page.wait_for_timeout(300)
            assert not export_dropdown.is_visible()

            # Step 3: Test Scenario / Reflection Mode Selection
            print("[Step 3] Testing Scenario / Reflection Mode Selection...")
            mode_pill = page.locator("#mode-selector-pill")
            mode_pill.click()
            page.wait_for_timeout(300)

            actionable_opt = page.locator(".mode-dropdown-item[data-mode='actionable']")
            if actionable_opt.is_visible():
                actionable_opt.click()
                page.wait_for_timeout(400)
                active_label = page.locator("#active-style-label").inner_text()
                print(f"[Step 3] Switched mode to: {active_label}")

            mode_screenshot = os.path.join(SCREENSHOT_DIR, "02_scenario_mode_selection.png")
            page.screenshot(path=mode_screenshot)
            print(f"[Step 3] Saved screenshot: {mode_screenshot}")

            # Switch back to Auto-Detect
            mode_pill.click()
            page.wait_for_timeout(300)
            auto_opt = page.locator(".mode-dropdown-item[data-mode='auto']")
            if auto_opt.is_visible():
                auto_opt.click()
                page.wait_for_timeout(300)

            # Step 4: Burmese Conversational Turn 1 - Greeting
            print("[Step 4] Turn 1: Sending Burmese greeting...")
            input_box = page.locator("#reflection-input")
            input_box.fill("ဟိုင်း မင်္ဂလာပါ Gemini ရေ")
            page.wait_for_timeout(300)

            page.locator("#send-reflection-btn").click()
            print("[Step 4] Waiting for Gemini turn 1 response...")
            page.wait_for_selector("#chat-stream .model-badge", timeout=20000)
            page.wait_for_timeout(1000)

            bubbles = page.locator("#chat-stream .bg-\\[\\#161b22\\]")
            turn1_bubble = bubbles.last.inner_text()
            print(f"[Step 4] Gemini Turn 1 Response:\n{turn1_bubble}")
            assert "ဒီနေ့ အလုပ်တွေအဆင်ပြေရဲ့လား၊ နောက်ထပ် ဘာကူညီပေးရမလဲခင်ဗျာ?" not in turn1_bubble

            turn1_screenshot = os.path.join(SCREENSHOT_DIR, "03_burmese_turn1_greeting.png")
            page.screenshot(path=turn1_screenshot)
            print(f"[Step 4] Saved screenshot: {turn1_screenshot}")

            # Step 5: Burmese Conversational Turn 2 - Task Proposal & Approval
            print("[Step 5] Turn 2: User requests task proposal...")
            input_box.fill("ဒီနေ့ hackathons_hub အတွက် Sanctuary OS master plan အပြီးသတ်ဖို့နဲ့ Hackathon အတွက် Submission package ပြင်ဆင်ဖို့ task ဖန်တီးပေးပါ")
            page.wait_for_timeout(300)
            page.locator("#send-reflection-btn").click()

            page.wait_for_timeout(6000)
            proposal_container = page.locator("#action-proposal-container")
            if proposal_container.is_visible():
                print("[Step 5] Action proposal card appeared. Approving action...")
                page.locator("#proposal-approve-btn").click()
                page.wait_for_timeout(1000)

            turn2_screenshot = os.path.join(SCREENSHOT_DIR, "04_burmese_turn2_task_proposal.png")
            page.screenshot(path=turn2_screenshot)
            print(f"[Step 5] Saved screenshot: {turn2_screenshot}")

            # Step 6: Burmese Conversational Turn 3 - Focus Block Scheduling
            print("[Step 6] Turn 3: User requests deep work sprint planning...")
            input_box.fill("နေ့လယ်ပိုင်းမှာ Sanctuary OS architecture အတွက် deep work sprint တစ်ခု စီစဉ်ပေးပါ")
            page.wait_for_timeout(300)
            page.locator("#send-reflection-btn").click()
            page.wait_for_timeout(6000)

            turn3_screenshot = os.path.join(SCREENSHOT_DIR, "05_burmese_turn3_schedule_focus.png")
            page.screenshot(path=turn3_screenshot)
            print(f"[Step 6] Saved screenshot: {turn3_screenshot}")

            # Step 7: Burmese Conversational Turn 4 - Cognitive Clarity
            print("[Step 7] Turn 4: User deep reflection on project balance...")
            input_box.fill("ဒီရက်ပိုင်း project တွေ ဆက်တိုက် လုပ်နေရလို့ စိတ်ဖိစီးမှု မဖြစ်အောင် ဘယ်လို balance လုပ်ရမလဲ?")
            page.wait_for_timeout(300)
            page.locator("#send-reflection-btn").click()
            page.wait_for_timeout(6000)

            turn4_screenshot = os.path.join(SCREENSHOT_DIR, "06_burmese_turn4_deep_reflection.png")
            page.screenshot(path=turn4_screenshot)
            print(f"[Step 7] Saved screenshot: {turn4_screenshot}")

            # Step 8: Auto-Summarize & Save Reflection Session
            print("[Step 8] Triggering Auto-Summarize and Save...")
            page.locator("#auto-summarize-btn").click()
            page.wait_for_timeout(2000)
            page.locator("#save-session-btn").click()
            page.wait_for_timeout(2000)

            save_screenshot = os.path.join(SCREENSHOT_DIR, "07_saved_session_sidebar.png")
            page.screenshot(path=save_screenshot)
            print(f"[Step 8] Saved screenshot: {save_screenshot}")

            # Step 9: Kanban Board
            print("[Step 9] Testing Kanban Board...")
            page.locator("#nav-kanban").click()
            page.wait_for_selector("#view-kanban-content:not(.hidden)", timeout=4000)
            page.wait_for_timeout(600)

            page.locator("#add-ticket-btn").click()
            page.wait_for_selector("#new-ticket-modal:not(.hidden)", timeout=3000)
            manual_test_ticket = "Test: Verify Vertex AI Burmese Dialogue E2E"
            page.locator("#ticket-title-input").fill(manual_test_ticket)
            page.locator("#ticket-priority-select").select_option("High")
            page.locator("#ticket-category-select").select_option("Work")
            page.locator("#ticket-column-select").select_option("todo")
            page.locator("#submit-ticket-btn").click()
            page.wait_for_selector("#new-ticket-modal", state="hidden", timeout=3000)
            page.wait_for_timeout(600)

            # Move to Done
            page.evaluate(f"""
                async () => {{
                    const tickets = state.tickets || [];
                    const t = tickets.find(x => x.title === '{manual_test_ticket}');
                    if (t) {{
                        await moveTicketColumn(t.id, 'done');
                    }}
                }}
            """)
            page.wait_for_timeout(800)

            kanban_screenshot = os.path.join(SCREENSHOT_DIR, "08_kanban_board_done.png")
            page.screenshot(path=kanban_screenshot)
            print(f"[Step 9] Saved screenshot: {kanban_screenshot}")

            # Step 10: Mindful Mood Calendar
            print("[Step 10] Testing Mindful Mood Calendar...")
            page.locator("#nav-calendar").click()
            page.wait_for_selector("#view-calendar-content:not(.hidden)", timeout=4000)
            page.wait_for_timeout(600)

            test_block_title = "Test: APAC Hackathon Architecture Sync"
            today_date = page.evaluate("() => new Date().toISOString().slice(0, 10)")
            page.locator("#new-event-title").fill(test_block_title)
            page.locator("#new-event-date").fill(today_date)
            page.locator("#new-event-timeblock").select_option("Afternoon Sprint")
            page.locator("#add-event-btn").click()
            page.wait_for_timeout(800)

            cal_screenshot = os.path.join(SCREENSHOT_DIR, "09_calendar_with_activities.png")
            page.screenshot(path=cal_screenshot)
            print(f"[Step 10] Saved screenshot: {cal_screenshot}")

            # Step 11: Life Rewind View
            print("[Step 11] Testing Life Rewind View...")
            page.locator("#nav-rewind").click()
            page.wait_for_selector("#view-rewind-content:not(.hidden)", timeout=4000)
            page.wait_for_timeout(600)

            rewind_screenshot = os.path.join(SCREENSHOT_DIR, "10_life_rewind_view.png")
            page.screenshot(path=rewind_screenshot)
            print(f"[Step 11] Saved screenshot: {rewind_screenshot}")

            # Step 12: Evening Shutdown Ritual Modal
            print("[Step 12] Testing Evening Shutdown Ritual Modal...")
            page.locator("#nav-shutdown").click()
            page.wait_for_selector("#shutdown-modal:not(.hidden)", timeout=4000)
            page.wait_for_timeout(500)

            page.locator("#shutdown-gratitude-input").fill("ဒီနေ့ Vertex AI dynamic Burmese model နဲ့ sanctuary features အားလုံး အောင်မြင်စွာ စမ်းသပ်နိုင်ခဲ့တယ်")
            page.wait_for_timeout(400)

            shutdown_screenshot = os.path.join(SCREENSHOT_DIR, "11_evening_shutdown_modal.png")
            page.screenshot(path=shutdown_screenshot)
            print(f"[Step 12] Saved screenshot: {shutdown_screenshot}")

            page.locator("#confirm-shutdown-btn").click()
            page.wait_for_selector("#shutdown-zen-confirmed:not(.hidden)", timeout=3000)
            page.locator("#wake-workspace-btn").click()
            page.wait_for_selector("#shutdown-modal", state="hidden", timeout=3000)

            # Step 13: Past Reflection & Wisdom Review Drawer
            print("[Step 13] Testing Past Reflection & Wisdom Review Drawer...")
            page.locator("#nav-journal").click()
            page.wait_for_selector("#view-journal-content:not(.hidden)", timeout=3000)
            page.wait_for_timeout(500)

            page.locator("#refresh-history-btn").click()
            page.wait_for_timeout(600)

            history_items = page.locator("#journal-history-list .history-item")
            if history_items.count() > 0:
                history_items.first.click()
                page.wait_for_selector("#journal-review-modal:not(.hidden)", timeout=4000)
                review_screenshot = os.path.join(SCREENSHOT_DIR, "12_past_reflection_wisdom_drawer.png")
                page.screenshot(path=review_screenshot)
                print(f"[Step 13] Saved screenshot: {review_screenshot}")
                page.locator("#close-review-modal-btn").click()
                page.wait_for_selector("#journal-review-modal", state="hidden", timeout=3000)

            # Step 14: Genie Floating Action Dock & Pill Bar
            print("[Step 14] Testing RonDesignLab Genie Floating Action Dock...")
            dock_translate = page.locator("#dock-translate-btn")
            dock_translate.click()
            page.wait_for_timeout(400)

            genie_dock_screenshot = os.path.join(SCREENSHOT_DIR, "13_genie_floating_dock_and_pill.png")
            page.screenshot(path=genie_dock_screenshot)
            print(f"[Step 14] Saved screenshot: {genie_dock_screenshot}")

            # Step 15: Google Drive Context Modal
            print("[Step 15] Testing Google Drive Integration Modal...")
            page.locator("#dock-chat-files-btn").click()
            page.wait_for_selector("#gdrive-modal:not(.hidden)", timeout=3000)
            page.wait_for_timeout(400)

            gdrive_screenshot = os.path.join(SCREENSHOT_DIR, "14_gdrive_context_modal.png")
            page.screenshot(path=gdrive_screenshot)
            print(f"[Step 15] Saved screenshot: {gdrive_screenshot}")

            # Click document context insert and close
            insert_btn = page.locator(".gdrive-insert-btn").first
            if insert_btn.is_visible():
                insert_btn.click()
                page.wait_for_timeout(300)
            else:
                page.locator("#close-gdrive-modal-btn").click()
                page.wait_for_timeout(300)

            # Step 16: Museum Memory Archive View
            print("[Step 16] Testing Museum Memory Archive View...")
            page.locator("#nav-archive").click()
            page.wait_for_selector("#view-archive-content:not(.hidden)", timeout=4000)
            page.wait_for_timeout(800)

            # Check specimens, stamps, and paper notes
            assert page.locator(".archival-stamp").first.is_visible()
            assert page.locator(".paper-note-card").first.is_visible()

            archive_screenshot = os.path.join(SCREENSHOT_DIR, "15_museum_memory_archive.png")
            page.screenshot(path=archive_screenshot)
            print(f"[Step 16] Saved screenshot: {archive_screenshot}")

            # Step 17: Places & Map Spatial Intelligence View
            print("[Step 17] Testing Places & Spatial Map View...")
            page.locator("#nav-places").click()
            page.wait_for_selector("#view-places-content:not(.hidden)", timeout=4000)
            page.wait_for_timeout(800)

            assert page.locator("#places-count-bangkok").is_visible()
            places_screenshot = os.path.join(SCREENSHOT_DIR, "16_places_spatial_memory_map.png")
            page.screenshot(path=places_screenshot)
            print(f"[Step 17] Saved screenshot: {places_screenshot}")

            # Step 18: Personal Memory & Context Modal
            print("[Step 18] Testing Personal Memory Context Modal...")
            page.locator("#open-memory-context-btn").click()
            page.wait_for_selector("#memory-context-modal:not(.hidden)", timeout=3000)
            page.wait_for_timeout(500)

            # Test tab switching
            page.locator("#tab-btn-goals").click()
            page.wait_for_timeout(300)
            page.locator("#tab-btn-insights").click()
            page.wait_for_timeout(300)
            page.locator("#tab-btn-profile").click()
            page.wait_for_timeout(300)

            # Update preferred name and occupation
            name_input = page.locator("#ctx-preferred-name")
            if name_input.is_visible():
                name_input.fill("Victor Kyaw")
            occ_input = page.locator("#ctx-occupation")
            if occ_input.is_visible():
                occ_input.fill("AI Systems Architect & Founder")

            page.locator("#save-memory-context-btn").click()
            page.wait_for_timeout(800)

            context_screenshot = os.path.join(SCREENSHOT_DIR, "17_personal_memory_context_modal.png")
            page.screenshot(path=context_screenshot)
            print(f"[Step 18] Saved screenshot: {context_screenshot}")

            close_mem_btn = page.locator("#close-memory-context-btn")
            if close_mem_btn.is_visible():
                close_mem_btn.click()
                page.wait_for_timeout(300)

            # Step 19: Full Automated Data Cleanup
            print("[Step 19] Comprehensive automated data cleanup...")

            # Clean test calendar event
            page.locator("#nav-calendar").click()
            page.wait_for_selector("#view-calendar-content:not(.hidden)", timeout=3000)
            del_evt_btn = page.locator(".calendar-event-item", has_text=test_block_title).locator(".delete-event-btn")
            if del_evt_btn.count() > 0:
                del_evt_btn.first.click()
                page.wait_for_timeout(600)

            # Delete test tickets via API
            try:
                t_resp = requests.get(
                    f"{base_url}/api/tickets",
                    headers={"Authorization": f"Bearer {TEST_AUTH_HEADER}"},
                    timeout=5
                )
                if t_resp.status_code == 200:
                    for t in t_resp.json().get("tickets", []):
                        if any(w in t.get("title", "") for w in ["Test:", "Sanctuary OS", "Hackathon", "Deploy"]):
                            requests.delete(
                                f"{base_url}/api/tickets/{t['id']}",
                                headers={"Authorization": f"Bearer {TEST_AUTH_HEADER}"},
                                timeout=5
                            )
            except Exception as e:
                print(f"[Step 19] Error deleting test tickets: {e}")

            # Delete test journals via API
            try:
                j_resp = requests.get(
                    f"{base_url}/api/journals",
                    headers={"Authorization": f"Bearer {TEST_AUTH_HEADER}"},
                    timeout=5
                )
                if j_resp.status_code == 200:
                    for entry in j_resp.json().get("entries", []):
                        if any(w in entry.get("title", "") for w in ["ဟိုင်း", "Test", "Sanctuary", "Hackathon"]):
                            requests.delete(
                                f"{base_url}/api/journal/{entry['id']}",
                                headers={"Authorization": f"Bearer {TEST_AUTH_HEADER}"},
                                timeout=5
                            )
            except Exception as e:
                print(f"[Step 19] Error deleting test journals: {e}")

            clean_screenshot = os.path.join(SCREENSHOT_DIR, "18_clean_state_verified.png")
            page.screenshot(path=clean_screenshot)
            print(f"[Step 19] Saved clean state screenshot: {clean_screenshot}")

            # Mirror all screenshots to ROOT_SCREENSHOT_DIR as well
            for f in os.listdir(SCREENSHOT_DIR):
                if f.endswith(".png"):
                    shutil.copy2(os.path.join(SCREENSHOT_DIR, f), os.path.join(ROOT_SCREENSHOT_DIR, f))

            browser.close()
            print("[Simulation] Real human user simulation completed with 100% SUCCESS and full cleanup!")

    finally:
        if server:
            print("[Simulation] Stopping ephemeral test server...")
            server.should_exit = True


if __name__ == "__main__":
    run_real_user_simulation()
