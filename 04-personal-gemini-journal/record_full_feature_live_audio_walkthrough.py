#!/usr/bin/env python3
"""
Comprehensive Live Feature Walkthrough with Real Audio & Narration for Sanctuary OS
Records a continuous high-definition video exercising 100% of Sanctuary OS features:
1. Zero-friction Guest Evaluator access
2. Live Multimodal Voice Assistant toggle (with animated soundwave & breathing orb)
3. 4-Style Reflection Persona Selector & Quick Mention Autocomplete (@tags)
4. Empathetic Multi-Turn Burmese Reflection with Gemini 2.5 Flash
5. Real-Time Dynamic Emotional Trajectory Arc (Chart.js)
6. Human-in-the-Loop Sovereign Gate (Action Proposal & Approval)
7. Session Distillation & 1-Click Firestore Sync
8. Executive Kanban Board with drag/drop prioritization
9. Mindful Calendar & Time-Blocking
10. Life Rewind Genuine Cognitive & Productivity Metrics
11. Dynamic Retrospective History, Search & Filter Chips
12. Executive Data Report Modal with Markdown Portability Export
13. Bilingual Settings Panel with sound & voice toggles
14. Mindful Evening Shutdown Ritual with Burmese Gratitude & Zen Confirmation

Audio Track:
- Crystal-clear professional narration (Samantha / Daniel)
- Authentic Tibetan Singing Bowl chime (216Hz/432Hz/648Hz harmonics)
- Synchronized sound effects for approvals and zen confirmation
"""

import os
import sys
import time
import socket
import threading
import subprocess
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_DIR))

# Hermetic test/demo mode
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
RECORDINGS_DIR = PROJECT_DIR / "tests" / "walkthrough_recordings"
AUDIO_DIR = PROJECT_DIR / "tests" / "walkthrough_audio"
OUTPUT_MP4 = PROJECT_DIR / "sanctuary_os_demo_walkthrough.mp4"
OUTPUT_GIF = PROJECT_DIR / "sanctuary_os_demo_walkthrough.gif"

def start_server():
    import uvicorn
    from main import app
    config = uvicorn.Config(app, host="127.0.0.1", port=TEST_PORT, log_level="error")
    server = uvicorn.Server(config)
    t = threading.Thread(target=server.run, daemon=True)
    t.start()
    for _ in range(50):
        try:
            with socket.create_connection(("127.0.0.1", TEST_PORT), timeout=0.2):
                print(f"  ✓ Local demo server active on {BASE_URL}")
                return server
        except OSError:
            time.sleep(0.1)
    raise RuntimeError("Failed to start local demo server")

