import os
import sys

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import time
import socket
import threading
import uvicorn
import pytest
from playwright.sync_api import sync_playwright

# Set up hermetic test environment before importing app
os.environ["ENVIRONMENT"] = "test"
os.environ["ALLOW_TEST_AUTH"] = "true"
os.environ["USE_MOCK_DB"] = "true"
os.environ["SECRET_MANAGER_PROJECT_ID"] = "test-project"
os.environ["GEMINI_API_KEY"] = "placeholder_key"
os.environ["IS_TEST_MODE"] = "true"

def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

TEST_PORT = get_free_port()
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"

@pytest.fixture(scope="session", autouse=True)
def run_test_server():
    """Spins up the FastAPI server in a background thread for end-to-end browser testing."""
    from main import app
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=TEST_PORT, log_level="error"))
    t = threading.Thread(target=server.run, daemon=True)
    t.start()
    
    # Wait for server to be responsive
    for _ in range(50):
        try:
            with socket.create_connection(("127.0.0.1", TEST_PORT), timeout=0.2):
                break
        except OSError:
            time.sleep(0.1)
    yield
    server.should_exit = True

def goto_authenticated(page, name="Alice"):
    """Loads Sanctuary OS and authenticates via hermetic test adapter."""
    page.goto(BASE_URL, wait_until="networkidle")
    page.evaluate(f"() => {{ if (window.__SANCTUARY_TEST_AUTH__) {{ window.__SANCTUARY_TEST_AUTH__.signIn('test_user', 'user@test.local', '{name}'); }} }}")
    page.wait_for_selector("#app-shell:not(.hidden)", timeout=5000)

def test_browser_ui_shell_and_navigation():
    """Verify Notion shell loading, persona switching, and view toggling with zero console errors."""
    console_errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        # 1. Load the Sanctuary OS SPA
        goto_authenticated(page)
        page.wait_for_timeout(300)

        # 2. Verify Title & Core Brand Header
        assert "Personal Gemini Life Guardian" in page.title()
        brand = page.locator("#app-shell").get_by_text("Sanctuary OS").first
        assert brand.is_visible()

        # 3. Verify Unified Guardian Sanctuary Callout
        callout_title = page.locator("#callout-title").text_content()
        assert "Guardian" in callout_title

        # 4. Verify View Navigation (Kanban, Calendar, Rewind)
        kanban_nav = page.locator("#nav-kanban")
        kanban_nav.click()
        page.wait_for_timeout(300)
        assert page.locator("#view-kanban-content").is_visible()
        assert page.locator("text=Execution Board").first.is_visible()

        calendar_nav = page.locator("#nav-calendar")
        calendar_nav.click()
        page.wait_for_timeout(300)
        assert page.locator("#view-calendar-content").is_visible()

        rewind_nav = page.locator("#nav-rewind")
        rewind_nav.click()
        page.wait_for_timeout(300)
        assert page.locator("#view-rewind-content").is_visible()

        # 5. Return to Journal View
        journal_nav = page.locator("#nav-journal")
        journal_nav.click()
        page.wait_for_timeout(300)
        assert page.locator("#view-journal-content").is_visible()

        browser.close()

    # Verify zero fatal JS console errors occurred
    assert len(console_errors) == 0, f"Unexpected browser console errors: {console_errors}"

def test_browser_ui_settings_modal_and_toggles():
    """Verify Settings Modal interaction, all toggle states, language switch, schedule inputs, and save flow."""
    console_errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        # Handle settings save alert dialog
        page.on("dialog", lambda d: d.accept())

        goto_authenticated(page)

        # 1. Open Settings Modal via Header Button
        settings_btn = page.locator("#open-settings-btn")
        settings_btn.click()
        page.wait_for_timeout(300)

        modal = page.locator("#settings-modal")
        assert modal.is_visible()

        # 2. Check and toggle audio switches
        voice_toggle = page.locator("#setting-voice-enabled")
        assert voice_toggle.is_visible()
        voice_toggle.click()

        tibetan_toggle = page.locator("#setting-tibetan-sound")
        assert tibetan_toggle.is_visible()
        tibetan_toggle.click()

        # 3. Check and toggle notification switches
        mac_notifs = page.locator("#setting-mac-notifications")
        assert mac_notifs.is_visible()
        mac_notifs.click()

        hotkey_toggle = page.locator("#setting-hotkey-enabled")
        assert hotkey_toggle.is_visible()
        hotkey_toggle.click()

        circadian_toggle = page.locator("#setting-circadian-enabled")
        assert circadian_toggle.is_visible()
        circadian_toggle.click()

        burnout_toggle = page.locator("#setting-burnout-alerts")
        assert burnout_toggle.is_visible()
        burnout_toggle.click()

        # 4. Change UI Language select
        lang_select = page.locator("#setting-ui-language")
        assert lang_select.is_visible()
        lang_select.select_option("my")
        lang_select.select_option("en")

        # 5. Fill Morning and Evening Circadian Schedule inputs
        morning_time = page.locator("#setting-morning-time")
        assert morning_time.is_visible()
        morning_time.fill("07:30")

        evening_time = page.locator("#setting-evening-time")
        assert evening_time.is_visible()
        evening_time.fill("19:00")

        # 6. Save Preferences and verify modal dismisses
        save_btn = page.locator("#save-settings-btn")
        save_btn.click()
        page.wait_for_timeout(500)
        assert not modal.is_visible()

        # 7. Test opening via sidebar settings button and closing via close button
        page.locator("#open-settings-sidebar-btn").click()
        page.wait_for_timeout(200)
        assert modal.is_visible()
        page.locator("#close-settings-btn").click()
        page.wait_for_timeout(200)
        assert not modal.is_visible()

        # 8. Test opening via bottom settings button
        page.locator("#open-settings-bottom-btn").click()
        page.wait_for_timeout(200)
        assert modal.is_visible()
        page.locator("#close-settings-btn").click()
        page.wait_for_timeout(200)
        assert not modal.is_visible()

        browser.close()

    assert len(console_errors) == 0

def test_browser_ui_kanban_card_creation():
    """Verify Kanban board renders cards, handles new card creation, and deletion."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        goto_authenticated(page)

        # Navigate to Kanban
        page.locator("#nav-kanban").click()
        page.wait_for_timeout(300)

        # Columns exist
        assert page.locator("#column-todo").is_visible()
        assert page.locator("#column-in-progress").is_visible()
        assert page.locator("#column-done").is_visible()

        # Handle dialog prompt for creating ticket
        page.on("dialog", lambda d: d.accept("Verify Security Boundary Component"))
        page.locator("#add-ticket-btn").click()
        page.wait_for_timeout(500)

        # Verify card rendered in column-todo
        card = page.locator("#column-todo .kanban-card", has_text="Verify Security Boundary Component").first
        assert card.is_visible()

        # Delete card
        del_btn = card.locator(".delete-ticket-btn")
        del_btn.click()
        page.wait_for_timeout(500)
        assert page.locator("#column-todo .kanban-card", has_text="Verify Security Boundary Component").count() == 0

        browser.close()

def test_browser_ui_language_toggle_burmese():
    """Verify UI Language Toggle switches DOM labels to Burmese."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        goto_authenticated(page)

        # Open Settings Modal
        page.locator("#open-settings-btn").click()
        page.wait_for_timeout(200)

        # Select Burmese
        lang_select = page.locator("#setting-ui-language")
        lang_select.select_option("my")
        page.wait_for_timeout(200)

        # Save settings
        page.locator("#save-settings-btn").click()
        page.wait_for_timeout(300)

        # Verify Burmese label in navigation
        burmese_journal = page.locator("text=စိတ်ငြိမ်းချမ်းရာ ဂျာနယ်").first
        assert burmese_journal.is_visible()

        # Switch back to English
        page.locator("#open-settings-btn").click()
        page.wait_for_timeout(200)
        page.locator("#setting-ui-language").select_option("en")
        page.locator("#save-settings-btn").click()
        page.wait_for_timeout(300)

        assert page.locator("text=Sanctuary Journal").first.is_visible()

        browser.close()

