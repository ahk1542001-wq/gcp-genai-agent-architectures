#!/usr/bin/env python3
"""
Record Actual Human User Walkthrough Video for Sanctuary OS
Using Playwright native screen recording with:
- Realistic typing speed (character-by-character)
- Simulated mouse movements & animated cursor ring
- Full interactive user journey:
  1. Landing page & Sign In as Victor Kyaw
  2. Persona Mode selection (Actionable Strategy)
  3. Live typing of Burmese reflection & Gemini response
  4. Human-in-the-Loop task proposal appearance & approval
  5. Distill & Save session to Firestore
  6. Navigation to Executive Kanban board & task interaction
  7. Mindful Calendar & real-time Emotional Arc curve
  8. Life Rewind genuine metrics
  9. Evening Shutdown ritual with Burmese gratitude & Zen confirmation
- Converts to 1080p MP4 and optimized GIF via ffmpeg
"""

import os
import sys
import time
import socket
import threading
import subprocess
from pathlib import Path

# Add project root to sys.path
PROJECT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_DIR))

# Ensure test / demo mode for hermetic local execution
os.environ["ENVIRONMENT"] = "test"
os.environ["ALLOW_TEST_AUTH"] = "true"
os.environ["USE_MOCK_DB"] = "true"
os.environ["IS_TEST_MODE"] = "true"
os.environ["GEMINI_API_KEY"] = "placeholder_key"
os.environ["GCP_PROJECT_ID"] = "intelligent-arc-488111-s0"

def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

TEST_PORT = get_free_port()
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"
VIDEO_RECORD_DIR = PROJECT_DIR / "tests" / "recordings"
OUTPUT_MP4 = PROJECT_DIR / "sanctuary_os_demo_walkthrough.mp4"
OUTPUT_GIF = PROJECT_DIR / "sanctuary_os_demo_walkthrough.gif"

def start_server():
    import uvicorn
    from main import app
    config = uvicorn.Config(app, host="127.0.0.1", port=TEST_PORT, log_level="warning")
    server = uvicorn.Server(config)
    t = threading.Thread(target=server.run, daemon=True)
    t.start()
    
    # Wait for server readiness
    for _ in range(50):
        try:
            with socket.create_connection(("127.0.0.1", TEST_PORT), timeout=0.2):
                print(f"  ✓ Local demo server ready at {BASE_URL}")
                return server
        except OSError:
            time.sleep(0.1)
    raise RuntimeError("Failed to start local demo server")

def inject_cursor_overlay(page):
    """Injects a sleek glowing cursor highlight that follows Playwright mouse moves."""
    page.evaluate("""() => {
        if (document.getElementById('__demo_cursor')) return;
        const cursor = document.createElement('div');
        cursor.id = '__demo_cursor';
        cursor.style.position = 'fixed';
        cursor.style.width = '24px';
        cursor.style.height = '24px';
        cursor.style.borderRadius = '50%';
        cursor.style.backgroundColor = 'rgba(99, 102, 241, 0.45)';
        cursor.style.border = '2px solid #818cf8';
        cursor.style.boxShadow = '0 0 12px rgba(129, 140, 248, 0.6)';
        cursor.style.pointerEvents = 'none';
        cursor.style.zIndex = '999999';
        cursor.style.transition = 'transform 0.12s ease, width 0.15s ease, height 0.15s ease, background-color 0.15s ease';
        cursor.style.transform = 'translate(-50%, -50%)';
        cursor.style.display = 'block';
        cursor.style.left = '720px';
        cursor.style.top = '450px';
        document.body.appendChild(cursor);

        window.addEventListener('mousemove', (e) => {
            cursor.style.left = e.clientX + 'px';
            cursor.style.top = e.clientY + 'px';
        });
        window.addEventListener('mousedown', () => {
            cursor.style.transform = 'translate(-50%, -50%) scale(0.7)';
            cursor.style.backgroundColor = 'rgba(239, 68, 68, 0.7)';
            cursor.style.borderColor = '#f87171';
        });
        window.addEventListener('mouseup', () => {
            cursor.style.transform = 'translate(-50%, -50%) scale(1)';
            cursor.style.backgroundColor = 'rgba(99, 102, 241, 0.45)';
            cursor.style.borderColor = '#818cf8';
        });
    }""")

