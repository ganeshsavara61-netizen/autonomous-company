# Set up the Autonomous Company as real Grok Bot agents (Windows PowerShell).
# Requires: Node.js 22+, the Grok Bot desktop app installed and signed in.
# Grok Bot access needs a paid xAI/Cursor plan - the app itself decides access.

npm install --global grok-bot-cli
gbot bots list   # verifies the app session works

python company.py --experimental-grokbot --backend grokbot grok-sync

Write-Host "Done. Open Grok Bot and check the Boardroom group."
