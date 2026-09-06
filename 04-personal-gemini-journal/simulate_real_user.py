#!/usr/bin/env python3
"""
Root runner for realistic human user browser simulation.
Enables `uv run python simulate_real_user.py` to execute directly from project root.
"""
import os
import sys

# Ensure current directory is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from tests.simulate_real_user import run_real_user_simulation

if __name__ == "__main__":
    run_real_user_simulation()
