# Autonomous Company

Run a small AI company from your terminal, CEO style. You give the orders;
five department agents - CEO, CTO, CMO, CFO and COO - turn them into
deliverables. Built to plug into **Grok Bot** (xAI's named AI teammates)
through the `gbot` CLI, and it also ships with a **free offline mode** that
runs anywhere with plain Python, and a bridge that hires the specialist
roster from your Agency Agents fork.

- You are the CEO. The agents work for you.
- Every command below is real and tested (12 automated tests, all passing).
- Free to build, copy and run in local mode. No paid API is needed for local mode.

## The company

| Agent  | Role | Department |
| ------ | ---- | ---------- |
| Chief  | Chief Executive Officer | executive |
| Forge  | Chief Technology Officer | engineering |
| Signal | Chief Marketing Officer | marketing |
| Ledger | Chief Financial Officer | finance |
| Flow   | Chief Operating Officer | operations |

## Requirements

- **Local mode (free, default):** Python 3.9+ only. Works on Windows, macOS and Linux.
- **Grok Bot mode:** Node.js 22+, the Grok Bot desktop app installed and signed
  in, and the `gbot` CLI (`npm install --global grok-bot-cli`). Grok Bot access
  currently requires a paid plan from xAI/Cursor (for example SuperGrok or an
  eligible Cursor plan). Check your own plan in the Grok Bot app.

## Quick start (free local mode)

```sh
git clone https://github.com/ganeshsavara61-netizen/autonomous-company.git
cd autonomous-company

# see your company
python company.py org

# give an order (CEO style)
python company.py assign --department engineering --task "Build the landing page"

# run the daily standup and a board meeting
python company.py standup
python company.py board-meeting

# CEO report
python company.py report
```

On Windows use `python` (or `py`) instead of `python3`. No install step, no
packages, no keys.

## Grok Bot mode (real AI teammates)

When you have Grok Bot access:

```sh
# one-time setup: installs gbot, creates the 5 agents and the Boardroom group
bash scripts/setup_grokbot.sh        # Windows: scripts\setup_grokbot.ps1

# now orders go to real Grok Bot agents
python company.py --backend grokbot assign --department marketing --task "Draft the launch post"
python company.py --backend grokbot board-meeting --agenda "Launch readiness review"
```

Each agent's personality and rules live in `agents/*.md` and are pushed into
the Grok Bot agent's Instructions field during setup.

## All commands

See [COMMANDS.md](COMMANDS.md) for the full reference. The short list:

```text
org            show the org chart
assign         give a task to a department agent
standup        latest task status per department
board-meeting  run a board meeting round
report         CEO report: totals and department breakdown
status         backend and gbot availability
grok-sync      create the company as real Grok Bot agents (needs gbot)
```

## Hire the whole Agency (your agency-agents fork)

This company plugs straight into your fork of
[Agency Agents](https://github.com/ganeshsavara61-netizen/agency-agents)
(upstream: [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents),
MIT licensed) - a roster of specialist AI agents (frontend wizards, Reddit
community ninjas, reality checkers and more). Import the roster and they join
your company payroll:

```sh
git clone https://github.com/ganeshsavara61-netizen/agency-agents
python company.py agency-import --roster agency-agents
python company.py agency-list
```

The five executives run the departments; the imported specialists are the
talent pool you can point Grok Bot at as you grow.

## Honest limits

- Local mode produces structured deliverables (plans, briefs, cost sheets) from
  deterministic templates. It is a working command system, not a large language
  model.
- Grok Bot mode sends your orders to real AI agents, but only while your Grok
  Bot plan and app are active. This repo cannot create Grok Bot access.
- The agents do not run a real business: no customers are contacted, no money
  moves, nothing is published. That stays with you, the CEO.

## Tests

```sh
python -m unittest discover -s tests -v
```

## License

MIT - see [LICENSE](LICENSE).
