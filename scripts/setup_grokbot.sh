#!/usr/bin/env bash
# Set up the Autonomous Company as real Grok Bot agents.
# Requires: Node.js 22+, the Grok Bot desktop app installed and signed in.
# Grok Bot access needs a paid xAI/Cursor plan - the app itself decides access.
set -euo pipefail

npm install --global grok-bot-cli
gbot bots list   # verifies the app session works

python3 company.py --experimental-grokbot --backend grokbot grok-sync

echo "Done. Open Grok Bot and check the Boardroom group."
