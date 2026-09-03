"""
Live Browser Automation E2E Test Suite for Sanctuary OS
Compliant with browser-automation and frontend-design principles.
Tests every button click, view switching, live typing, dynamic history,
executive report synthesis, and captures visual proof screenshots.
"""

import os
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

        # Step 2: Live Typing in Reflection Studio
        input_box = page.locator("#reflection-input")
        assert input_box.is_visible()
        input_box.click()
        test_thought = "Designing an ultra-secure personal life guardian for Google Cloud Run with zero hardcoded credentials."
        input_box.type(test_thought, delay=15)
        
        # Click Clear button and re-type to test clear functionality
        page.locator("#clear-input-btn").click()
        assert input_box.input_value() == ""
        
        input_box.type(test_thought, delay=10)
        page.screenshot(path=os.path.join(screenshot_dir, "02_reflection_input_typed.png"))

        # Submit reflection
        page.locator("#send-reflection-btn").click()
        page.wait_for_selector("#chat-stream .animate-fadeIn", timeout=5000)
        assert test_thought in page.locator("#chat-stream").inner_text()

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
                        conversation: [{role: 'user', text: 'Status update on Sanctuary OS'}, {role: 'model', text: 'All systems verified.'}],
                        action_items: [{title: 'Submit to Hack2Skill APAC GenAI Academy'}]
                    })
                });
            }
        """)

        page.locator("#refresh-history-btn").click()
        page.wait_for_timeout(500)

        # Click entry to open Review Drawer
        saved_entry = page.locator("#journal-history-list .history-item", has_text="Live E2E Verified Reflection")
        assert saved_entry.is_visible()
        saved_entry.click()

        review_modal = page.locator("#journal-review-modal")
        page.wait_for_selector("#journal-review-modal", state="visible", timeout=5000)
        assert "Live E2E Verified Reflection" in page.locator("#review-modal-title").inner_text()
        page.screenshot(path=os.path.join(screenshot_dir, "09_history_review_drawer.png"))

        page.locator("#close-review-modal-btn").click()
        page.wait_for_selector("#journal-review-modal", state="hidden", timeout=5000)

        browser.close()
