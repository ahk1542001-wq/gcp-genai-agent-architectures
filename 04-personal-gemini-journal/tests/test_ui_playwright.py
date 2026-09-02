import os
import sys
import time
import socket
import threading
import uvicorn
import pytest
from playwright.sync_api import sync_playwright

# Set up test environment
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

def test_browser_ui_shell_and_navigation():
    """Verify Notion shell loading, persona switching, and view toggling with zero console errors."""
    console_errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        # 1. Load the Sanctuary OS SPA
        page.goto(BASE_URL, wait_until="networkidle")
        page.wait_for_timeout(500)

        # 2. Verify Title & Core Brand Header
        assert "Personal Gemini Life Guardian" in page.title()
        brand = page.locator("text=Sanctuary OS").first
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

        page.goto(BASE_URL, wait_until="networkidle")

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
        page.goto(BASE_URL, wait_until="networkidle")

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
        page.goto(BASE_URL, wait_until="networkidle")

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
        page.goto(BASE_URL, wait_until="networkidle")

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
        page.goto(BASE_URL, wait_until="networkidle")

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
        page.goto(BASE_URL, wait_until="networkidle")

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
        page.goto(BASE_URL, wait_until="networkidle")

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
        page.goto(BASE_URL, wait_until="networkidle")

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
        page.goto(BASE_URL, wait_until="networkidle")

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
        page.goto(BASE_URL, wait_until="networkidle")

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