def test_browser_ui_export_dropdown_and_options():
    """Verify Export dropdown exposes Markdown, Plain text, and PDF print options."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        goto_authenticated(page)

        # Click Export Menu button
        export_btn = page.locator("#export-menu-btn")
        export_btn.click()
        page.wait_for_timeout(200)

        # Verify dropdown options are visible
        assert page.locator("#export-md-btn").is_visible()
        assert page.locator("#export-txt-btn").is_visible()
        assert page.locator("#export-pdf-btn").is_visible()

        browser.close()

def test_browser_ui_offline_draft_preservation():
    """Verify LocalStorage hybrid auto-save restores unsubmitted draft upon reload."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        goto_authenticated(page)

        # Type draft in reflection input
        draft_text = "Late night reflection: Finished the Playwright tests and feeling proud."
        textarea = page.locator("#reflection-input")
        textarea.fill(draft_text)
        page.wait_for_timeout(200)

        # Reload the page
        page.reload(wait_until="networkidle")
        page.wait_for_timeout(300)

        # Verify draft was restored from LocalStorage
        restored_value = page.locator("#reflection-input").input_value()
        assert restored_value == draft_text

        browser.close()

def test_browser_ui_voice_assistant_button_toggle():
    """Verify Start Live Voice button toggles to Stop Voice and activates soundwave."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        goto_authenticated(page)

        voice_btn = page.locator("#live-voice-toggle-btn")
        assert "Start Live Voice" in voice_btn.text_content()

        # Click Start Voice
        voice_btn.click()
        page.wait_for_timeout(200)
        assert "Stop Voice" in voice_btn.text_content()
        assert page.locator("#soundwave-bar").is_visible()

        # Click Stop Voice
        voice_btn.click()
        page.wait_for_timeout(200)
        assert "Start Live Voice" in voice_btn.text_content()

        browser.close()

def test_browser_ui_add_ticket_button_modal_prompt():
    """Verify + New Ticket button opens dialog prompt and creates card in To Do column."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        goto_authenticated(page)

        # Switch to Kanban view
        page.locator("#nav-kanban").click()
        page.wait_for_timeout(200)

        # Handle browser prompt dialog
        page.on("dialog", lambda d: d.accept("Build APAC GenAI Demo Ticket"))

        # Click + New Ticket
        page.locator("#add-ticket-btn").click()
        page.wait_for_timeout(500)

        # Verify card rendered in column-todo
        card = page.locator("#column-todo .kanban-card").first
        assert card.is_visible()
        assert "Build APAC GenAI Demo Ticket" in card.text_content()

        browser.close()

def test_browser_ui_clear_and_reflect_buttons():
    """Verify Clear button empties input and Reflect ➔ button submits and displays message."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        goto_authenticated(page)

        textarea = page.locator("#reflection-input")
        clear_btn = page.locator("#clear-input-btn")
        send_btn = page.locator("#send-reflection-btn")

        # Test Clear Button
        textarea.fill("Draft text that must be cleared")
        page.wait_for_timeout(100)
        clear_btn.click()
        page.wait_for_timeout(100)
        assert textarea.input_value() == ""

        # Test Send Reflection Button
        test_msg = "Completed Playwright browser test suite with deep verification"
        textarea.fill(test_msg)
        send_btn.click()
        page.wait_for_timeout(1200)

        # Verify user message appears in chat-stream
        chat_stream = page.locator("#chat-stream")
        assert test_msg in chat_stream.text_content()

        browser.close()

def test_browser_sidebar_clean_executive_navigation_no_kid_gimmicks():
    """Verify mature executive sidebar: clean pillars present, kid breathing gimmick removed."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        goto_authenticated(page)

        # 1. Executive pillars must be visible
        assert page.locator("#nav-journal").is_visible()
        assert page.locator("#nav-kanban").is_visible()
        assert page.locator("#nav-calendar").is_visible()
        assert page.locator("#nav-rewind").is_visible()
        assert page.locator("#nav-shutdown").is_visible()

        # 2. Kid breathing gimmick and modal must NOT exist in the DOM
        assert page.locator("#nav-destress").count() == 0, "Kid breathing button must not exist in executive sidebar"
        assert page.locator("#breathing-modal").count() == 0, "Breathing circle modal must be removed"

        browser.close()

def test_browser_ui_shutdown_ritual_modal():
    """Verify Evening Shutdown button opens ritual modal, confirm ritual, wake workspace, and cancel."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        goto_authenticated(page)

        # 1. Click Evening Shutdown in sidebar
        page.locator("#nav-shutdown").click()
        page.wait_for_timeout(200)

        modal = page.locator("#shutdown-modal")
        assert modal.is_visible()
        assert "Evening Shutdown Sanctuary" in modal.text_content()

        # 2. Confirm shutdown ritual
        confirm_btn = page.locator("#confirm-shutdown-btn")
        assert confirm_btn.is_visible()
        confirm_btn.click()
        page.wait_for_timeout(200)

        assert "Gratitude saved" in page.locator("#shutdown-gratitude-prompt").text_content()
        assert page.locator("#shutdown-zen-confirmed").is_visible()
        assert not confirm_btn.is_visible()

        # 3. Wake workspace back up
        wake_btn = page.locator("#wake-workspace-btn")
        assert wake_btn.is_visible()
        wake_btn.click()
        page.wait_for_timeout(200)
        assert not modal.is_visible()

        # 4. Reopen and test cancel button
        page.locator("#nav-shutdown").click()
        page.wait_for_timeout(200)
        assert modal.is_visible()
        page.locator("#cancel-shutdown-btn").click()
        page.wait_for_timeout(200)
        assert not modal.is_visible()

        browser.close()


# ==============================================================================
# Phase 2 RED Tests: Real Firebase Sign-In, Session UX & Secret Absence
# ==============================================================================

def test_browser_unauthenticated_landing_state():
    """
    RED TEST: Fresh visitor must see unauthenticated landing state with:
    - #auth-landing visible, #app-shell hidden
    - Google sign-in CTA, product promise & privacy note
    - Zero previous owner email or test token in loaded page/source
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto(BASE_URL, wait_until="networkidle")
        page.wait_for_timeout(300)

        # 1. Landing state must be visible
        landing = page.locator("#auth-landing")
        assert landing.is_visible(), "Expected #auth-landing to be visible for unauthenticated user"

        # 2. Main app shell must be hidden
        app_shell = page.locator("#app-shell")
        assert not app_shell.is_visible(), "Expected #app-shell to be hidden before sign-in"

        # 3. Google Sign-In button must be present
        signin_btn = page.locator("#google-signin-btn")
        assert signin_btn.is_visible(), "Expected #google-signin-btn to be visible"

        # 4. Zero hardcoded owner identity or tokens in loaded source or text
        content = page.content().lower()
        assert "victor.job154@gmail.com" not in content, "Owner personal email leaked in frontend source/DOM!"
        assert "test-token:victor_kyaw" not in content, "Hardcoded identity token found in frontend source/DOM!"

        browser.close()


