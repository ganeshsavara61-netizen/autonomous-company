#!/usr/bin/env python3
"""Autonomous Company - a CEO-style command center.

You are the CEO. This tool runs a small AI company of department agents.

Two backends:
  * local   (default, free, offline): deterministic department agents that
            turn your tasks into deliverables and keep a company state file.
  * grokbot: delegates to real Grok Bot agents through the `gbot` CLI
            (EXPERIMENTAL and untested; needs the Grok Bot desktop app signed in
            and a paid plan; must be enabled with --experimental-grokbot).

No third-party Python packages are required.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path

VERSION = "1.0.0"
DEFAULT_STATE_FILE = "company_state.json"
AGENTS_DIR = Path(__file__).resolve().parent / "agents"

DEPARTMENTS = {
    "executive": {
        "lead": "Chief",
        "title": "Chief Executive Officer",
        "mission": "Set company strategy, make final calls and review every department.",
    },
    "engineering": {
        "lead": "Forge",
        "title": "Chief Technology Officer",
        "mission": "Design, build and test the product.",
    },
    "marketing": {
        "lead": "Signal",
        "title": "Chief Marketing Officer",
        "mission": "Grow awareness and bring in customers.",
    },
    "finance": {
        "lead": "Ledger",
        "title": "Chief Financial Officer",
        "mission": "Track budget, costs and runway.",
    },
    "operations": {
        "lead": "Flow",
        "title": "Chief Operating Officer",
        "mission": "Keep daily work moving and on schedule.",
    },
}

DELIVERABLE_TEMPLATES = {
    "executive": "Strategy memo: '{task}'. Decision, owner and next review date drafted for board approval.",
    "engineering": "Build plan: '{task}'. Split into milestones, each with acceptance tests and a risk list.",
    "marketing": "Campaign brief: '{task}'. Audience, channels, message and success metric defined.",
    "finance": "Cost sheet: '{task}'. Line items, a budget cap and free-tier options listed.",
    "operations": "Runbook: '{task}'. Steps, owners, schedule and escalation path documented.",
}


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def load_state(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "company": "Autonomous Company",
        "version": VERSION,
        "founded": now_iso(),
        "next_id": 1,
        "tasks": [],
    }


def save_state(path: Path, state: dict) -> None:
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def gbot_available() -> bool:
    return shutil.which("gbot") is not None


def run_gbot(args: list[str]) -> str:
    """Run a gbot CLI command and return its stdout."""
    result = subprocess.run(
        ["gbot", *args], capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        raise RuntimeError(f"gbot {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def role_file(department: str) -> Path:
    return AGENTS_DIR / f"{department}.md"


def cmd_org(state: dict, args: argparse.Namespace) -> str:
    lines = [f"{state['company']} - org chart", ""]
    lines.append("You (CEO and owner)")
    for dept, info in DEPARTMENTS.items():
        lines.append(f"  |- {info['lead']} ({info['title']}) - {dept}: {info['mission']}")
    return "\n".join(lines)


def cmd_assign(state: dict, args: argparse.Namespace) -> str:
    dept = args.department.lower()
    if dept not in DEPARTMENTS:
        raise SystemExit(f"unknown department '{dept}'. Choose from: {', '.join(DEPARTMENTS)}")
    info = DEPARTMENTS[dept]
    if args.backend == "grokbot":
        if not gbot_available():
            raise SystemExit("gbot CLI not found. Install it first: npm install --global grok-bot-cli")
        reply = run_gbot(["send", info["lead"], args.task])
        return f"Sent to {info['lead']} ({info['title']}) via Grok Bot.\n{reply}"
    task_id = state["next_id"]
    state["next_id"] += 1
    deliverable = DELIVERABLE_TEMPLATES[dept].format(task=args.task)
    record = {
        "id": task_id,
        "department": dept,
        "owner": info["lead"],
        "task": args.task,
        "status": "done",
        "deliverable": deliverable,
        "created": now_iso(),
        "completed": now_iso(),
    }
    state["tasks"].append(record)
    return (
        f"Task #{task_id} assigned to {info['lead']} ({info['title']}).\n"
        f"Status: done\nDeliverable: {deliverable}"
    )


def cmd_standup(state: dict, args: argparse.Namespace) -> str:
    if not state["tasks"]:
        return "Standup: no tasks yet. Assign one with: python company.py assign --department engineering --task \"...\""
    lines = ["Standup - latest tasks per department:"]
    for dept, info in DEPARTMENTS.items():
        dept_tasks = [t for t in state["tasks"] if t["department"] == dept]
        if dept_tasks:
            last = dept_tasks[-1]
            lines.append(f"  {info['lead']} ({dept}): {len(dept_tasks)} task(s), latest: #{last['id']} {last['task']} [{last['status']}]")
        else:
            lines.append(f"  {info['lead']} ({dept}): idle")
    return "\n".join(lines)


def cmd_report(state: dict, args: argparse.Namespace) -> str:
    total = len(state["tasks"])
    done = sum(1 for t in state["tasks"] if t["status"] == "done")
    lines = [
        f"{state['company']} - CEO report",
        f"Founded: {state['founded']}",
        f"Tasks total: {total} | done: {done} | open: {total - done}",
        "",
        "Department breakdown:",
    ]
    for dept, info in DEPARTMENTS.items():
        count = sum(1 for t in state["tasks"] if t["department"] == dept)
        lines.append(f"  {dept:<12} ({info['lead']:<7}): {count} task(s)")
    return "\n".join(lines)


def cmd_board(state: dict, args: argparse.Namespace) -> str:
    if args.backend == "grokbot":
        if not gbot_available():
            raise SystemExit("gbot CLI not found. Install it first: npm install --global grok-bot-cli")
        agenda = args.agenda or "Weekly board meeting: each department gives status, risks and next steps."
        reply = run_gbot(["send", "Boardroom", agenda])
        return f"Board meeting started in the Boardroom group.\n{reply}"
    lines = ["Board meeting - department updates:", ""]
    for dept, info in DEPARTMENTS.items():
        dept_tasks = [t for t in state["tasks"] if t["department"] == dept]
        if dept_tasks:
            done = sum(1 for t in dept_tasks if t["status"] == "done")
            lines.append(f"  {info['lead']} ({info['title']}): {done}/{len(dept_tasks)} tasks done. Latest: {dept_tasks[-1]['task']}")
        else:
            lines.append(f"  {info['lead']} ({info['title']}): no work assigned yet. Ready for orders.")
    lines.append("")
    lines.append("Chair (you): review the updates above and assign the next tasks.")
    return "\n".join(lines)


def cmd_status(state: dict, args: argparse.Namespace) -> str:
    lines = [
        f"{state['company']} v{state.get('version', VERSION)}",
        f"Backend: {args.backend}",
        f"gbot CLI: {'found' if gbot_available() else 'not found (local mode only)'}",
        f"Tasks recorded: {len(state['tasks'])}",
    ]
    return "\n".join(lines)


def cmd_grok_sync(state: dict, args: argparse.Namespace) -> str:
    """Create the company as real Grok Bot agents and a Boardroom group via gbot."""
    if not gbot_available():
        raise SystemExit("gbot CLI not found. Install it first: npm install --global grok-bot-cli")
    outputs = []
    for dept, info in DEPARTMENTS.items():
        path = role_file(dept)
        if not path.exists():
            raise SystemExit(f"missing role file: {path}")
        description = path.read_text(encoding="utf-8").strip()
        outputs.append(run_gbot(["bots", "create", "--name", info["lead"], "--description", description]))
    member_args: list[str] = []
    for info in DEPARTMENTS.values():
        member_args += ["--member", info["lead"]]
    outputs.append(run_gbot(["groups", "create", "--name", "Boardroom", *member_args,
                             "--description", "Autonomous Company board meeting room"]))
    return "Grok Bot company created:\n" + "\n".join(o for o in outputs if o)



def parse_agent_file(path: Path) -> dict | None:
    """Parse an Agency Agents file. Real agents start with YAML front matter
    that has a `name:` line; other markdown (README, playbooks) is skipped."""
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    meta: dict = {}
    for ln in lines[1:]:
        if ln.strip() == "---":
            break
        if ":" in ln and not ln.startswith(" "):
            key, _, val = ln.partition(":")
            meta[key.strip()] = val.strip().strip('"').strip("'")
    if "name" not in meta:
        return None
    return {
        "name": meta["name"],
        "description": meta.get("description", ""),
        "vibe": meta.get("vibe", ""),
    }


def cmd_agency_import(state: dict, args: argparse.Namespace) -> str:
    """Import specialist agents from an Agency Agents roster folder.

    Works with a clone of https://github.com/ganeshsavara61-netizen/agency-agents
    (MIT, upstream: https://github.com/msitarzewski/agency-agents). Only files
    with agent front matter are imported; the folder name is the division.
    """
    roster = Path(args.roster).resolve()
    if not roster.is_dir():
        raise SystemExit(f"roster folder not found: {roster}")
    specialists = state.setdefault("specialists", {})
    added = skipped = 0
    for path in sorted(roster.rglob("*.md")):
        rel = path.relative_to(roster)
        if ".git" in rel.parts or len(rel.parts) < 2:
            continue
        info = parse_agent_file(path)
        if info is None:
            skipped += 1
            continue
        slug = path.stem
        if slug not in specialists:
            added += 1
        specialists[slug] = {
            "division": rel.parts[0],
            "name": info["name"],
            "summary": info["description"][:160],
            "vibe": info["vibe"],
            "source": str(path),
        }
    if not specialists:
        raise SystemExit(f"no agent files with front matter found under {roster}")
    return (
        f"Agency import: {added} new specialist(s), {skipped} non-agent file(s) skipped. "
        f"Total on payroll: {len(specialists)}.\n"
        "List them with: python company.py agency-list [--division engineering]"
    )


def cmd_agency_list(state: dict, args: argparse.Namespace) -> str:
    specialists = state.get("specialists", {})
    if not specialists:
        return ("No specialists hired yet. Import your Agency Agents roster:\n"
                "  git clone https://github.com/ganeshsavara61-netizen/agency-agents\n"
                "  python company.py agency-import --roster agency-agents")
    division = getattr(args, "division", None)
    rows = {k: v for k, v in specialists.items() if not division or v["division"] == division}
    if not rows:
        divs = sorted({v["division"] for v in specialists.values()})
        raise SystemExit(f"no specialists in division '{division}'. Divisions: {', '.join(divs)}")
    lines = [f"Specialist agents on payroll: {len(rows)}", ""]
    for slug in sorted(rows):
        v = rows[slug]
        lines.append(f"  [{v['division']}] {slug} - {v['name']}: {v['summary'][:90]}")
    return "\n".join(lines)


def cmd_agency_assign(state: dict, args: argparse.Namespace) -> str:
    """Give a task to an imported specialist. Local mode records a brief that
    quotes the specialist's own role; it does not call any AI model."""
    specialists = state.get("specialists", {})
    spec = specialists.get(args.specialist)
    if spec is None:
        raise SystemExit(f"unknown specialist '{args.specialist}'. Run: python company.py agency-list")
    task_id = state["next_id"]
    state["next_id"] += 1
    brief = (f"Brief for {spec['name']} ({spec['division']}): '{args.task}'. "
             f"Role: {spec['summary']} Role file: {spec['source']}")
    state["tasks"].append({
        "id": task_id, "department": "agency:" + spec["division"], "owner": spec["name"],
        "task": args.task, "status": "briefed", "deliverable": brief,
        "created": now_iso(), "completed": None,
    })
    return (f"Task #{task_id} briefed to {spec['name']} [{spec['division']}].\n"
            "Status: briefed (open - a human or an AI tool must do the work)\n" + brief)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="company",
        description="Autonomous Company - CEO-style AI company command center.",
    )
    parser.add_argument("--backend", choices=["local", "grokbot"], default="local",
                        help="local = free offline agents (default); grokbot = real Grok Bot agents via the gbot CLI")
    parser.add_argument("--experimental-grokbot", action="store_true",
                        help="required to use --backend grokbot (untested adapter, needs a paid Grok Bot plan)")
    parser.add_argument("--state", default=DEFAULT_STATE_FILE, help="path to the company state file")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("org", help="show the org chart")
    sub.add_parser("standup", help="latest task status per department")
    sub.add_parser("report", help="CEO report: totals and department breakdown")
    sub.add_parser("status", help="backend and gbot availability")

    p_assign = sub.add_parser("assign", help="assign a task to a department agent")
    p_assign.add_argument("--department", required=True, help=", ".join(DEPARTMENTS))
    p_assign.add_argument("--task", required=True, help="the task in plain words")

    p_board = sub.add_parser("board-meeting", help="run a board meeting round")
    p_board.add_argument("--agenda", default=None, help="agenda (grokbot backend)")

    sub.add_parser("grok-sync", help="create the company as real Grok Bot agents via gbot")

    p_import = sub.add_parser("agency-import", help="import specialist agents from an Agency Agents roster folder")
    p_import.add_argument("--roster", required=True, help="path to a cloned agency-agents repository")

    p_alist = sub.add_parser("agency-list", help="list imported specialist agents")
    p_alist.add_argument("--division", default=None, help="only this division, e.g. engineering")

    p_aassign = sub.add_parser("agency-assign", help="brief a task to an imported specialist")
    p_aassign.add_argument("--specialist", required=True, help="specialist slug from agency-list")
    p_aassign.add_argument("--task", required=True)
    return parser


COMMANDS = {
    "org": cmd_org,
    "assign": cmd_assign,
    "standup": cmd_standup,
    "report": cmd_report,
    "board-meeting": cmd_board,
    "status": cmd_status,
    "grok-sync": cmd_grok_sync,
    "agency-import": cmd_agency_import,
    "agency-list": cmd_agency_list,
    "agency-assign": cmd_agency_assign,
}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.backend == "grokbot" and not args.experimental_grokbot:
        raise SystemExit("The grokbot backend is experimental and untested. It needs a paid Grok Bot "
                         "plan and the gbot CLI. Add --experimental-grokbot to use it anyway.")
    state = load_state(Path(args.state))
    output = COMMANDS[args.command](state, args)
    if args.backend == "local":
        save_state(Path(args.state), state)
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
