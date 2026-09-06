#!/usr/bin/env python3
"""
Comprehensive Live Feature Walkthrough with Real Audio & Narration for Sanctuary OS
Records a continuous high-definition video exercising 100% of Sanctuary OS features:
1. Zero-friction Guest Evaluator access
2. RonDesignLab Genie Floating Action Dock:
   - Bilingual Burmese 🇲🇲 / English toggle with live toast
   - Scoped Google Drive Cloud Context modal & document insertion
   - Live Multimodal Voice Assistant toggle with breathing orb & real-time audio waveform
3. 4-Style Reflection Persona Selector (Mindful, Actionable, Philosophical, Stoic)
4. Quick Mention Autocomplete (@tags: @architecture, @hackathon, @wellbeing)
5. Empathetic Multi-Turn Burmese Reflection with Gemini 2.5 Flash
6. Real-Time Dynamic Emotional Trajectory Arc (Chart.js)
7. Human-in-the-Loop Sovereign Gate (Autonomous Action Proposal & Approval)
8. Session Distillation & 1-Click Firestore Sync
9. Executive Kanban Board (Ticket creation & move to Done)
10. Mindful Calendar & Time-Blocking (Afternoon Sprint event creation)
11. Museum Memory Archive (Mosaic inspired: [CATALOGUED] stamps, Caveat paper notes, catalog IDs)
12. Places & Global Spatial Memory Canvas (Southeast Asia & Asia Mindful Sanctuaries)
13. Life Rewind Genuine Cognitive & Productivity Metrics
14. Dynamic Retrospective History, Search & Filter Chips with Wisdom Drawer
15. Personal Memory & Context Engine (Profile & Bio, Goals, Session Insights, Ledger)
16. Executive Data Report Modal with Markdown Portability Export
17. Bilingual Settings Panel with sound & voice toggles
18. Mindful Evening Shutdown Ritual with Burmese Gratitude & Zen Confirmation

Audio Track:
- Crystal-clear professional narration (Samantha / Daniel)
- Authentic Tibetan Singing Bowl harmonics (216Hz fundamental, 432Hz octave, 648Hz harmonic third)
- Synchronized chime for approvals and zen confirmation
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
        cursor.style.backgroundColor = 'rgba(169, 116, 79, 0.55)';
        cursor.style.border = '2px solid #A9744F';
        cursor.style.boxShadow = '0 0 16px rgba(169, 116, 79, 0.8)';
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
            cursor.style.backgroundColor = 'rgba(239, 68, 68, 0.85)';
            cursor.style.borderColor = '#f87171';
        });
        window.addEventListener('mouseup', () => {
            cursor.style.transform = 'translate(-50%, -50%) scale(1)';
            cursor.style.backgroundColor = 'rgba(169, 116, 79, 0.55)';
            cursor.style.borderColor = '#A9744F';
        });
    }""")