def test_browser_authenticated_app_reveal_and_signout():
    """
    RED TEST: Signing in reveals the application shell with user identity,
    and clicking Sign Out returns to the landing screen.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto(BASE_URL, wait_until="networkidle")
        page.wait_for_timeout(300)

        # Sign in through hermetic test auth adapter
        page.evaluate("window.__SANCTUARY_TEST_AUTH__ && window.__SANCTUARY_TEST_AUTH__.signIn('alice_1', 'alice@test.com', 'Alice')")
        page.wait_for_timeout(300)

        # App shell must now be visible, landing hidden
        assert page.locator("#app-shell").is_visible(), "Expected #app-shell to be visible after sign-in"
        assert not page.locator("#auth-landing").is_visible(), "Expected #auth-landing to be hidden after sign-in"

        # User identity must be displayed
        user_name = page.locator("#user-display-name").text_content()
        assert "Alice" in user_name

        # Sign Out button must be present and functional
        signout_btn = page.locator("#signout-btn")
        assert signout_btn.is_visible(), "Expected #signout-btn to be visible"
        signout_btn.click()
        page.wait_for_timeout(300)

        # After sign-out, return to landing state
        assert page.locator("#auth-landing").is_visible(), "Expected #auth-landing to be visible after sign-out"
        assert not page.locator("#app-shell").is_visible(), "Expected #app-shell to be hidden after sign-out"

        browser.close()


def test_hermetic_test_auth_adapter_security_gate():
    """
    SECURITY GATE: When auth_mode is 'firebase', the test adapter window.__SANCTUARY_TEST_AUTH__
    must be strictly undefined/unreachable in client context.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Intercept /api/public-config to simulate production Firebase mode
        page.route("**/api/public-config", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"auth_mode": "firebase", "environment": "production", "firebase": {"apiKey": "fake_public_key", "projectId": "intelligent-arc-488111-s0"}}'
        ))

        page.goto(BASE_URL, wait_until="networkidle")
        page.wait_for_timeout(300)

        adapter_exists = page.evaluate("typeof window.__SANCTUARY_TEST_AUTH__ !== 'undefined'")
        assert not adapter_exists, "Security Gate Violation: Test auth adapter is exposed in Firebase auth mode!"

        # Test auth helper section must not be visible
        test_section = page.locator("#test-auth-section")
        assert not test_section.is_visible()

        browser.close()


def test_browser_action_proposal_approval_and_dismissal_flow():
    """
    Verify Human-in-the-Loop approval:
    1. Agent returns proposed action (not auto-executed)
    2. Proposal card appears with Approve and Dismiss buttons
    3. User clicks Approve -> action executes -> feedback displayed -> card clears
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Intercept /api/agent/live-turn to propose a ticket creation
        page.route("**/api/agent/live-turn", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({
                "spoken_ack": "I propose creating a task for you.",
                "final_reply": "Should I schedule this in your To Do board?",
                "proposed_actions": [{
                    "tool": "create_ticket",
                    "params": {
                        "title": "Verified Action Approval Task",
                        "priority": "High",
                        "category": "Work",
                        "column": "todo"
                    }
                }],
                "ui_actions": [],
                "sentiment": 0.8,
                "detected_mode": "coach",
                "tickets": []
            })
        ))

        goto_authenticated(page)

        # Trigger reflection turn
        page.locator("#reflection-input").fill("Propose a new task for me")
        page.locator("#send-reflection-btn").click()
        page.wait_for_timeout(500)

        # Action proposal card must become visible
        proposal_container = page.locator("#action-proposal-container")
        assert proposal_container.is_visible()
        desc = page.locator("#proposal-description").text_content()
        assert "Verified Action Approval Task" in desc

        # Click Approve
        approve_btn = page.locator("#proposal-approve-btn")
        assert approve_btn.is_visible()
        approve_btn.click()

        # Feedback should appear
        page.wait_for_timeout(400)
        feedback = page.locator("#proposal-feedback")
        assert feedback.is_visible()
        assert "approved" in feedback.text_content().lower()

        # After brief moment, container should disappear (queue drained)
        page.wait_for_timeout(1200)
        assert not proposal_container.is_visible()

        # 2. Test Dismiss flow: trigger another proposal and click Dismiss
        confirm_called = []
        page.route("**/api/agent/actions/confirm", lambda route: (confirm_called.append(True), route.continue_()))

        page.locator("#reflection-input").fill("Propose second task")
        page.locator("#send-reflection-btn").click()
        page.wait_for_timeout(500)

        assert proposal_container.is_visible()
        dismiss_btn = page.locator("#proposal-dismiss-btn")
        assert dismiss_btn.is_visible()
        dismiss_btn.click()
        page.wait_for_timeout(300)

        # Card must be dismissed immediately without calling /api/agent/actions/confirm
        assert not proposal_container.is_visible()
        assert len(confirm_called) == 0, "Dismiss must NOT trigger any confirmation API write!"

        browser.close()


def test_browser_rewind_empty_state_and_no_fake_metrics():
    """
    RED TEST: Rewind view renders genuine user metrics or clean empty state.
    Must never render '100% Streak' or 'Found emotional stability during hackathon crunch'
    or random mood badges.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Mock empty rewind response
        page.route("**/api/rewind", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({
                "total_entries": 0,
                "total_words": 0,
                "streak_days": 0,
                "completed_tickets": 0,
                "open_tickets": 0,
                "living_memories_count": 0,
                "recent_tags": [],
                "recent_reflections": []
            })
        ))

        goto_authenticated(page)

        # Navigate to Rewind
        page.locator("#nav-rewind").click()
        page.wait_for_timeout(400)

        content = page.content()
        # Verify no hardcoded mock text exists
        assert "100% Streak" not in content
        assert "Found emotional stability during hackathon crunch" not in content
        assert "Mastered enterprise multi-tenant Firestore security" not in content

        # Verify clean empty state is visible
        empty_el = page.locator("#rewind-empty-state")
        assert empty_el.is_visible()
        assert "begins with your first reflection" in empty_el.text_content()

        browser.close()


