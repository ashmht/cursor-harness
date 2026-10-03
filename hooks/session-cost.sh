#!/bin/bash
# Wrapper for session-cost.py (Cursor hooks invoke shell, not python directly).
exec python3 "$(dirname "$0")/session-cost.py"
