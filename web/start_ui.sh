#!/bin/bash
# S4 Multi-Agent Debate System - Web UI Launcher

echo "================================================================================"
echo " S4 MULTI-AGENT DEBATE SYSTEM - DARK RED CYBERPUNK UI"
echo "================================================================================"
echo ""
echo "Starting web server..."
echo ""

cd "$(dirname "$0")"
conda run -p ../venv python api.py
