#!/usr/bin/env bash
# setup.sh — Bootstrap a virtual environment for the Pomodoro Timer
# Usage: ./setup.sh or bash setup.sh

set -e

echo "🍅 Setting up Pomodoro Timer..."
python3 -m venv venv

echo ""
echo "✅ Virtual environment created successfully!"
echo ""
echo "To activate and run:"
echo "  source venv/bin/activate"
echo "  python3 pomodoro.py"
echo ""
echo "— or run directly:"
echo "  ./venv/bin/python3 pomodoro.py"