def test_browser_rewind_genuine_metrics():
    """
    RED TEST: Rewind view accurately presents calculated real metrics from /api/rewind.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.route("**/api/rewind", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({
                "total_entries": 7,
                "total_words": 1420,
                "streak_days": 5,
                "completed_tickets": 12,
                "open_tickets": 3,
                "living_memories_count": 4,
                "recent_tags": ["wellness", "focus"],
                "recent_reflections": [
                    {"id": "r1", "title": "First Step", "date": "2026-09-01", "excerpt": "Clear mind"}
                ]
            })
        ))

        goto_authenticated(page)

        page.locator("#nav-rewind").click()
        page.wait_for_timeout(400)

        # Check genuine metric elements
        assert page.locator("#rewind-total-entries").text_content() == "7"
        assert page.locator("#rewind-total-words").text_content() == "1420"
        assert page.locator("#rewind-streak-days").text_content() == "5"
        assert page.locator("#rewind-completed-tickets").text_content() == "12"

        browser.close()


def test_browser_calendar_crud_and_empty_state():
    """
    RED TEST: Calendar supports adding focus events for a date/time block,
    viewing events, and deleting events with immediate DOM updates.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        goto_authenticated(page)

        page.locator("#nav-calendar").click()
        page.wait_for_timeout(400)

        # Calendar view must have an event list / management container
        assert page.locator("#calendar-events-section").is_visible()

        # Add event
        page.locator("#new-event-title").fill("Deep Architecture Focus")
        page.locator("#new-event-date").fill("2026-09-04")
        page.locator("#new-event-timeblock").select_option("Morning Focus")
        page.locator("#add-event-btn").click()
        page.wait_for_timeout(500)

        # Verify event appears in list
        event_item = page.locator(".calendar-event-item", has_text="Deep Architecture Focus").first
        assert event_item.is_visible()

        # Delete event
        event_item.locator(".delete-event-btn").click()
        page.wait_for_timeout(500)

        # Verify deleted
        assert not page.locator(".calendar-event-item", has_text="Deep Architecture Focus").is_visible()

        browser.close()


def test_browser_api_fetch_401_session_expiry_preserves_draft():
    """
    RED TEST: When any authenticated API call fails with 401 Unauthorized,
    the app transitions safely to the signed-out state without losing unsaved draft text.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        goto_authenticated(page)

        # User writes a valuable draft
        draft_content = "Crucial uncommitted ideas: building the APAC GenAI Sanctuary."
        textarea = page.locator("#reflection-input")
        textarea.fill(draft_content)
        page.wait_for_timeout(200)

        # Trigger an API call that returns 401 (e.g. simulated session expired on saving journal)
        page.route("**/api/agent/live-turn", lambda route: route.fulfill(
            status=401,
            content_type="application/json",
            body='{"detail": "Session expired or invalid credentials."}'
        ))

        page.locator("#send-reflection-btn").click()
        page.wait_for_timeout(500)

        # Must transition to auth landing screen with explanatory banner
        assert page.locator("#auth-landing").is_visible(), "Expected app to show auth landing on 401"
        assert not page.locator("#app-shell").is_visible(), "Expected app shell to hide on 401"

        # Draft must be preserved in LocalStorage
        saved_draft = page.evaluate("localStorage.getItem('journal_draft')")
        assert saved_draft == draft_content, "Draft was lost upon 401 session expiry!"

        browser.close()


def test_browser_responsive_mobile_390x844_layout_and_touch_targets():
    """
    RED TEST: Mobile 390x844 viewport:
    - Mobile bottom navigation bar is visible with 4 Sanctuary Loop tabs.
    - Sidebar is hidden.
    - Touch targets are at least 44x44px.
    - No horizontal scroll overflow exists.
    - Mobile nav buttons switch views seamlessly.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 390, "height": 844})

        goto_authenticated(page)

        # 1. Mobile bottom nav must be visible
        bottom_nav = page.locator("#mobile-bottom-nav")
        assert bottom_nav.is_visible(), "Mobile bottom nav must be visible on 390px viewport"

        # 2. Main desktop sidebar must be hidden
        sidebar = page.locator("#main-sidebar")
        assert not sidebar.is_visible(), "Desktop sidebar must be hidden on mobile viewport"

        # 3. Touch target sizes for mobile navigation buttons must be >= 44x44px
        for btn_id in ["#mobile-nav-journal", "#mobile-nav-kanban", "#mobile-nav-calendar", "#mobile-nav-rewind"]:
            btn = page.locator(btn_id)
            assert btn.is_visible()
            box = btn.bounding_box()
            assert box is not None
            assert box["height"] >= 44, f"{btn_id} touch height must be >= 44px, got {box['height']}"
            assert box["width"] >= 44, f"{btn_id} touch width must be >= 44px, got {box['width']}"

        # 4. Zero horizontal overflow
        no_overflow = page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        assert no_overflow, "Horizontal overflow detected on mobile viewport!"

        # 5. Mobile nav switching works across all tabs
        page.locator("#mobile-nav-kanban").click()
        page.wait_for_timeout(200)
        assert page.locator("#view-kanban-content").is_visible()
        assert not page.locator("#view-journal-content").is_visible()

        page.locator("#mobile-nav-calendar").click()
        page.wait_for_timeout(200)
        assert page.locator("#view-calendar-content").is_visible()
        assert not page.locator("#view-kanban-content").is_visible()

        page.locator("#mobile-nav-rewind").click()
        page.wait_for_timeout(200)
        assert page.locator("#view-rewind-content").is_visible()
        assert not page.locator("#view-calendar-content").is_visible()

        page.locator("#mobile-nav-journal").click()
        page.wait_for_timeout(200)
        assert page.locator("#view-journal-content").is_visible()
        assert not page.locator("#view-rewind-content").is_visible()

        browser.close()


def test_browser_responsive_desktop_1440x900_sidebar_and_collapse():
    """
    RED TEST: Desktop 1440x900 viewport:
    - Mobile bottom nav is hidden.
    - Main sidebar is visible and collapsible via #sidebar-toggle-btn.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        goto_authenticated(page)

        # 1. Mobile bottom nav must be hidden
        assert not page.locator("#mobile-bottom-nav").is_visible(), "Mobile bottom nav must be hidden on desktop"

        # 2. Desktop sidebar must be visible
        sidebar = page.locator("#main-sidebar")
        assert sidebar.is_visible(), "Desktop sidebar must be visible on 1440px desktop"

        # 3. Sidebar toggle button collapses and expands sidebar
        toggle_btn = page.locator("#sidebar-toggle-btn")
        assert toggle_btn.is_visible()

        # Click to collapse
        toggle_btn.click()
        page.wait_for_timeout(300)
        assert not sidebar.is_visible()

        # Click to expand
        toggle_btn.click()
        page.wait_for_timeout(300)
        assert sidebar.is_visible()

        browser.close()


def test_browser_dynamic_history_and_review_drawer():
    """
    Verify dynamic past reflections list rendering (with zero hardcoding)
    and review drawer modal interaction.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})

        goto_authenticated(page, name="HistoryTester")

        # 1. Past reflections container exists
        history_list = page.locator("#journal-history-list")
        assert history_list.is_visible()

        # 2. Hardcoded mock entries ("Cloud Run Security & Deployment") must NOT exist
        assert "Cloud Run Security & Deployment" not in history_list.inner_text()

        # 3. Create a real journal entry via API so dynamic history displays it
        page.evaluate("""
            async () => {
                await fetch('/api/journal/save', {
                    method: 'POST',
                    headers: {
                        'Authorization': 'Bearer ' + localStorage.getItem('journal_token'),
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        title: 'Playwright Dynamic Journal 101',
                        content: 'Reflecting on zero-hardcode architecture in Cloud Run.',
                        conversation: [{role: 'user', text: 'How do I scale to zero?'}],
                        action_items: [{title: 'Deploy to Cloud Run with labels'}]
                    })
                });
            }
        """)

        # 4. Refresh history list
        page.locator("#refresh-history-btn").click()
        page.wait_for_timeout(500)

        # 5. Entry should now appear in the sidebar
        entry_item = page.locator("#journal-history-list .history-item", has_text="Playwright Dynamic Journal 101")
        assert entry_item.is_visible()

        # 6. Clicking entry opens Review Drawer
        entry_item.click()
        review_modal = page.locator("#journal-review-modal")
        page.wait_for_selector("#journal-review-modal", state="visible", timeout=5000)
        assert review_modal.is_visible()
        assert "Playwright Dynamic Journal 101" in page.locator("#review-modal-title").inner_text()

        # 7. Close review drawer
        page.locator("#close-review-modal-btn").click()
        page.wait_for_selector("#journal-review-modal", state="hidden", timeout=5000)
        assert not review_modal.is_visible()

        browser.close()