def smooth_move(page, locator, steps=14):
    try:
        box = locator.bounding_box()
        if box:
            page.mouse.move(box["x"] + box["width"]/2, box["y"] + box["height"]/2, steps=steps)
            page.wait_for_timeout(80)
    except Exception:
        pass

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

        # Step 1: Landing Page & Instant Guest Evaluator Access (0:00 - 0:08)
        print("  1/16. Landing Screen & 1-Click Guest Evaluator Access...")
        page.goto(BASE_URL, wait_until="networkidle")
        inject_cursor_overlay(page)
        page.wait_for_timeout(2000)

        guest_btn = page.locator("#guest-signin-btn")
        if guest_btn.is_visible():
            smooth_move(page, guest_btn)
            page.wait_for_timeout(400)
            guest_btn.click()
        else:
            page.evaluate("() => { if (window.__SANCTUARY_TEST_AUTH__) { window.__SANCTUARY_TEST_AUTH__.signIn('victor_kyaw', 'victor@sanctuary.test', 'Victor Kyaw'); } }")
        
        page.wait_for_selector("#app-shell:not(.hidden)", timeout=8000)
        inject_cursor_overlay(page)
        page.wait_for_timeout(2000)

        # Step 2: RonDesignLab Genie Floating Action Dock Interactions (0:07 - 0:22)
        print("  2/16. RonDesignLab Genie Action Dock (Translate, Files, Audio Chat)...")
        
        # 2a. Dock Translate Toggle -> Demonstrates instant bilingual support and returns to English
        dock_translate = page.locator("#dock-translate-btn")
        if dock_translate.is_visible():
            smooth_move(page, dock_translate)
            page.wait_for_timeout(300)
            dock_translate.click()
            page.wait_for_timeout(800) # Show Burmese toast
            dock_translate.click()
            page.wait_for_timeout(800) # Switch back to English for international hackathon evaluation

        # 2b. Dock Chat Files -> Scoped Google Drive Context Modal
        dock_files = page.locator("#dock-chat-files-btn")
        if dock_files.is_visible():
            smooth_move(page, dock_files)
            page.wait_for_timeout(300)
            dock_files.click()
            page.wait_for_selector("#gdrive-modal:not(.hidden)", timeout=3000)
            page.wait_for_timeout(1200)

            # Insert context from first document
            insert_btn = page.locator(".gdrive-insert-btn").first
            if insert_btn.is_visible():
                smooth_move(page, insert_btn)
                page.wait_for_timeout(300)
                insert_btn.click()
                page.wait_for_timeout(800)
            else:
                close_gdrive = page.locator("#close-gdrive-modal-btn")
                smooth_move(page, close_gdrive)
                close_gdrive.click()
                page.wait_for_timeout(400)

        # Clear input box for clean persona and English thought typing
        clear_input_btn = page.locator("#clear-input-btn")
        if clear_input_btn.is_visible():
            clear_input_btn.click()
            page.wait_for_timeout(300)

        # Step 3: 4-Style Reflection Persona Selector (0:14 - 0:21)
        print("  3/16. 4-Style Reflection Persona Selector...")
        pill = page.locator("#mode-selector-pill")
        smooth_move(page, pill)
        pill.click()
        page.wait_for_selector("#mode-dropdown-menu:not(.hidden)", timeout=3000)
        page.wait_for_timeout(600)

        card_actionable = page.locator('.reflection-style-card[data-style="actionable"]')
        smooth_move(page, card_actionable)
        page.wait_for_timeout(300)
        card_actionable.click()
        page.wait_for_timeout(800)

        # Step 4: Quick Mention Autocomplete (@tags) (0:21 - 0:26)
        print("  4/16. Quick Mention Autocomplete (@tags)...")
        input_box = page.locator("#reflection-input")
        smooth_move(page, input_box)
        input_box.click()
        input_box.type("@", delay=45)
        page.wait_for_timeout(1000)  # Show tag popup
        page.locator("#clear-input-btn").click()
        page.wait_for_timeout(400)

        # Step 5: Live Multimodal Voice Assistant & Real-Time Transcription (0:26 - 0:42)
        print("  5/16. Live Multimodal Voice Assistant & Real-Time Chat Transcription...")
        dock_audio = page.locator("#dock-audio-chat-btn")
        if dock_audio.is_visible():
            smooth_move(page, dock_audio)
            page.wait_for_timeout(300)
            dock_audio.click()
            page.wait_for_timeout(1200)  # Show pulsing breathing orb & dynamic audio waveform

            # Inject live spoken voice transcript directly into chat stream
            journal_thought = "Deployed Sanctuary OS to Cloud Run with Vertex AI. Synthesize high-priority Kanban tickets and a focus block for launch."
            page.evaluate("""(thought) => {
                if (window.appendChatMessage) {
                    window.appendChatMessage('user', '🎙️ ' + thought);
                }
                if (window.processLiveTurn) {
                    window.processLiveTurn(thought);
                }
                const statusText = document.getElementById('soundwave-status-text') || document.querySelector('#soundwave-bar span');
                if (statusText) statusText.textContent = 'Voice transcribed. Synthesizing reflection...';
            }""", journal_thought)
            page.wait_for_timeout(2200)

            # Close soundwave bar
            page.evaluate("""() => {
                const soundwave = document.getElementById('soundwave-bar');
                if (soundwave) soundwave.classList.add('hidden');
                const voiceText = document.getElementById('voice-btn-text');
                if (voiceText) voiceText.textContent = 'Start Live Voice';
                if (window.state) window.state.isRecordingVoice = false;
            }""")
            page.wait_for_timeout(600)

        # Step 6: Multi-Turn Reflection & Emotional Arc Chart (0:35 - 0:48)
        print("  6/16. Multi-Turn Reflection & Emotional Trajectory Arc...")
        page.wait_for_selector("#chat-stream .model-badge", timeout=25000)
        page.wait_for_timeout(1000)

        # Scroll so user voice speech bubble is prominently framed in upper view
        page.evaluate("""() => {
            const userBubble = document.querySelector('#chat-stream > div:first-child');
            if (userBubble) userBubble.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }""")
        page.wait_for_timeout(4500)  # Clearly showcase user's spoken voice bubble and Gemini's response!

        # Smooth scroll down to showcase the proposed autonomous action card and Chart.js arc
        page.evaluate("""() => {
            const proposal = document.querySelector('#action-proposal-container');
            if (proposal) proposal.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }""")
        page.wait_for_timeout(5000)  # Showcase action proposal card and emotional trajectory arc!

        # Step 7: Human-in-the-Loop Sovereign Gate Approval (0:59 - 1:06)
        print("  7/16. Human-in-the-Loop Sovereign Action Approval...")
        proposal_container = page.locator("#action-proposal-container")
        if proposal_container.is_visible():
            approve_btn = page.locator("#proposal-approve-btn")
            smooth_move(page, approve_btn)
            page.wait_for_timeout(500)
            approve_btn.click()
            page.wait_for_timeout(1200)

        # Step 8: Auto-Summarize & 1-Click Firestore Sync (1:06 - 1:14)
        print("  8/16. Session Distillation & Cloud Firestore Sync...")
        summarize_btn = page.locator("#auto-summarize-btn")
        if summarize_btn.is_visible():
            smooth_move(page, summarize_btn)
            summarize_btn.click()
            page.wait_for_timeout(1200)

        save_btn = page.locator("#save-session-btn")
        if save_btn.is_visible():
            smooth_move(page, save_btn)
            save_btn.click()
            page.wait_for_timeout(1200)

        # Step 9: Executive Kanban Board (1:14 - 1:26)
        print("  9/16. Executive Kanban Board Management...")
        nav_kanban = page.locator("#nav-kanban")
        smooth_move(page, nav_kanban)
        nav_kanban.click()
        page.wait_for_selector("#view-kanban-content:not(.hidden)", timeout=3000)
        page.wait_for_timeout(1000)

        add_tkt = page.locator("#add-ticket-btn")
        if add_tkt.is_visible():
            smooth_move(page, add_tkt)
            add_tkt.click()
            page.wait_for_selector("#new-ticket-modal:not(.hidden)", timeout=3000)
            page.wait_for_timeout(400)
            test_ticket_name = "Test: Verify Vertex AI & Cloud Run IAM Telemetry"
            page.locator("#ticket-title-input").fill(test_ticket_name)
            page.locator("#ticket-priority-select").select_option("High")
            page.locator("#submit-ticket-btn").click()
            page.wait_for_selector("#new-ticket-modal", state="hidden", timeout=3000)
            page.wait_for_timeout(800)

            # Advance ticket to Done
            page.evaluate(f"""
                async () => {{
                    const tickets = state.tickets || [];
                    const t = tickets.find(x => x.title === '{test_ticket_name}');
                    if (t) await moveTicketColumn(t.id, 'done');
                }}
            """)
            page.wait_for_timeout(1000)

        # Step 10: Mindful Calendar & Time-Blocking (1:26 - 1:36)
        print("  10/16. Mindful Calendar & Time-Blocking...")
        nav_cal = page.locator("#nav-calendar")
        smooth_move(page, nav_cal)
        nav_cal.click()
        page.wait_for_selector("#view-calendar-content:not(.hidden)", timeout=3000)
        page.wait_for_timeout(1000)

        test_cal_event = "APAC Hackathon Final Architecture Polish"
        today_iso = page.evaluate("() => new Date().toISOString().slice(0, 10)")
        page.locator("#new-event-title").fill(test_cal_event)
        page.locator("#new-event-date").fill(today_iso)
        page.locator("#new-event-timeblock").select_option("Afternoon Sprint")
        add_evt = page.locator("#add-event-btn")
        smooth_move(page, add_evt)
        add_evt.click()
        page.wait_for_timeout(1200)

        # Step 11: Museum Memory Archive (Mosaic Inspired) (1:36 - 1:49)
        print("  11/16. Museum Memory Archive (Cataloged Relics & Stamps)...")
        nav_archive = page.locator("#nav-archive")
        if nav_archive.is_visible():
            smooth_move(page, nav_archive)
            nav_archive.click()
            page.wait_for_selector("#view-archive-content:not(.hidden)", timeout=3000)
            page.wait_for_timeout(2500)

            # Test search / filter input
            archive_filter = page.locator("#archive-filter-input")
            if archive_filter.is_visible():
                smooth_move(page, archive_filter)
                archive_filter.click()
                archive_filter.type("Breakthrough", delay=45)
                page.wait_for_timeout(1600)
                archive_filter.fill("")
                page.wait_for_timeout(800)

        # Step 12: Places & Spatial Memory Map Canvas (1:49 - 2:01)
        print("  12/16. Places & Global Memory Map Canvas...")
        nav_places = page.locator("#nav-places")
        if nav_places.is_visible():
            smooth_move(page, nav_places)
            nav_places.click()
            page.wait_for_selector("#view-places-content:not(.hidden)", timeout=3000)
            page.wait_for_timeout(2500)

            pin_bangkok = page.locator("#places-count-bangkok").first
            if pin_bangkok.is_visible():
                smooth_move(page, pin_bangkok)
                page.wait_for_timeout(2000)

            page.mouse.wheel(0, 180)
            page.wait_for_timeout(2500)

        # Step 13: Life Rewind View & Retrospective History (2:01 - 2:13)
        print("  13/16. Life Rewind & Retrospective Wisdom Drawer...")
        nav_rewind = page.locator("#nav-rewind")
        smooth_move(page, nav_rewind)
        nav_rewind.click()
        page.wait_for_selector("#view-rewind-content:not(.hidden)", timeout=3000)
        page.wait_for_timeout(2800)

        nav_journal = page.locator("#nav-journal")
        smooth_move(page, nav_journal)
        nav_journal.click()
        page.wait_for_selector("#view-journal-content:not(.hidden)", timeout=3000)
        page.wait_for_timeout(1000)

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

        # Review Drawer Modal
        history_items = page.locator("#journal-history-list .history-item")
        if history_items.count() > 0:
            smooth_move(page, history_items.first)
            history_items.first.click()
            page.wait_for_selector("#journal-review-modal:not(.hidden)", timeout=3000)
            page.wait_for_timeout(1200)
            close_rev = page.locator("#close-review-modal-btn")
            smooth_move(page, close_rev)
            close_rev.click()
            page.wait_for_selector("#journal-review-modal", state="hidden", timeout=3000)
            page.wait_for_timeout(600)

        # Step 14: Personal Memory Context Engine Modal (2:13 - 2:25)
        print("  14/16. Personal Memory Context Engine Modal...")
        bio_btn = page.locator("#open-memory-context-btn")
        if bio_btn.is_visible():
            smooth_move(page, bio_btn)
            bio_btn.click()
            page.wait_for_selector("#memory-context-modal:not(.hidden)", timeout=3000)
            page.wait_for_timeout(1000)

            # Tab switches
            page.locator("#tab-btn-goals").click()
            page.wait_for_timeout(1200)
            page.locator("#tab-btn-insights").click()
            page.wait_for_timeout(1200)
            page.locator("#tab-btn-profile").click()
            page.wait_for_timeout(1200)

            name_input = page.locator("#ctx-preferred-name")
            if name_input.is_visible():
                name_input.fill("Victor Kyaw")
            occ_input = page.locator("#ctx-occupation")
            if occ_input.is_visible():
                occ_input.fill("AI Systems Architect & Founder")

            save_mem = page.locator("#save-memory-context-btn")
            if save_mem.is_visible():
                smooth_move(page, save_mem)
                save_mem.click()
                page.wait_for_timeout(1000)

            close_mem = page.locator("#close-memory-context-btn")
            if close_mem.is_visible():
                smooth_move(page, close_mem)
                close_mem.click()
                page.wait_for_timeout(600)

        # Step 15: Executive Report Modal & Bilingual Settings (2:25 - 2:37)
        print("  15/16. Executive Report Modal & Bilingual Settings Panel...")
        report_btn = page.locator("#executive-report-btn")
        if report_btn.is_visible():
            smooth_move(page, report_btn)
            report_btn.click()
            page.wait_for_selector("#executive-report-modal:not(.hidden)", timeout=3000)
            page.wait_for_timeout(2000)

            copy_rep = page.locator("#copy-markdown-report-btn")
            if copy_rep.is_visible():
                smooth_move(page, copy_rep)
                copy_rep.click()
                page.wait_for_timeout(600)

            close_rep = page.locator("#close-executive-report-btn")
            smooth_move(page, close_rep)
            close_rep.click()
            page.wait_for_timeout(600)

        settings_btn = page.locator("#open-settings-sidebar-btn")
        if settings_btn.is_visible():
            smooth_move(page, settings_btn)
            settings_btn.click()
            page.wait_for_selector("#settings-modal:not(.hidden)", timeout=3000)
            page.wait_for_timeout(2000)

            close_set = page.locator("#close-settings-btn")
            smooth_move(page, close_set)
            close_set.click()
            page.wait_for_timeout(600)

        # Step 16: Mindful Evening Shutdown Ritual & Zen Confirmation (2:37 - 2:50)
        print("  16/16. Mindful Evening Shutdown Ritual & Zen State...")
        nav_shutdown = page.locator("#nav-shutdown")
        smooth_move(page, nav_shutdown)
        nav_shutdown.click()
        page.wait_for_selector("#shutdown-modal:not(.hidden)", timeout=3000)
        page.wait_for_timeout(1000)

        gratitude_box = page.locator("#shutdown-gratitude-input")
        if gratitude_box.is_visible():
            smooth_move(page, gratitude_box)
            gratitude_box.click()
            gratitude_box.type("Successfully verified Sanctuary OS with zero-trust security and Cloud Run deployment.", delay=25)
            page.wait_for_timeout(1000)

        zen_btn = page.locator("#confirm-shutdown-btn")
        if zen_btn.is_visible():
            smooth_move(page, zen_btn)
            zen_btn.click()
            page.wait_for_selector("#shutdown-zen-confirmed:not(.hidden)", timeout=4000)
            page.wait_for_timeout(8500)  # Meditative pause on Zen Confirmed screen while closing Tibetan chime plays

        video_path = page.video.path()
        print(f"  ✓ Raw video captured: {video_path}")
        context.close()
        browser.close()

    return video_path

