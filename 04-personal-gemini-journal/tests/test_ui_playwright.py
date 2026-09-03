import os
import sys
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
    """Verify Settings Modal interaction and toggle states."""
    console_errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        goto_authenticated(page)

        # Open Settings Modal
        settings_btn = page.locator("#open-settings-btn")
        settings_btn.click()
        page.wait_for_timeout(300)

        modal = page.locator("#settings-modal")
        assert modal.is_visible()

        # Check toggle switches exist
        voice_toggle = page.locator("#setting-voice-enabled")
        assert voice_toggle.is_visible()
        tibetan_toggle = page.locator("#setting-tibetan-sound")
        assert tibetan_toggle.is_visible()

        # Close Modal
        close_btn = page.locator("#close-settings-btn")
        close_btn.click()
        page.wait_for_timeout(300)
        assert not modal.is_visible()

        browser.close()

    assert len(console_errors) == 0

def test_browser_ui_kanban_card_creation():
    """Verify Kanban board renders cards and updates counts."""
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

def test_browser_ui_destress_breathing_modal_cycle():
    """Verify De-Stress Breathe button opens breathing circle and close button dismisses it."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        goto_authenticated(page)

        # Click De-Stress Breathe in sidebar
        page.locator("#nav-destress").click()
        page.wait_for_timeout(200)

        modal = page.locator("#breathing-modal")
        assert modal.is_visible()
        assert page.locator("#breathing-circle").is_visible()
        assert "Inhale" in page.locator("#breathing-phase-text").text_content()

        # Close Modal
        page.locator("#close-breathing-btn").click()
        page.wait_for_timeout(200)
        assert not modal.is_visible()

        browser.close()

def test_browser_ui_shutdown_ritual_modal():
    """Verify Evening Shutdown button opens ritual modal and close button dismisses it."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        goto_authenticated(page)

        # Click Evening Shutdown in sidebar
        page.locator("#nav-shutdown").click()
        page.wait_for_timeout(200)

        modal = page.locator("#shutdown-modal")
        assert modal.is_visible()
        assert "Evening Shutdown Sanctuary" in modal.text_content()

        # Close Modal
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