def test_browser_executive_data_report_modal():
    """
    Verify Executive Cognitive & Productivity Data Report modal:
    - Button opens modal
    - Loads authentic metrics (word count, done tasks, focus blocks, burnout risk, learned rules)
    - Action buttons exist (Download Markdown, Print/PDF)
    - Modal can be closed
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})

        goto_authenticated(page, name="ExecutiveUser")

        # 1. Click Executive Report button
        report_btn = page.locator("#executive-report-btn")
        assert report_btn.is_visible()
        report_btn.click()

        # 2. Modal appears
        report_modal = page.locator("#executive-report-modal")
        page.wait_for_selector("#executive-report-modal", state="visible", timeout=5000)
        assert report_modal.is_visible()

        # 3. KPI values and sections are rendered
        word_count = page.locator("#report-word-count")
        done_tasks = page.locator("#report-done-tasks")
        focus_blocks = page.locator("#report-focus-blocks")
        burnout_risk = page.locator("#report-burnout-risk")
        rules_count = page.locator("#report-rules-count")

        assert word_count.is_visible()
        assert done_tasks.is_visible()
        assert focus_blocks.is_visible()
        assert burnout_risk.is_visible()
        assert rules_count.is_visible()

        assert int(word_count.inner_text().replace(",", "")) >= 0
        assert int(done_tasks.inner_text().replace(",", "")) >= 0
        assert int(focus_blocks.inner_text().replace(",", "")) >= 0

        # 4. Action buttons are present and clickable
        download_btn = page.locator("#download-report-md-btn")
        print_btn = page.locator("#print-report-btn")
        assert download_btn.is_visible()
        assert print_btn.is_visible()

        # 5. Close modal
        page.locator("#close-executive-report-btn").click()
        page.wait_for_selector("#executive-report-modal", state="hidden", timeout=5000)
        assert not report_modal.is_visible()

        browser.close()


def test_browser_dynamic_emotional_arc_zero_state_and_live_update():
    """
    Verify Cognitive & Emotional Arc zero-state and live dynamic update:
    - Fresh session displays authentic empty state (no fake lines/points).
    - Canvas wrapper is hidden, awaiting reflection dialogue.
    - After Turn 1 reflection, empty state hides and canvas wrapper becomes visible.
    - Turn 1 status badge shows "Live Psychological Shift • Turn 1".
    - After Turn 2 follow-up reflection, emotional arc chart updates to Turn 2.
    - Chart canvas element is active and rendered.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        goto_authenticated(page, name="ArcUser")

        # 1. Fresh state: empty placeholder is visible, canvas wrapper is hidden
        empty_state = page.locator("#emotional-arc-empty")
        canvas_wrapper = page.locator("#emotional-arc-canvas-wrapper")
        assert empty_state.is_visible(), "Empty state must be visible before any reflection"
        assert not canvas_wrapper.is_visible(), "Canvas wrapper must be hidden before any reflection"
        assert "Awaiting Reflection Dialogue" in empty_state.inner_text()

        # 2. Type reflection and send Turn 1
        input_box = page.locator("#reflection-input")
        input_box.fill("Feeling scattered this morning, need to focus on architecture.")
        page.locator("#send-reflection-btn").click()

        # 3. Canvas wrapper is now revealed, empty placeholder hidden
        page.wait_for_selector("#emotional-arc-canvas-wrapper", state="visible", timeout=6000)
        assert canvas_wrapper.is_visible()
        assert not empty_state.is_visible()
        assert "Turn 1" in page.locator("#arc-status-badge").inner_text()
        assert page.locator("#emotionalArcChart").is_visible()

        # 4. Multi-turn: Send Turn 2 follow-up reflection
        input_box.fill("Taking a deep breath and structuring the components clearly.")
        page.locator("#send-reflection-btn").click()
        page.wait_for_timeout(1000)

        # 5. Emotional arc status badge advances to Turn 2
        assert "Turn 2" in page.locator("#arc-status-badge").inner_text()

        browser.close()