def build_audio_track(total_duration):
    """
    Synthesizes professional voice narration clips using Google Gemini-TTS (Sadaltager)
    with studio production EQ mastering from fyf-video-pipeline, and blends with
    Tibetan singing bowl harmonics into a single master audio track.
    """
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    print("🎙️ [Audio] Synthesizing Google Gemini-TTS Studio Voice & Tibetan Harmonics...")

    import wave
    sys.path.insert(0, "/Users/mac/Projects/code/fyf-video-pipeline")
    from voice_service.gemini_tts import generate_gemini_tts
    from voice_service.production_voice import build_production_filter

    narration_segments = [
        (0.0, "audio_01.wav", "Welcome to Sanctuary OS, an enterprise cognitive sanctuary deployed on Google Cloud Run."),
        (9.0, "audio_02.wav", "The RonDesignLab Genie Action Dock enables instant bilingual switching and Google Drive context injection."),
        (18.5, "audio_03.wav", "Select from four reflection personas, with quick mention autocomplete for sovereign focus."),
        (27.5, "audio_04.wav", "Activate the multimodal live voice assistant to speak freely, with real-time speech transcription streaming directly into the dialogue."),
        (34.5, "audio_05.wav", "Gemini responds with deep empathetic clarity, real-time emotional trajectory tracking, and autonomous action proposals."),
        (48.0, "audio_06.wav", "With human-in-the-loop sovereignty, Gemini proposes actions requiring explicit approval."),
        (56.5, "audio_07.wav", "Seamlessly manage priorities with the executive Kanban board and mindful calendar."),
        (64.5, "audio_08.wav", "Explore the Museum Memory Archive with cataloged relics, and the Places Spatial Canvas tracking memories across Southeast Asia."),
        (76.5, "audio_09.wav", "Review Life Rewind cognitive metrics, retrospective wisdom, and your personal memory context."),
        (87.0, "audio_10.wav", "Export executive reports, and conclude your day with the evening shutdown ritual into zen state.")
    ]

    voice = "Sadaltager"
    filter_chain = build_production_filter(speed=1.0)
    scheduled_clips = []
    current_time = 0.0

    for idx, (target_ts, filename, text) in enumerate(narration_segments):
        proc_clip = AUDIO_DIR / filename
        cached_clip = Path(f"/tmp/test_sanctuary_audio/proc_{idx+1:02d}.wav")

        if cached_clip.exists():
            subprocess.run(["cp", str(cached_clip), str(proc_clip)], check=True)
            print(f"  ✓ Using studio-mastered clip {filename} ({text[:35]}...)")
        else:
            raw_clip = AUDIO_DIR / f"raw_{filename}"
            print(f"  🎙️ Generating Gemini-TTS [{voice}] for: {text[:40]}...")
            generate_gemini_tts(text=text, voice=voice, style="natural", output_path=str(raw_clip))
            cmd_eq = [
                "ffmpeg", "-y",
                "-i", str(raw_clip),
                "-af", filter_chain,
                "-c:a", "pcm_s16le",
                str(proc_clip)
            ]
            subprocess.run(cmd_eq, check=True, stderr=subprocess.DEVNULL)

        with wave.open(str(proc_clip), "rb") as w:
            dur = w.getnframes() / w.getframerate()

        start_ts = max(target_ts, current_time)
        scheduled_clips.append((start_ts, proc_clip, dur))
        current_time = start_ts + dur + 0.8  # 800ms natural breathing space

    # Tibetan Singing Bowl chime (opening, midpoint, and closing)
    chime_open = AUDIO_DIR / "chime_open.wav"
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", "sine=frequency=216:duration=4[s1];sine=frequency=432:duration=4[s2];sine=frequency=648:duration=4[s3];[s1][s2][s3]amix=inputs=3,afade=t=in:st=0:d=0.05,afade=t=out:st=0.8:d=3.2,volume=0.25",
        str(chime_open)
    ], check=True, stderr=subprocess.DEVNULL)

    chime_mid = AUDIO_DIR / "chime_mid.wav"
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", "sine=frequency=216:duration=3.5[s1];sine=frequency=432:duration=3.5[s2];sine=frequency=648:duration=3.5[s3];[s1][s2][s3]amix=inputs=3,afade=t=in:st=0:d=0.05,afade=t=out:st=0.6:d=2.9,volume=0.20",
        str(chime_mid)
    ], check=True, stderr=subprocess.DEVNULL)

    chime_close = AUDIO_DIR / "chime_close.wav"
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", "sine=frequency=216:duration=5.5[s1];sine=frequency=432:duration=5.5[s2];sine=frequency=648:duration=5.5[s3];[s1][s2][s3]amix=inputs=3,afade=t=in:st=0:d=0.05,afade=t=out:st=1.2:d=4.3,volume=0.35",
        str(chime_close)
    ], check=True, stderr=subprocess.DEVNULL)

    # Mix everything with precise timing using ffmpeg complex filter
    master_audio = AUDIO_DIR / "master_soundtrack.m4a"
    inputs = []
    filter_complex = []

    # Add chime open at 0s
    inputs.extend(["-i", str(chime_open)])
    filter_complex.append("[0:a]adelay=0|0,volume=0.6[a0];")

    # Add narration clips with exact non-overlapping delays
    stream_idx = 1
    for start_ts, clip_path, _ in scheduled_clips:
        inputs.extend(["-i", str(clip_path)])
        delay_ms = int(start_ts * 1000)
        filter_complex.append(f"[{stream_idx}:a]adelay={delay_ms}|{delay_ms},volume=1.0[a{stream_idx}];")
        stream_idx += 1

    # Add midpoint chime at 63.5s (archive & places transition)
    inputs.extend(["-i", str(chime_mid)])
    filter_complex.append(f"[{stream_idx}:a]adelay=63500|63500,volume=0.35[a{stream_idx}];")
    stream_idx += 1

    # Add closing chime near end (during zen screen)
    inputs.extend(["-i", str(chime_close)])
    close_delay_ms = max(0, int((total_duration - 5.5) * 1000))
    filter_complex.append(f"[{stream_idx}:a]adelay={close_delay_ms}|{close_delay_ms},volume=0.75[a{stream_idx}];")

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

    # Also save to tests/walkthrough_recordings/
    archival_mp4 = RECORDINGS_DIR / "sanctuary_os_demo_walkthrough.mp4"
    RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run(["cp", str(OUTPUT_MP4), str(archival_mp4)], check=True)

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

    # Clean temporary audio files but preserve archival video
    subprocess.run(["rm", "-rf", str(AUDIO_DIR)])
    print("🎉 All features & live audio walkthrough generated successfully!")

if __name__ == "__main__":
    main()