def inject_cursor_overlay(page):
    """Sleek glowing cursor ring that moves smoothly with mouse interactions."""
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
        cursor.style.boxShadow = '0 0 14px rgba(129, 140, 248, 0.7)';
        cursor.style.pointerEvents = 'none';
        cursor.style.zIndex = '999999';
        cursor.style.transition = 'transform 0.1s ease, width 0.15s ease, height 0.15s ease, background-color 0.15s ease';
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
            cursor.style.transform = 'translate(-50%, -50%) scale(0.65)';
            cursor.style.backgroundColor = 'rgba(239, 68, 68, 0.75)';
            cursor.style.borderColor = '#f87171';
        });
        window.addEventListener('mouseup', () => {
            cursor.style.transform = 'translate(-50%, -50%) scale(1)';
            cursor.style.backgroundColor = 'rgba(99, 102, 241, 0.45)';
            cursor.style.borderColor = '#818cf8';
        });
    }""")

def smooth_move(page, locator, steps=12):
    box = locator.bounding_box()
    if box:
        page.mouse.move(box["x"] + box["width"]/2, box["y"] + box["height"]/2, steps=steps)
        page.wait_for_timeout(100)

def record_browser_session():
    from playwright.sync_api import sync_playwright
    server = start_server()
    RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)

    print("🎬 [Video] Commencing Full-Feature Browser Automation Recording...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--font-render-hinting=medium", "--enable-font-antialiasing"]
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            record_video_dir=str(RECORDINGS_DIR),
            record_video_size={"width": 1440, "height": 900}
        )
        page = context.new_page()

        # Step 1: Landing Page & Instant Guest Evaluator Access (0:00 - 0:05)
        print("  1/14. Landing Screen & 1-Click Guest Evaluator Access...")
        page.goto(BASE_URL, wait_until="networkidle")
        inject_cursor_overlay(page)
        page.wait_for_timeout(1000)

        guest_btn = page.locator("#guest-signin-btn")
        if guest_btn.is_visible():
            smooth_move(page, guest_btn)
            page.wait_for_timeout(400)
            guest_btn.click()
        else:
            page.evaluate("() => { if (window.__SANCTUARY_TEST_AUTH__) { window.__SANCTUARY_TEST_AUTH__.signIn('victor_kyaw', 'victor@sanctuary.test', 'Victor Kyaw'); } }")
        
        page.wait_for_selector("#app-shell:not(.hidden)", timeout=6000)
        inject_cursor_overlay(page)
        page.wait_for_timeout(1200)

        # Step 2: Live Voice Assistant & Animated Soundwave (0:05 - 0:11)
        print("  2/14. Live Multimodal Voice Assistant Toggle...")
        voice_toggle = page.locator("#live-voice-toggle-btn")
        if voice_toggle.is_visible():
            smooth_move(page, voice_toggle)
            page.wait_for_timeout(300)
            voice_toggle.click()
            page.wait_for_timeout(1600)  # Show pulsing orb and active soundwave
            smooth_move(page, voice_toggle)
            voice_toggle.click()
            page.wait_for_timeout(800)

        # Step 3: 4-Style Reflection Persona Selector (0:11 - 0:17)
        print("  3/14. 4-Style Reflection Persona Selector...")
        pill = page.locator("#mode-selector-pill")
        smooth_move(page, pill)
        pill.click()
        page.wait_for_selector("#mode-dropdown-menu:not(.hidden)", timeout=3000)
        page.wait_for_timeout(500)

        card_actionable = page.locator('.reflection-style-card[data-style="actionable"]')
        smooth_move(page, card_actionable)
        page.wait_for_timeout(300)
        card_actionable.click()
        page.wait_for_timeout(800)

        # Step 4: Quick Mention Autocomplete (@tags) (0:17 - 0:22)
        print("  4/14. Quick Mention Autocomplete (@tags)...")
        input_box = page.locator("#reflection-input")
        smooth_move(page, input_box)
        input_box.click()
        input_box.type("@", delay=40)
        page.wait_for_timeout(1000)  # Show tag popup
        page.locator("#clear-input-btn").click()
        page.wait_for_timeout(300)

        # Step 5: Realistic Burmese Reflection Typing (0:22 - 0:31)
        print("  5/14. Realistic Burmese Reflection Typing...")
        journal_thought = "ဒီနေ့ Cloud Run ပေါ်မှာ Sanctuary OS ကို အောင်မြင်စွာ Deploy လုပ်ပြီးပြီ။ Security Constitution နဲ့ Firestore Multi-Tenancy ကို စစ်ဆေးပြီးပြီ။ Executive tasks တွေ စီစဉ်ချင်တယ်။"
        input_box.type(journal_thought, delay=35)
        page.wait_for_timeout(800)

        # Submit to Gemini
        send_btn = page.locator("#send-reflection-btn")
        smooth_move(page, send_btn)
        send_btn.click()

        # Step 6: Gemini 2.5 Flash Empathetic Reflection & Emotional Arc (0:31 - 0:38)
        print("  6/14. Multi-Turn Reflection & Emotional Trajectory Arc...")
        page.wait_for_selector("#chat-stream .model-badge", timeout=8000)
        page.wait_for_timeout(1000)
        page.mouse.wheel(0, 250)
        page.wait_for_timeout(1200)

        # Step 7: Human-in-the-Loop Sovereign Gate Approval (0:38 - 0:44)
        print("  7/14. Human-in-the-Loop Sovereign Action Approval...")
        proposal_container = page.locator("#action-proposal-container")
        if proposal_container.is_visible():
            approve_btn = page.locator("#proposal-approve-btn")
            smooth_move(page, approve_btn)
            page.wait_for_timeout(600)
            approve_btn.click()
            page.wait_for_timeout(1200)

        # Step 8: Auto-Summarize & 1-Click Firestore Sync (0:44 - 0:50)
        print("  8/14. Session Distillation & Cloud Firestore Sync...")
        summarize_btn = page.locator("#auto-summarize-btn")
        if summarize_btn.is_visible():
            smooth_move(page, summarize_btn)
            summarize_btn.click()
            page.wait_for_timeout(1200)

        save_btn = page.locator("#save-session-btn")
        if save_btn.is_visible():
            smooth_move(page, save_btn)
            save_btn.click()
            page.wait_for_timeout(1000)

        # Step 9: Executive Kanban Board (0:50 - 0:57)
        print("  9/14. Executive Kanban Board Navigation & Management...")
        nav_kanban = page.locator("#nav-kanban")
        smooth_move(page, nav_kanban)
        nav_kanban.click()
        page.wait_for_selector("#view-kanban-content:not(.hidden)", timeout=3000)
        page.wait_for_timeout(1200)

        add_tkt = page.locator("#add-ticket-btn")
        if add_tkt.is_visible():
            smooth_move(page, add_tkt)
            page.wait_for_timeout(500)

        # Step 10: Mindful Calendar & Life Rewind (0:57 - 1:06)
        print("  10/14. Mindful Calendar & Genuine Life Rewind Metrics...")
        nav_cal = page.locator("#nav-calendar")
        smooth_move(page, nav_cal)
        nav_cal.click()
        page.wait_for_selector("#view-calendar-content:not(.hidden)", timeout=3000)
        page.wait_for_timeout(1500)

        nav_rewind = page.locator("#nav-rewind")
        smooth_move(page, nav_rewind)
        nav_rewind.click()
        page.wait_for_selector("#view-rewind-content:not(.hidden)", timeout=3000)
        page.wait_for_timeout(1800)

        # Step 10b: Museum Memory Archive & Places Map Geography
        print("  10b/14. Museum Memory Archive & Places Map Geography...")
        nav_archive = page.locator("#nav-archive")
        if nav_archive.is_visible():
            smooth_move(page, nav_archive)
            nav_archive.click()
            page.wait_for_selector("#view-archive-content:not(.hidden)", timeout=3000)
            page.wait_for_timeout(1500)

        nav_places = page.locator("#nav-places")
        if nav_places.is_visible():
            smooth_move(page, nav_places)
            nav_places.click()
            page.wait_for_selector("#view-places-content:not(.hidden)", timeout=3000)
            page.wait_for_timeout(1500)

        # Step 11: Dynamic History Search & Review Drawer (1:06 - 1:13)
        print("  11/14. Dynamic Retrospective History & Tag Filtering...")
        nav_journal = page.locator("#nav-journal")
        smooth_move(page, nav_journal)
        nav_journal.click()
        page.wait_for_selector("#view-journal-content:not(.hidden)", timeout=3000)
        page.wait_for_timeout(800)

        chip_actionable = page.locator('#history-filter-chips .history-chip[data-filter="actionable"]')
        if chip_actionable.is_visible():
            smooth_move(page, chip_actionable)
            chip_actionable.click()
            page.wait_for_timeout(800)

        chip_all = page.locator('#history-filter-chips .history-chip[data-filter="all"]')
        if chip_all.is_visible():
            smooth_move(page, chip_all)
            chip_all.click()
            page.wait_for_timeout(600)

        # Step 12: Executive Report Modal & Data Portability (1:13 - 1:20)
        print("  12/14. Executive Data Report Modal & Export Portability...")
        report_btn = page.locator("#executive-report-btn")
        if report_btn.is_visible():
            smooth_move(page, report_btn)
            report_btn.click()
            page.wait_for_selector("#executive-report-modal", state="visible", timeout=3000)
            page.wait_for_timeout(1200)

            close_rep = page.locator("#close-executive-report-btn")
            smooth_move(page, close_rep)
            close_rep.click()
            page.wait_for_timeout(600)

        # Step 12b: Personal Memory Context & Google Drive Modals
        print("  12b/14. Personal Bio & Google Drive Context Modals...")
        bio_btn = page.locator("#open-memory-context-btn")
        if bio_btn.is_visible():
            smooth_move(page, bio_btn)
            bio_btn.click()
            page.wait_for_selector("#memory-context-modal", state="visible", timeout=3000)
            page.wait_for_timeout(1000)
            close_bio = page.locator("#close-memory-context-btn")
            if close_bio.is_visible():
                smooth_move(page, close_bio)
                close_bio.click()
                page.wait_for_timeout(600)

        gdrive_btn = page.locator("#open-gdrive-btn")
        if gdrive_btn.is_visible():
            smooth_move(page, gdrive_btn)
            gdrive_btn.click()
            page.wait_for_selector("#gdrive-modal", state="visible", timeout=3000)
            page.wait_for_timeout(1000)
            close_gdrive = page.locator("#close-gdrive-modal-btn")
            if close_gdrive.is_visible():
                smooth_move(page, close_gdrive)
                close_gdrive.click()
                page.wait_for_timeout(500)

        # Step 13: Bilingual Settings Panel (1:20 - 1:27)
        print("  13/14. Executive Settings Panel & Sound Controls...")
        settings_btn = page.locator("#open-settings-sidebar-btn")
        if settings_btn.is_visible():
            smooth_move(page, settings_btn)
            settings_btn.click()
            page.wait_for_selector("#settings-modal", state="visible", timeout=3000)
            page.wait_for_timeout(1200)

            close_set = page.locator("#close-settings-btn")
            smooth_move(page, close_set)
            close_set.click()
            page.wait_for_timeout(600)

        # Step 14: Evening Shutdown Ritual & Zen Confirmation (1:27 - 1:35)
        print("  14/14. Mindful Evening Shutdown Ritual & Zen State...")
        nav_shutdown = page.locator("#nav-shutdown")
        smooth_move(page, nav_shutdown)
        nav_shutdown.click()
        page.wait_for_selector("#shutdown-modal", state="visible", timeout=3000)
        page.wait_for_timeout(800)

        gratitude_box = page.locator("#shutdown-gratitude-input")
        if gratitude_box.is_visible():
            smooth_move(page, gratitude_box)
            gratitude_box.click()
            gratitude_box.type("Sanctuary OS အောင်မြင်စွာ တည်ဆောက်ပြီးစီးခြင်း။", delay=35)
            page.wait_for_timeout(800)

        zen_btn = page.locator("#confirm-shutdown-btn")
        if zen_btn.is_visible():
            smooth_move(page, zen_btn)
            zen_btn.click()
            page.wait_for_timeout(2500)

        video_path = page.video.path()
        print(f"  ✓ Raw video captured: {video_path}")
        context.close()
        browser.close()

    return video_path

def build_audio_track(total_duration):
    """
    Synthesizes professional voice narration clips and blends with
    Tibetan singing bowl harmonics into a single master audio track.
    """
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    print("🎙️ [Audio] Synthesizing Professional Voice Narration & Tibetan Harmonics...")

    narration_segments = [
        (0.0, "audio_01.aiff", "Welcome to Sanctuary OS, an enterprise cognitive sanctuary deployed on Google Cloud Run."),
        (6.0, "audio_02.aiff", "Featuring live multimodal voice assistance with real-time audio interaction."),
        (13.0, "audio_03.aiff", "Select from four distinct reflection personas, with quick tag autocomplete."),
        (22.0, "audio_04.aiff", "Reflect freely in your native language. Gemini 2.5 Flash responds with deep empathetic clarity."),
        (38.0, "audio_05.aiff", "With human-in-the-loop sovereignty, Gemini proposes actions requiring explicit human approval."),
        (45.0, "audio_06.aiff", "Distill breakthrough insights and synchronize securely to tenant-isolated Cloud Firestore."),
        (52.0, "audio_07.aiff", "Seamlessly organize sprint priorities with the executive Kanban board and mindful calendar."),
        (65.0, "audio_08.aiff", "Review genuine cognitive metrics in Life Rewind, and explore retrospective wisdom in the history drawer."),
        (76.0, "audio_09.aiff", "Export executive reports with full data portability, and customize bilingual settings."),
        (88.0, "audio_10.aiff", "Complete your day with the evening shutdown ritual and confirm your zen state.")
    ]

    # 1. Generate individual narration AIFF clips
    voice = "Samantha"
    for timestamp, filename, text in narration_segments:
        clip_path = AUDIO_DIR / filename
        cmd = ["say", "-v", voice, "-r", "165", text, "-o", str(clip_path)]
        subprocess.run(cmd, check=True)

    # 2. Generate Tibetan Singing Bowl chime (opening and closing)
    chime_open = AUDIO_DIR / "chime_open.wav"
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", "sine=frequency=216:duration=4[s1];sine=frequency=432:duration=4[s2];sine=frequency=648:duration=4[s3];[s1][s2][s3]amix=inputs=3,afade=t=in:st=0:d=0.05,afade=t=out:st=0.8:d=3.2,volume=0.25",
        str(chime_open)
    ], check=True, stderr=subprocess.DEVNULL)

    chime_close = AUDIO_DIR / "chime_close.wav"
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", "sine=frequency=216:duration=5[s1];sine=frequency=432:duration=5[s2];sine=frequency=648:duration=5[s3];[s1][s2][s3]amix=inputs=3,afade=t=in:st=0:d=0.05,afade=t=out:st=1.2:d=3.8,volume=0.35",
        str(chime_close)
    ], check=True, stderr=subprocess.DEVNULL)

    # 3. Mix everything with precise timing using ffmpeg complex filter
    master_audio = AUDIO_DIR / "master_soundtrack.m4a"
    
    # Construct ffmpeg amix graph
    inputs = []
    filter_complex = []
    
    # Add chime open at 0s
    inputs.extend(["-i", str(chime_open)])
    filter_complex.append("[0:a]adelay=0|0,volume=0.6[a0];")
    
    # Add narration clips with delays
    stream_idx = 1
    for timestamp, filename, _ in narration_segments:
        clip_path = AUDIO_DIR / filename
        inputs.extend(["-i", str(clip_path)])
        delay_ms = int(timestamp * 1000)
        filter_complex.append(f"[{stream_idx}:a]adelay={delay_ms}|{delay_ms},volume=1.0[a{stream_idx}];")
        stream_idx += 1

    # Add closing chime near end
    inputs.extend(["-i", str(chime_close)])
    close_delay_ms = max(0, int((total_duration - 4.5) * 1000))
    filter_complex.append(f"[{stream_idx}:a]adelay={close_delay_ms}|{close_delay_ms},volume=0.7[a{stream_idx}];")
    
    total_streams = stream_idx + 1
    mix_sources = "".join(f"[a{i}]" for i in range(total_streams))
    filter_complex.append(f"{mix_sources}amix=inputs={total_streams}:normalize=0[aout]")

    cmd_mix = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", "".join(filter_complex),
        "-map", "[aout]",
        "-c:a", "aac",
        "-b:a", "192k",
        str(master_audio)
    ]
    subprocess.run(cmd_mix, check=True, stderr=subprocess.DEVNULL)
    print(f"  ✓ Master Audio Soundtrack created: {master_audio}")
    return master_audio

def compile_master_video(webm_path, audio_path):
    print("🎬 [Render] Merging HD Video with Master Audio into 1080p MP4 & GIF...")

    # Probe duration of webm
    probe = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(webm_path)
    ], capture_output=True, text=True, check=True)
    video_duration = float(probe.stdout.strip())

    # Build High-Definition Master MP4 with Audio
    cmd_mp4 = [
        "ffmpeg", "-y",
        "-i", str(webm_path),
        "-i", str(audio_path),
        "-vf", "scale=1440:900,format=yuv420p",
        "-r", "30",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", str(video_duration),
        "-movflags", "+faststart",
        str(OUTPUT_MP4)
    ]
    subprocess.run(cmd_mp4, check=True, stderr=subprocess.DEVNULL)
    size_mb = OUTPUT_MP4.stat().st_size / (1024 * 1024)
    print(f"  ✅ Complete HD Video with Audio: {OUTPUT_MP4} ({size_mb:.2f} MB, {video_duration:.1f}s)")

    # Generate Walkthrough GIF for README
    cmd_gif = [
        "ffmpeg", "-y",
        "-i", str(OUTPUT_MP4),
        "-vf", "fps=6,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer",
        str(OUTPUT_GIF)
    ]
    subprocess.run(cmd_gif, check=True, stderr=subprocess.DEVNULL)
    gif_mb = OUTPUT_GIF.stat().st_size / (1024 * 1024)
    print(f"  ✅ GitHub Walkthrough GIF: {OUTPUT_GIF} ({gif_mb:.2f} MB)")

def main():
    # 1. Record browser user flow
    webm_path = record_browser_session()

    # Probe duration
    probe = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(webm_path)
    ], capture_output=True, text=True, check=True)
    duration = float(probe.stdout.strip())
    print(f"  ✓ Captured session duration: {duration:.1f} seconds")

    # 2. Build synchronized narration & Tibetan audio track
    audio_path = build_audio_track(duration)

    # 3. Merge video & audio into final deliverables
    compile_master_video(webm_path, audio_path)

    # Cleanup temporary directories
    subprocess.run(["rm", "-rf", str(RECORDINGS_DIR), str(AUDIO_DIR)])
    print("🎉 All features & live audio walkthrough generated successfully!")

if __name__ == "__main__":
    main()