def test_browser_reflection_style_selector_and_routing():
    """
    Verify Reflection Style Selector:
    - 4 interactive cards present: Balanced, Actionable, Deep Philosophy, Brainstorm.
    - Clicking each style card toggles active state, updates persona mode.
    - Updates active-style-label and Notion callout emoji/title.
    - Affects live turn payload (/api/agent/live-turn) with matching persona_mode parameter.
    """
    captured_payloads = []

    def handle_request(req):
        if "/api/agent/live-turn" in req.url and req.method == "POST":
            try:
                captured_payloads.append(req.post_data_json)
            except Exception:
                pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("request", handle_request)
        goto_authenticated(page, name="StyleTester")

        # 1. Verify all 4 cards exist
        card_balanced = page.locator('.reflection-style-card[data-style="balanced"]')
        card_actionable = page.locator('.reflection-style-card[data-style="actionable"]')
        card_philosophy = page.locator('.reflection-style-card[data-style="philosophy"]')
        card_brainstorm = page.locator('.reflection-style-card[data-style="brainstorm"]')

        assert card_balanced.is_visible()
        assert card_actionable.is_visible()
        assert card_philosophy.is_visible()
        assert card_brainstorm.is_visible()

        # Default is balanced
        style_label = page.locator("#active-style-label")
        assert "Balanced" in style_label.inner_text()
        assert "active" in (card_balanced.get_attribute("class") or "")

        input_box = page.locator("#reflection-input")
        send_btn = page.locator("#send-reflection-btn")

        # 2. Click Actionable -> toggles active state, updates persona mode, sends persona_mode: "actionable"
        card_actionable.click()
        assert "Actionable" in style_label.inner_text()
        assert "active" in (card_actionable.get_attribute("class") or "")
        assert "active" not in (card_balanced.get_attribute("class") or "")
        assert "🎯" in page.locator("#callout-emoji").inner_text()
        assert "Actionable" in page.locator("#callout-title").inner_text()

        input_box.fill("Focusing on immediate execution goals and tickets.")
        send_btn.click()
        page.wait_for_selector("#chat-stream .model-badge", timeout=6000)
        assert len(captured_payloads) >= 1
        assert captured_payloads[-1].get("persona_mode") == "actionable"

        # 3. Click Deep Philosophy -> toggles active state, updates persona mode, sends persona_mode: "philosophy"
        card_philosophy.click()
        assert "Deep Philosophy" in style_label.inner_text()
        assert "active" in (card_philosophy.get_attribute("class") or "")
        assert "active" not in (card_actionable.get_attribute("class") or "")
        assert "📜" in page.locator("#callout-emoji").inner_text()
        assert "Deep Philosophy" in page.locator("#callout-title").inner_text()

        input_box.fill("Questioning core assumptions about time and priority.")
        send_btn.click()
        page.wait_for_timeout(800)
        assert len(captured_payloads) >= 2
        assert captured_payloads[-1].get("persona_mode") == "philosophy"

        # 4. Click Brainstorm -> toggles active state, updates persona mode, sends persona_mode: "brainstorm"
        card_brainstorm.click()
        assert "Brainstorm" in style_label.inner_text()
        assert "active" in (card_brainstorm.get_attribute("class") or "")
        assert "active" not in (card_philosophy.get_attribute("class") or "")
        assert "💡" in page.locator("#callout-emoji").inner_text()
        assert "Brainstorm" in page.locator("#callout-title").inner_text()

        input_box.fill("Exploring wild lateral possibilities.")
        send_btn.click()
        page.wait_for_timeout(800)
        assert len(captured_payloads) >= 3
        assert captured_payloads[-1].get("persona_mode") == "brainstorm"

        # 5. Click Balanced -> toggles active state, updates persona mode, sends persona_mode: "balanced"
        card_balanced.click()
        assert "Balanced" in style_label.inner_text()
        assert "active" in (card_balanced.get_attribute("class") or "")
        assert "active" not in (card_brainstorm.get_attribute("class") or "")
        assert "🧭" in page.locator("#callout-emoji").inner_text()
        assert "Balanced" in page.locator("#callout-title").inner_text()

        input_box.fill("Returning to center with balanced clarity.")
        send_btn.click()
        page.wait_for_timeout(800)
        assert len(captured_payloads) >= 4
        assert captured_payloads[-1].get("persona_mode") == "balanced"

        browser.close()


