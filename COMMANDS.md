# Command reference

All commands run from the project folder. Global flags come before the command:

```text
python company.py [--backend local|grokbot] [--state PATH] <command> ...
```

`--backend local` (default) is free and offline. `--backend grokbot` sends the
same orders to real Grok Bot agents through the `gbot` CLI.

## org

Show the org chart.

```sh
python company.py org
```

## assign

Give a task to one department agent.

```sh
python company.py assign --department engineering --task "Build the landing page"
```

Departments: `executive`, `engineering`, `marketing`, `finance`, `operations`.
In local mode the agent returns a finished deliverable and records it in the
state file. In grokbot mode the task is sent to that agent's Grok Bot.

## standup

Latest task status per department.

```sh
python company.py standup
```

## board-meeting

Run a board meeting round. Local mode: every department head reports numbers.
Grok Bot mode: the agenda goes to the Boardroom group.

```sh
python company.py board-meeting
python company.py --backend grokbot board-meeting --agenda "Q1 planning"
```

## report

CEO report: totals plus a department breakdown.

```sh
python company.py report
```

## status

Show backend, whether `gbot` is installed, and how many tasks are recorded.

```sh
python company.py status
```

## grok-sync

One-time Grok Bot setup: creates the five agents (with their `agents/*.md`
instructions) and the Boardroom group.

```sh
python company.py --backend grokbot grok-sync
```

Requires `npm install --global grok-bot-cli` and a signed-in Grok Bot desktop
app. The `scripts/setup_grokbot.sh` and `scripts/setup_grokbot.ps1` helpers
run the full sequence.

## agency-import

Import specialist agents from an Agency Agents roster folder (for example a
clone of your agency-agents fork). Scans recursively for agent `.md` files and
registers each one; running it again only adds new agents.

```sh
git clone https://github.com/ganeshsavara61-netizen/agency-agents
python company.py agency-import --roster agency-agents
```

## agency-list

List the imported specialist agents with a one-line summary of each.

```sh
python company.py agency-list
```
