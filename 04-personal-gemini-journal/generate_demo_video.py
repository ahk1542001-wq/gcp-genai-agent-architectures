#!/usr/bin/env python3
"""
Generates a high-definition Demo Walkthrough Video (MP4) and animated GIF
from the 26 human verification screenshots in tests/screenshots/human_walkthrough/.
"""

import os
import subprocess
from pathlib import Path

SCREENSHOTS_DIR = Path("tests/screenshots/human_walkthrough")
OUTPUT_MP4 = Path("sanctuary_os_demo_walkthrough.mp4")
OUTPUT_GIF = Path("sanctuary_os_demo_walkthrough.gif")

# Key sequence of slides for concise ~55s demo
SLIDES = [
    ("01_auth_landing.png", 2.5),
    ("02_authenticated_dashboard.png", 2.5),
    ("03_reflection_style_pill_selected.png", 2.0),
    ("03b_mention_autocomplete_popup.png", 2.0),
    ("04_reflection_input_typed.png", 2.0),
    ("05_turn1_completed.png", 2.5),
    ("06_hitl_proposal_displayed.png", 2.5),
    ("07_hitl_proposal_approved.png", 2.5),
    ("08_distilled_summary.png", 2.5),
    ("09_session_saved.png", 2.0),
    ("10_voice_active.png", 2.0),
    ("11_kanban_view.png", 2.5),
    ("11b_new_ticket_modal.png", 2.0),
    ("13_calendar_event_added.png", 2.5),
    ("14_life_rewind_view.png", 2.5),
    ("15_history_search_and_chips.png", 2.5),
    ("16_journal_review_drawer.png", 2.5),
    ("17_executive_report_modal.png", 2.5),
    ("18_settings_modal_open.png", 2.0),
    ("19_settings_saved_burmese.png", 2.0),
    ("20_shutdown_modal_gratitude.png", 2.5),
    ("21_shutdown_zen_confirmed.png", 2.5),
    ("22_export_dropdown_menu.png", 2.0),
]

def build_demo_video():
    print("🎬 Building Sanctuary OS Demo Video...")
    concat_file = Path("concat_slides.txt")
    
    with open(concat_file, "w") as f:
        for filename, duration in SLIDES:
            filepath = SCREENSHOTS_DIR / filename
            if filepath.exists():
                f.write(f"file '{filepath.resolve()}'\n")
                f.write(f"duration {duration}\n")
        if SLIDES:
            last_path = (SCREENSHOTS_DIR / SLIDES[-1][0]).resolve()
            f.write(f"file '{last_path}'\n")

    # Generate MP4
    cmd_mp4 = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-vf", "scale=1440:900,format=yuv420p",
        "-r", "25",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(OUTPUT_MP4)
    ]
    print(f"Running: {' '.join(cmd_mp4)}")
    subprocess.run(cmd_mp4, check=True)
    print(f"  ✓ MP4 created: {OUTPUT_MP4} ({OUTPUT_MP4.stat().st_size / 1024 / 1024:.2f} MB)")

    # Generate optimized GIF for README
    cmd_gif = [
        "ffmpeg", "-y",
        "-i", str(OUTPUT_MP4),
        "-vf", "fps=8,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer",
        str(OUTPUT_GIF)
    ]
    print(f"Running: {' '.join(cmd_gif)}")
    subprocess.run(cmd_gif, check=True)
    print(f"  ✓ GIF created: {OUTPUT_GIF} ({OUTPUT_GIF.stat().st_size / 1024 / 1024:.2f} MB)")

    if concat_file.exists():
        concat_file.unlink()

if __name__ == "__main__":
    build_demo_video()