def test_browser_multiturn_dialogue_badges_auto_summarize_and_save():
    """
    Verify Multi-Turn Follow-Up Dialogue:
    - User bubble and Gemini reflection bubble with gemini-3.7-flash model badge and timestamp
    - Turn count increment (0 Turn -> 1 Turn -> 2 Turns)
    - Dynamic follow-up input placeholder
    - Auto-Summarize button click creates distilled summary card with badge
    - Save Reflection button click saves entry to Firestore and updates sync indicator
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        goto_authenticated(page, name="MultiTurnTester")

        # Initial turn counter is 0
        turn_badge = page.locator("#turn-counter-badge")
        assert "0 Turn" in turn_badge.inner_text()

        input_box = page.locator("#reflection-input")
        send_btn = page.locator("#send-reflection-btn")

        # Step 1: Turn 1 (Initial Reflection)
        prompt_turn_1 = "Initial reflection on establishing a strong daily rhythm."
        input_box.fill(prompt_turn_1)
        send_btn.click()
        page.wait_for_selector("#chat-stream .model-badge", timeout=6000)

        # Verify User bubble 1 and Gemini bubble 1
        chat_stream = page.locator("#chat-stream")
        assert prompt_turn_1 in chat_stream.inner_text()
        model_badges = page.locator("#chat-stream .model-badge", has_text="gemini-3.7-flash")
        assert model_badges.count() >= 1
        assert "1 Turn" in turn_badge.inner_text()

        # Verify dynamic follow-up placeholder
        placeholder = input_box.get_attribute("placeholder") or ""
        assert "Ask a follow-up reflection, challenge Gemini's thought, or explore deeper..." in placeholder

        # Step 2: Turn 2 (Multi-Turn Follow-Up Inquiry)
        prompt_turn_2 = "How can I structure the morning deep work blocks without context switching?"
        input_box.fill(prompt_turn_2)
        send_btn.click()
        page.wait_for_timeout(1000)

        # Verify User bubble 2, Gemini bubble 2, and turn count increment to 2 Turns
        assert prompt_turn_2 in chat_stream.inner_text()
        assert model_badges.count() >= 2
        assert "2 Turns" in turn_badge.inner_text()

        # Step 3: Auto-Summarize Button Click
        summarize_btn = page.locator("#auto-summarize-btn")
        assert summarize_btn.is_visible()
        summarize_btn.click()
        page.wait_for_selector(".summary-card", timeout=6000)
        assert "distilled reflection summary" in page.locator(".summary-card").inner_text().lower()
        assert "Auto-Synthesized" in page.locator(".summary-card").inner_text()

        # Step 4: Save Reflection Button Click
        save_btn = page.locator("#save-session-btn")
        assert save_btn.is_visible()
        save_btn.click()
        page.wait_for_timeout(1000)

        # Firestore sync indicator verified
        sync_badge = page.locator("#firestore-sync-badge")
        assert "Firestore Synchronized" in sync_badge.inner_text()

        # Verify entry rendered into Dynamic History list
        history_list = page.locator("#journal-history-list")
        assert history_list.is_visible()

        browser.close()


def test_browser_history_live_search_and_filter_chips():
    """
    Verify Past Reflections Search & Filter Chips:
    - Live search across title, date, content, and breakthrough
    - Filter chips: [All], [Reflective], [Actionable], [Breakthrough]
    - Dynamic review drawer modal opening, content inspection, and closing
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        goto_authenticated(page, name="SearchFilterTester")

        # Seed 3 distinct reflections via API
        page.evaluate("""
            async () => {
                const token = localStorage.getItem('journal_token');
                const headers = {
                    'Authorization': 'Bearer ' + token,
                    'Content-Type': 'application/json'
                };
                await fetch('/api/journal/save', {
                    method: 'POST',
                    headers,
                    body: JSON.stringify({
                        title: 'Zen Mindfulness Practice',
                        content: 'Meditative stillness and breath focus in the morning.',
                        tags: ['Reflective', 'Mindfulness'],
                        action_items: []
                    })
                });
                await fetch('/api/journal/save', {
                    method: 'POST',
                    headers,
                    body: JSON.stringify({
                        title: 'Sprint Architecture Execution',
                        content: 'Refining Cloud Run deploy pipeline and habits.',
                        tags: ['Actionable', 'Work'],
                        action_items: [{title: 'Deploy to Cloud Run'}]
                    })
                });
                await fetch('/api/journal/save', {
                    method: 'POST',
                    headers,
                    body: JSON.stringify({
                        title: 'Philosophy on Mental Models',
                        content: 'Socratic inquiry revealed deeper assumptions.',
                        breakthrough: 'Realized clarity comes from ruthless elimination.',
                        tags: ['Breakthrough', 'Philosophy'],
                        action_items: []
                    })
                });
            }
        """)

        # Refresh history
        page.locator("#refresh-history-btn").click()
        page.wait_for_timeout(600)

        item_zen = page.locator("#journal-history-list .history-item", has_text="Zen Mindfulness Practice")
        item_sprint = page.locator("#journal-history-list .history-item", has_text="Sprint Architecture Execution")
        item_philo = page.locator("#journal-history-list .history-item", has_text="Philosophy on Mental Models")

        assert item_zen.is_visible()
        assert item_sprint.is_visible()
        assert item_philo.is_visible()

        search_input = page.locator("#history-search-input")

        # 1. Search by Title: "Zen"
        search_input.fill("Zen")
        page.wait_for_timeout(200)
        assert item_zen.is_visible()
        assert not item_sprint.is_visible()
        assert not item_philo.is_visible()

        # Clear search
        search_input.fill("")
        page.wait_for_timeout(200)
        assert item_zen.is_visible()
        assert item_sprint.is_visible()
        assert item_philo.is_visible()

        # 2. Search by Content: "Cloud Run"
        search_input.fill("Cloud Run")
        page.wait_for_timeout(200)
        assert item_sprint.is_visible()
        assert not item_zen.is_visible()
        assert not item_philo.is_visible()

        search_input.fill("")
        page.wait_for_timeout(200)

        # 3. Search by Breakthrough: "ruthless elimination"
        search_input.fill("ruthless elimination")
        page.wait_for_timeout(200)
        assert item_philo.is_visible()
        assert not item_zen.is_visible()
        assert not item_sprint.is_visible()

        # 4. Search with non-matching term: zero items displayed
        search_input.fill("NonExistentTermXYZ123")
        page.wait_for_timeout(200)
        assert not item_zen.is_visible()
        assert not item_sprint.is_visible()
        assert not item_philo.is_visible()

        # Clear search
        search_input.fill("")
        page.wait_for_timeout(200)
        assert item_zen.is_visible()
        assert item_sprint.is_visible()
        assert item_philo.is_visible()

        # 5. Filter Chip: [Reflective]
        chip_reflective = page.locator('#history-filter-chips .history-chip[data-filter="reflective"]')
        chip_reflective.click()
        page.wait_for_timeout(200)
        assert item_zen.is_visible()
        assert not item_sprint.is_visible()
        assert not item_philo.is_visible()

        # 6. Filter Chip: [Actionable]
        chip_actionable = page.locator('#history-filter-chips .history-chip[data-filter="actionable"]')
        chip_actionable.click()
        page.wait_for_timeout(200)
        assert item_sprint.is_visible()
        assert not item_zen.is_visible()
        assert not item_philo.is_visible()

        # 7. Filter Chip: [Breakthrough]
        chip_breakthrough = page.locator('#history-filter-chips .history-chip[data-filter="breakthrough"]')
        chip_breakthrough.click()
        page.wait_for_timeout(200)
        assert item_philo.is_visible()
        assert not item_zen.is_visible()
        assert not item_sprint.is_visible()

        # 8. Filter Chip: [All]
        chip_all = page.locator('#history-filter-chips .history-chip[data-filter="all"]')
        chip_all.click()
        page.wait_for_timeout(200)
        assert item_zen.is_visible()
        assert item_sprint.is_visible()
        assert item_philo.is_visible()

        # 9. Dynamic Review Drawer Modal Test
        item_zen.click()
        review_modal = page.locator("#journal-review-modal")
        page.wait_for_selector("#journal-review-modal", state="visible", timeout=5000)
        assert "Zen Mindfulness Practice" in page.locator("#review-modal-title").inner_text()
        assert "Meditative stillness" in page.locator("#review-modal-content").inner_text()

        # Close via top cross button
        page.locator("#close-review-modal-btn").click()
        page.wait_for_selector("#journal-review-modal", state="hidden", timeout=5000)

        # Open second item and close via bottom button
        item_sprint.click()
        page.wait_for_selector("#journal-review-modal", state="visible", timeout=5000)
        assert "Sprint Architecture Execution" in page.locator("#review-modal-title").inner_text()
        page.locator("#close-review-modal-bottom-btn").click()
        page.wait_for_selector("#journal-review-modal", state="hidden", timeout=5000)

        browser.close()


def test_browser_rapid_reflection_style_switching_during_turn():
    """
    Verify rapid concurrent style switching:
    - User rapidly toggles between style cards before and during turn submission.
    - Active UI states, badge labels, and emojis update synchronously and stay clean.
    - Verified network payload accurately reflects the latest active mode.
    """
    captured_payloads = []

    def handle_request(req):
        if "/api/agent/live-turn" in req.url and req.method == "POST":
            try:
                captured_payloads.append(req.post_data_json)
            except Exception:
                pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("request", handle_request)
        goto_authenticated(page, name="RapidStyleUser")

        card_balanced = page.locator('.reflection-style-card[data-style="balanced"]')
        card_actionable = page.locator('.reflection-style-card[data-style="actionable"]')
        card_philosophy = page.locator('.reflection-style-card[data-style="philosophy"]')
        card_brainstorm = page.locator('.reflection-style-card[data-style="brainstorm"]')
        style_label = page.locator("#active-style-label")

        # Rapid succession clicking
        card_actionable.click()
        card_philosophy.click()
        card_brainstorm.click()
        card_actionable.click()

        # Final active state must be Actionable
        assert "Actionable" in style_label.inner_text()
        assert "active" in (card_actionable.get_attribute("class") or "")
        assert "active" not in (card_philosophy.get_attribute("class") or "")
        assert "active" not in (card_brainstorm.get_attribute("class") or "")

        # Send turn with actionable mode
        input_box = page.locator("#reflection-input")
        input_box.fill("Action item rapid test.")
        page.locator("#send-reflection-btn").click()

        # Rapidly switch style to Deep Philosophy immediately after send
        card_philosophy.click()
        assert "Deep Philosophy" in style_label.inner_text()
        assert "active" in (card_philosophy.get_attribute("class") or "")

        page.wait_for_selector("#chat-stream .model-badge", timeout=6000)
        assert len(captured_payloads) >= 1
        assert captured_payloads[0].get("persona_mode") == "actionable"

        # Subsequent Turn 2 must use the newly selected Deep Philosophy mode
        input_box.fill("Reframing in philosophy mode.")
        page.locator("#send-reflection-btn").click()
        page.wait_for_timeout(800)

        assert len(captured_payloads) >= 2
        assert captured_payloads[1].get("persona_mode") == "philosophy"

        browser.close()


