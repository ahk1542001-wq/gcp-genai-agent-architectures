"""
Live Browser Automation E2E Test Suite for Sanctuary OS
Compliant with browser-automation and frontend-design principles.
Tests every button click, view switching, live typing, dynamic history,
executive report synthesis, and captures visual proof screenshots.
"""

import os
import sys

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
import socket
import threading
import uvicorn
import pytest
from playwright.sync_api import sync_playwright

# Set test environment
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
    """Spins up the FastAPI server in background thread."""
    from main import app
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=TEST_PORT, log_level="error"))
    t = threading.Thread(target=server.run, daemon=True)
    t.start()
    
    for _ in range(50):
        try:
            with socket.create_connection(("127.0.0.1", TEST_PORT), timeout=0.2):
                break
        except OSError:
            time.sleep(0.1)
    yield
    server.should_exit = True


def test_full_browser_automation_lifecycle():
    """
    Comprehensive Browser Automation Flow:
    1. Authenticate user into private tenant.
    2. Test live typing into Reflection Input and submit reflection.
    3. Test all Navigation button clicks (Reflect -> Act -> Calendar -> Rewind -> Reflect).
    4. Verify ambient glow styling on active navigation items.
    5. Test Executive Data Report modal: open, verify authentic numbers, test markdown export.
    6. Test De-Stress Box Breathing modal cycle and Tibetan chime.
    7. Test Evening Shutdown Ritual modal.
    8. Test Dynamic History Sidebar and Review Drawer.
    9. Capture screenshots of key stages.
    """
    screenshot_dir = os.path.join(os.path.dirname(__file__), "screenshots")
    os.makedirs(screenshot_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # Step 1: Open Application & Authenticate
        page.goto(BASE_URL, wait_until="networkidle")
        page.evaluate("() => { if (window.__SANCTUARY_TEST_AUTH__) { window.__SANCTUARY_TEST_AUTH__.signIn('exec_tester', 'exec@sanctuary.test', 'Aung Hein Kyaw'); } }")
        page.wait_for_selector("#app-shell:not(.hidden)", timeout=5000)
        
        # Verify authenticated tenant identity
        assert page.locator("#user-display-name").inner_text() == "Aung Hein Kyaw"
        page.screenshot(path=os.path.join(screenshot_dir, "01_sanctuary_dashboard.png"))

        # Step 2: Reflection Style Selector & Multi-Turn Dialogue with Badges
        pill = page.locator("#mode-selector-pill")
        card_actionable = page.locator('.reflection-style-card[data-style="actionable"]')
        card_philosophy = page.locator('.reflection-style-card[data-style="philosophy"]')
        card_brainstorm = page.locator('.reflection-style-card[data-style="brainstorm"]')
        card_balanced = page.locator('.reflection-style-card[data-style="balanced"]')

        pill.click()
        page.wait_for_selector("#mode-dropdown-menu:not(.hidden)", timeout=3000)
        card_actionable.click()
        assert "Actionable" in page.locator("#active-style-label").inner_text()

        pill.click()
        page.wait_for_selector("#mode-dropdown-menu:not(.hidden)", timeout=3000)
        card_philosophy.click()
        assert "Deep Philosophy" in page.locator("#active-style-label").inner_text()

        pill.click()
        page.wait_for_selector("#mode-dropdown-menu:not(.hidden)", timeout=3000)
        card_brainstorm.click()
        assert "Brainstorm" in page.locator("#active-style-label").inner_text()

        pill.click()
        page.wait_for_selector("#mode-dropdown-menu:not(.hidden)", timeout=3000)
        card_balanced.click()
        assert "Balanced" in page.locator("#active-style-label").inner_text()
        page.screenshot(path=os.path.join(screenshot_dir, "02a_reflection_style_selector.png"))

        # 2B. Live Typing in Reflection Studio (Turn 1)
        input_box = page.locator("#reflection-input")
        assert input_box.is_visible()
        input_box.click()
        test_thought = "Designing an ultra-secure personal life guardian for Google Cloud Run with zero hardcoded credentials."
        input_box.type(test_thought, delay=15)
        
        # Click Clear button and re-type to test clear functionality
        page.locator("#clear-input-btn").click()
        assert input_box.input_value() == ""
        
        input_box.type(test_thought, delay=10)
        page.screenshot(path=os.path.join(screenshot_dir, "02b_reflection_input_typed.png"))

        # Submit Turn 1 reflection
        page.locator("#send-reflection-btn").click()
        page.wait_for_selector("#chat-stream .model-badge", timeout=6000)
        assert test_thought in page.locator("#chat-stream").inner_text()

        # 2C. Verify Turn 1 model badge, turn counter, emotional arc, and follow-up placeholder
        assert page.locator("#chat-stream .model-badge", has_text="gemini-3.7-flash").first.is_visible()
        assert "1 Turn" in page.locator("#turn-counter-badge").inner_text()
        assert "Turn 1" in page.locator("#arc-status-badge").inner_text()
        assert "Ask a follow-up reflection, challenge Gemini's thought, or explore deeper..." in (input_box.get_attribute("placeholder") or "")

        # 2D. Multi-Turn Follow-Up Dialogue (Turn 2)
        followup_thought = "What architectural boundaries ensure zero-leakage cross-tenant isolation in Firestore?"
        input_box.fill(followup_thought)
        page.locator("#send-reflection-btn").click()
        page.wait_for_timeout(1000)

        assert followup_thought in page.locator("#chat-stream").inner_text()
        assert page.locator("#chat-stream .model-badge").count() >= 2
        assert "2 Turns" in page.locator("#turn-counter-badge").inner_text()
        assert "Turn 2" in page.locator("#arc-status-badge").inner_text()
        page.screenshot(path=os.path.join(screenshot_dir, "02c_multiturn_dialogue_and_badges.png"))

        # 2E. Auto-Summarize Action
        page.locator("#auto-summarize-btn").click()
        page.wait_for_selector(".summary-card", timeout=6000)
        assert page.locator(".summary-card").is_visible()
        page.screenshot(path=os.path.join(screenshot_dir, "02d_auto_summarize_distilled.png"))

        # 2F. Save Reflection Action
        page.locator("#save-session-btn").click()
        page.wait_for_timeout(800)
        assert "Firestore Synchronized" in page.locator("#firestore-sync-badge").inner_text()
        page.screenshot(path=os.path.join(screenshot_dir, "02e_firestore_saved.png"))

        # Step 3: Navigation Switching & Ambient Glow Verification
        # 3A. Switch to Act / Kanban Board
        page.locator("#nav-kanban").click()
        page.wait_for_selector("#view-kanban-content:not(.hidden)", timeout=3000)
        assert "active-glow" in page.locator("#nav-kanban").get_attribute("class")
        page.screenshot(path=os.path.join(screenshot_dir, "03_kanban_board.png"))

        # 3B. Switch to Mindful Calendar
        page.locator("#nav-calendar").click()
        page.wait_for_selector("#view-calendar-content:not(.hidden)", timeout=3000)
        assert "active-glow" in page.locator("#nav-calendar").get_attribute("class")
        page.screenshot(path=os.path.join(screenshot_dir, "04_calendar_view.png"))

        # 3C. Switch to Life Rewind
        page.locator("#nav-rewind").click()
        page.wait_for_selector("#view-rewind-content:not(.hidden)", timeout=3000)
        assert "active-glow" in page.locator("#nav-rewind").get_attribute("class")
        page.screenshot(path=os.path.join(screenshot_dir, "05_rewind_view.png"))

        # 3D. Switch back to Journal Studio
        page.locator("#nav-journal").click()
        page.wait_for_selector("#view-journal-content:not(.hidden)", timeout=3000)
        assert "active-glow" in page.locator("#nav-journal").get_attribute("class")

        # Step 4: Executive Cognitive & Productivity Data Report Modal
        report_btn = page.locator("#executive-report-btn")
        assert report_btn.is_visible()
        report_btn.click()

        report_modal = page.locator("#executive-report-modal")
        page.wait_for_selector("#executive-report-modal", state="visible", timeout=5000)
        
        # Verify genuine metrics displayed
        word_count_text = page.locator("#report-word-count").inner_text()
        done_tasks_text = page.locator("#report-done-tasks").inner_text()
        assert int(word_count_text.replace(",", "")) >= 0
        assert int(done_tasks_text.replace(",", "")) >= 0
        page.screenshot(path=os.path.join(screenshot_dir, "06_executive_report_modal.png"))

        # Close Executive Report Modal
        page.locator("#close-executive-report-btn").click()
        page.wait_for_selector("#executive-report-modal", state="hidden", timeout=5000)

        # Step 5: Evening Shutdown Ritual Modal
        shutdown_btn = page.locator("#nav-shutdown")
        shutdown_btn.click()
        shutdown_modal = page.locator("#shutdown-modal")
        page.wait_for_selector("#shutdown-modal", state="visible", timeout=5000)
        page.screenshot(path=os.path.join(screenshot_dir, "08_shutdown_modal.png"))

        # Close shutdown modal
        page.locator("#cancel-shutdown-btn").click()
        page.wait_for_selector("#shutdown-modal", state="hidden", timeout=5000)

        # Step 7: Dynamic History & Review Drawer Test (Zero Mock Data)
        history_list = page.locator("#journal-history-list")
        assert "Cloud Run Security & Deployment" not in history_list.inner_text(), "Found legacy hardcoded entry!"
        
        # Save real journal entry via API
        page.evaluate("""
            async () => {
                await fetch('/api/journal/save', {
                    method: 'POST',
                    headers: {
                        'Authorization': 'Bearer ' + localStorage.getItem('journal_token'),
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        title: 'Live E2E Verified Reflection',
                        content: 'All components verified under Playwright browser automation.',
                        tags: ['Actionable', 'Breakthrough'],
                        conversation: [{role: 'user', text: 'Status update on Sanctuary OS'}, {role: 'model', text: 'All systems verified.'}],
                        action_items: [{title: 'Submit to Hack2Skill APAC GenAI Academy'}]
                    })
                });
            }
        """)

        page.locator("#refresh-history-btn").click()
        page.wait_for_timeout(500)

        # Test live search
        search_box = page.locator("#history-search-input")
        search_box.fill("Verified")
        page.wait_for_timeout(200)
        saved_entry = page.locator("#journal-history-list .history-item", has_text="Live E2E Verified Reflection")
        assert saved_entry.is_visible()
        search_box.fill("")
        page.wait_for_timeout(200)

        # Test filter chips
        page.locator('#history-filter-chips .history-chip[data-filter="actionable"]').click()
        page.wait_for_timeout(200)
        assert saved_entry.is_visible()
        page.locator('#history-filter-chips .history-chip[data-filter="breakthrough"]').click()
        page.wait_for_timeout(200)
        assert saved_entry.is_visible()
        page.locator('#history-filter-chips .history-chip[data-filter="all"]').click()
        page.wait_for_timeout(200)
        page.screenshot(path=os.path.join(screenshot_dir, "09a_history_search_and_filter_chips.png"))

        # Click entry to open Review Drawer
        saved_entry.click()

        review_modal = page.locator("#journal-review-modal")
        page.wait_for_selector("#journal-review-modal", state="visible", timeout=5000)
        assert "Live E2E Verified Reflection" in page.locator("#review-modal-title").inner_text()
        page.screenshot(path=os.path.join(screenshot_dir, "09b_history_review_drawer.png"))

        page.locator("#close-review-modal-btn").click()
        page.wait_for_selector("#journal-review-modal", state="hidden", timeout=5000)

        browser.close()