def smooth_mouse_move(page, target_locator, steps=15):
    """Moves the mouse smoothly towards an element to mimic a human user."""
    box = target_locator.bounding_box()
    if not box:
        return
    dest_x = box["x"] + box["width"] / 2
    dest_y = box["y"] + box["height"] / 2
    page.mouse.move(dest_x, dest_y, steps=steps)
    page.wait_for_timeout(150)

def record_walkthrough():
    from playwright.sync_api import sync_playwright
    
    server = start_server()
    VIDEO_RECORD_DIR.mkdir(parents=True, exist_ok=True)

    print("🎬 Starting Actual Screen Recording Walkthrough...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--font-render-hinting=medium", "--enable-font-antialiasing"]
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            record_video_dir=str(VIDEO_RECORD_DIR),
            record_video_size={"width": 1440, "height": 900}
        )
        page = context.new_page()

        # Step 1: Open Landing Page
        print("  [1/9] Opening Sanctuary OS Landing Page...")
        page.goto(BASE_URL, wait_until="networkidle")
        inject_cursor_overlay(page)
        page.wait_for_timeout(1200)

        # Move to Guest Evaluator button and click
        guest_btn = page.locator("#guest-signin-btn")
        if guest_btn.is_visible():
            smooth_mouse_move(page, guest_btn)
            page.wait_for_timeout(400)
            guest_btn.click()
        else:
            # Fallback test sign-in
            page.evaluate("() => { if (window.__SANCTUARY_TEST_AUTH__) { window.__SANCTUARY_TEST_AUTH__.signIn('victor_kyaw', 'victor@sanctuary.test', 'Victor Kyaw'); } }")
        
        page.wait_for_selector("#app-shell:not(.hidden)", timeout=6000)
        inject_cursor_overlay(page)
        page.wait_for_timeout(1500)

        # Step 2: Persona Mode Switching
        print("  [2/9] Selecting Persona Style (Actionable Strategy)...")
        pill = page.locator("#mode-selector-pill")
        smooth_mouse_move(page, pill)
        pill.click()
        page.wait_for_selector("#mode-dropdown-menu:not(.hidden)", timeout=3000)
        page.wait_for_timeout(600)

        card_actionable = page.locator('.reflection-style-card[data-style="actionable"]')
        smooth_mouse_move(page, card_actionable)
        page.wait_for_timeout(400)
        card_actionable.click()
        page.wait_for_timeout(800)

        # Step 3: Realistic Character-by-Character Typing
        print("  [3/9] Typing Burmese & English Executive Reflection...")
        input_box = page.locator("#reflection-input")
        smooth_mouse_move(page, input_box)
        input_box.click()
        page.wait_for_timeout(300)

        journal_thought = "Cloud Run ပေါ်မှာ Sanctuary OS ကို အောင်မြင်စွာ Deploy လုပ်နိုင်ခဲ့တယ်။ System ရဲ့ Security Constitution နဲ့ Firestore Multi-Tenancy ကို စစ်ဆေးပြီးပြီ။ Executive tasks တွေ plan လုပ်ချင်တယ်။"
        input_box.type(journal_thought, delay=35)
        page.wait_for_timeout(800)

        # Submit Reflection
        send_btn = page.locator("#send-reflection-btn")
        smooth_mouse_move(page, send_btn)
        send_btn.click()

        # Step 4: Await Gemini Reflection & Action Proposal
        print("  [4/9] Waiting for Gemini reflection & HITL Action Proposal...")
        page.wait_for_selector("#chat-stream .model-badge", timeout=8000)
        page.wait_for_timeout(1500)

        # Smooth scroll to read Gemini response
        page.mouse.wheel(0, 300)
        page.wait_for_timeout(1200)

        # Hover and Approve HITL Proposal if visible
        proposal_container = page.locator("#action-proposal-container")
        if proposal_container.is_visible():
            print("  [HITL Gate] Gemini proposed structured action. Approving...")
            approve_btn = page.locator("#proposal-approve-btn")
            smooth_mouse_move(page, approve_btn)
            page.wait_for_timeout(800)
            approve_btn.click()
            page.wait_for_timeout(1500)

        # Step 5: Auto-Summarize & Firestore Save
        print("  [5/9] Distilling Breakthrough Summary & Saving to Firestore...")
        summarize_btn = page.locator("#auto-summarize-btn")
        if summarize_btn.is_visible():
            smooth_mouse_move(page, summarize_btn)
            summarize_btn.click()
            page.wait_for_timeout(1500)

        save_btn = page.locator("#save-session-btn")
        if save_btn.is_visible():
            smooth_mouse_move(page, save_btn)
            save_btn.click()
            page.wait_for_timeout(1200)

        # Step 6: Switch to Executive Kanban Board
        print("  [6/9] Navigating to Executive Kanban Board...")
        nav_kanban = page.locator("#nav-kanban")
        smooth_mouse_move(page, nav_kanban)
        nav_kanban.click()
        page.wait_for_selector("#view-kanban-content:not(.hidden)", timeout=3000)
        page.wait_for_timeout(1500)

        # Hover over kanban columns
        columns = page.locator(".kanban-column")
        if columns.count() > 0:
            smooth_mouse_move(page, columns.first)
            page.wait_for_timeout(800)
            if columns.count() > 1:
                smooth_mouse_move(page, columns.nth(1))
                page.wait_for_timeout(800)

        # Step 7: Switch to Mindful Calendar & Emotional Arc
        print("  [7/9] Viewing Mindful Calendar & Emotional Trajectory Arc...")
        nav_cal = page.locator("#nav-calendar")
        smooth_mouse_move(page, nav_cal)
        nav_cal.click()
        page.wait_for_selector("#view-calendar-content:not(.hidden)", timeout=3000)
        page.wait_for_timeout(1800)

        # Step 8: Switch to Life Rewind
        print("  [8/9] Checking Life Rewind Cognitive & Productivity Metrics...")
        nav_rewind = page.locator("#nav-rewind")
        smooth_mouse_move(page, nav_rewind)
        nav_rewind.click()
        page.wait_for_selector("#view-rewind-content:not(.hidden)", timeout=3000)
        page.wait_for_timeout(2000)

        # Step 9: Evening Shutdown Ritual & Zen Confirmation
        print("  [9/9] Performing Evening Shutdown Ritual & Zen State...")
        nav_shutdown = page.locator("#nav-shutdown")
        smooth_mouse_move(page, nav_shutdown)
        nav_shutdown.click()
        page.wait_for_selector("#shutdown-modal", state="visible", timeout=3000)
        page.wait_for_timeout(1000)

        gratitude_input = page.locator("#shutdown-gratitude-input")
        if gratitude_input.is_visible():
            smooth_mouse_move(page, gratitude_input)
            gratitude_input.click()
            gratitude_input.type("Sanctuary OS Cloud Run deployment အောင်မြင်စွာ ပြီးမြောက်ခြင်း။", delay=35)
            page.wait_for_timeout(800)

        zen_btn = page.locator("#confirm-shutdown-btn")
        if zen_btn.is_visible():
            smooth_mouse_move(page, zen_btn)
            zen_btn.click()
            page.wait_for_timeout(2500)

        # End session
        page.wait_for_timeout(1000)
        video_path = page.video.path()
        print(f"  ✓ Playwright raw screen recording saved: {video_path}")
        
        context.close()
        browser.close()

    # Convert recorded webm to crystal-clear MP4 and GIF
    convert_video(video_path)

def convert_video(webm_path):
    print("🎬 Converting Screen Recording to 1080p MP4 & Optimized GIF...")
    
    # 1. High-definition MP4
    cmd_mp4 = [
        "ffmpeg", "-y",
        "-i", str(webm_path),
        "-vf", "scale=1440:900,format=yuv420p",
        "-r", "30",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(OUTPUT_MP4)
    ]
    subprocess.run(cmd_mp4, check=True)
    size_mb = OUTPUT_MP4.stat().st_size / (1024 * 1024)
    print(f"  ✅ High-Definition MP4 Generated: {OUTPUT_MP4} ({size_mb:.2f} MB)")

    # 2. Optimized GIF for GitHub README
    cmd_gif = [
        "ffmpeg", "-y",
        "-i", str(OUTPUT_MP4),
        "-vf", "fps=8,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer",
        str(OUTPUT_GIF)
    ]
    subprocess.run(cmd_gif, check=True)
    gif_mb = OUTPUT_GIF.stat().st_size / (1024 * 1024)
    print(f"  ✅ GitHub Walkthrough GIF Generated: {OUTPUT_GIF} ({gif_mb:.2f} MB)")

if __name__ == "__main__":
    record_walkthrough()