def test_browser_multiturn_session_expiry_and_draft_restoration():
    """
    Verify Multi-Turn Follow-Up 401 Session Expiry & Draft Preservation:
    - User executes Turn 1 successfully.
    - User types Turn 2 follow-up reflection into input box.
    - 401 Unauthorized occurs on API fetch.
    - App transitions safely to Auth Landing without crashing.
    - Draft is saved in localStorage.
    - Upon re-authentication, app restores Turn 2 draft into #reflection-input.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        goto_authenticated(page, name="SessionExpiryUser")

        # Turn 1
        input_box = page.locator("#reflection-input")
        input_box.fill("Turn 1: Initial morning reflection on codebase architecture.")
        page.locator("#send-reflection-btn").click()
        page.wait_for_selector("#chat-stream .model-badge", timeout=6000)
        assert "1 Turn" in page.locator("#turn-counter-badge").inner_text()

        # Turn 2: User drafts deep follow-up thought
        turn_2_thought = "Turn 2: How do we guarantee multi-tenant Firestore security rules fail closed?"
        input_box.fill(turn_2_thought)

        # Mock 401 Unauthorized for next live-turn request
        page.route("**/api/agent/live-turn", lambda route: route.fulfill(
            status=401,
            content_type="application/json",
            body='{"detail": "Firebase auth token expired."}'
        ))

        # Attempt to send Turn 2
        page.locator("#send-reflection-btn").click()
        page.wait_for_timeout(500)

        # Verify auth landing screen appears with explanatory banner
        assert page.locator("#auth-landing").is_visible()
        assert not page.locator("#app-shell").is_visible()

        # Verify draft was safely preserved in localStorage
        stored_draft = page.evaluate("localStorage.getItem('journal_draft')")
        assert stored_draft == turn_2_thought

        # Remove 401 route to allow normal authentication
        page.unroute("**/api/agent/live-turn")

        # Simulate user re-authenticating
        page.evaluate("() => { if (window.__SANCTUARY_TEST_AUTH__) { window.__SANCTUARY_TEST_AUTH__.signIn('reauth_user', 'user@test.local', 'Reauthenticated User'); } }")
        page.wait_for_selector("#app-shell:not(.hidden)", timeout=5000)

        # Verify app shell is visible and Turn 2 draft was restored into #reflection-input
        assert page.locator("#app-shell").is_visible()
        restored_input = page.locator("#reflection-input").input_value()
        assert restored_input == turn_2_thought

        browser.close()


def test_browser_modal_escape_key_and_clean_dismissal():
    """
    Verify Escape key dismisses all open modals cleanly without null-pointer errors:
    - Settings modal
    - Shutdown ritual modal
    - Executive data report modal
    - Journal review drawer modal
    """
    console_errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda err: console_errors.append(str(err)))
        goto_authenticated(page, name="EscapeTester")

        # 1. Test Settings Modal Escape
        page.locator("#open-settings-btn").click()
        page.wait_for_selector("#settings-modal", state="visible", timeout=3000)
        page.keyboard.press("Escape")
        page.wait_for_selector("#settings-modal", state="hidden", timeout=3000)
        assert not page.locator("#settings-modal").is_visible()

        # 2. Test Executive Report Modal Escape
        page.locator("#executive-report-btn").click()
        page.wait_for_selector("#executive-report-modal", state="visible", timeout=3000)
        page.keyboard.press("Escape")
        page.wait_for_selector("#executive-report-modal", state="hidden", timeout=3000)
        assert not page.locator("#executive-report-modal").is_visible()

        # 3. Test Shutdown Ritual Modal Escape
        page.locator("#nav-shutdown").click()
        page.wait_for_selector("#shutdown-modal", state="visible", timeout=3000)
        page.keyboard.press("Escape")
        page.wait_for_selector("#shutdown-modal", state="hidden", timeout=3000)
        assert not page.locator("#shutdown-modal").is_visible()

        # 4. Test Journal Review Drawer Modal Escape
        page.evaluate("""
            () => {
                openJournalReviewModal({
                    id: 'escape_test_doc',
                    title: 'Escape Test Entry',
                    content: 'Testing modal dismissal on Escape.',
                    created_at: new Date().toISOString()
                });
            }
        """)
        page.wait_for_selector("#journal-review-modal", state="visible", timeout=3000)
        page.keyboard.press("Escape")
        page.wait_for_selector("#journal-review-modal", state="hidden", timeout=3000)
        assert not page.locator("#journal-review-modal").is_visible()

        # Ensure no runtime exceptions occurred during Escape key events
        assert len(console_errors) == 0, f"Encountered unexpected console errors: {console_errors}"

        browser.close()


def test_browser_multiturn_whitespace_validation_and_cmd_enter_submit():
    """
    Verify input edge cases:
    - Empty or whitespace-only input cannot be submitted (turn counter does not advance).
    - Cmd+Enter / Ctrl+Enter keyboard shortcut triggers reflection submit.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        goto_authenticated(page, name="ShortcutTester")

        input_box = page.locator("#reflection-input")
        send_btn = page.locator("#send-reflection-btn")
        turn_badge = page.locator("#turn-counter-badge")

        # 1. Whitespace only submission
        input_box.fill("   \n\t   ")
        send_btn.click()
        page.wait_for_timeout(300)
        assert "0 Turn" in turn_badge.inner_text()
        assert page.locator("#chat-stream .chat-bubble").count() == 0

        # 2. Cmd+Enter / Ctrl+Enter quick submission
        input_box.fill("Testing keyboard shortcut quick submit with Cmd+Enter.")
        page.keyboard.press("Meta+Enter")
        page.wait_for_selector("#chat-stream .model-badge", timeout=6000)
        assert "1 Turn" in turn_badge.inner_text()
        assert "Testing keyboard shortcut quick submit with Cmd+Enter." in page.locator("#chat-stream").inner_text()

        browser.close()


def test_browser_auto_summarize_persists_breakthrough_and_summary_to_firestore():
    """
    Verify Auto-Summarize to Firestore Save pipeline:
    - User conducts reflection turn.
    - Clicks Auto-Summarize button -> renders distilled summary card.
    - Clicks Save Reflection button -> verifies POST /api/journal/save contains summary & breakthrough.
    """
    captured_save_payloads = []

    def handle_request(req):
        if "/api/journal/save" in req.url and req.method == "POST":
            try:
                captured_save_payloads.append(req.post_data_json)
            except Exception:
                pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("request", handle_request)
        goto_authenticated(page, name="SummarizeSaveTester")

        # Turn 1
        input_box = page.locator("#reflection-input")
        input_box.fill("Focusing deeply on engineering simplicity and ruthless clarity.")
        page.locator("#send-reflection-btn").click()
        page.wait_for_selector("#chat-stream .model-badge", timeout=6000)

        # Auto-Summarize
        page.locator("#auto-summarize-btn").click()
        page.wait_for_selector(".summary-card", timeout=6000)
        assert page.locator(".summary-card").is_visible()

        # Save Reflection
        page.locator("#save-session-btn").click()
        page.wait_for_timeout(800)
        assert "Firestore Synchronized" in page.locator("#firestore-sync-badge").inner_text()

        # Verify captured save payload
        assert len(captured_save_payloads) >= 1
        payload = captured_save_payloads[-1]
        assert "summary" in payload and len(payload["summary"]) > 0
        assert "breakthrough" in payload
        assert "MultiTurn" in payload.get("tags", [])
        browser.close()
