import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPANY = ROOT / "company.py"


def run_cli(state_dir, *cli_args):
    state = Path(state_dir) / "state.json"
    cmd = [sys.executable, str(COMPANY), "--state", str(state), *cli_args]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)


class TestAutonomousCompany(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_org_chart_lists_all_departments(self):
        result = run_cli(self.dir, "org")
        self.assertEqual(result.returncode, 0, result.stderr)
        for lead in ["Chief", "Forge", "Signal", "Ledger", "Flow"]:
            self.assertIn(lead, result.stdout)

    def test_assign_creates_done_task_with_deliverable(self):
        result = run_cli(self.dir, "assign", "--department", "engineering",
                         "--task", "Build landing page")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Task #1", result.stdout)
        self.assertIn("Forge", result.stdout)
        state = json.loads((Path(self.dir) / "state.json").read_text())
        self.assertEqual(len(state["tasks"]), 1)
        self.assertEqual(state["tasks"][0]["status"], "done")
        self.assertIn("landing page", state["tasks"][0]["deliverable"])

    def test_unknown_department_fails(self):
        result = run_cli(self.dir, "assign", "--department", "legal", "--task", "x")
        self.assertNotEqual(result.returncode, 0)

    def test_standup_and_report_after_assigns(self):
        run_cli(self.dir, "assign", "--department", "marketing", "--task", "Launch post")
        run_cli(self.dir, "assign", "--department", "finance", "--task", "Budget review")
        standup = run_cli(self.dir, "standup")
        self.assertIn("Signal", standup.stdout)
        self.assertIn("Launch post", standup.stdout)
        report = run_cli(self.dir, "report")
        self.assertIn("Tasks total: 2", report.stdout)

    def test_empty_standup_is_helpful(self):
        result = run_cli(self.dir, "standup")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("no tasks yet", result.stdout)

    def test_board_meeting_local(self):
        run_cli(self.dir, "assign", "--department", "operations", "--task", "Weekly schedule")
        result = run_cli(self.dir, "board-meeting")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Flow", result.stdout)
        self.assertIn("1/1 tasks done", result.stdout)

    def test_status_reports_local_backend(self):
        result = run_cli(self.dir, "status")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Backend: local", result.stdout)

    def test_agent_role_files_exist(self):
        for dept in ["executive", "engineering", "marketing", "finance", "operations"]:
            role_file = ROOT / "agents" / f"{dept}.md"
            self.assertTrue(role_file.exists(), f"missing {role_file}")
            self.assertGreater(len(role_file.read_text().strip()), 50)


if __name__ == "__main__":
    unittest.main()


def make_roster(base):
    roster = Path(base) / "agency-agents"
    (roster / "engineering").mkdir(parents=True)
    (roster / "engineering" / "engineering-frontend-wizard.md").write_text(
        '---\nname: Frontend Wizard\ndescription: "Builds pixel perfect interfaces."\nvibe: Ships fast\n---\n\n# Frontend Wizard\n')
    (roster / "marketing").mkdir()
    (roster / "marketing" / "marketing-reddit-ninja.md").write_text(
        "---\nname: Reddit Ninja\ndescription: Grows communities.\n---\n# Reddit Ninja\n")
    (roster / "engineering" / "PLAYBOOK.md").write_text("# Phase 4 Playbook\nno front matter\n")
    (roster / "README.md").write_text("# The Agency\n")
    return roster


class TestAgencyBridge(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        self.roster = make_roster(self.dir)

    def tearDown(self):
        self.tmp.cleanup()

    def test_import_reads_front_matter_and_skips_non_agents(self):
        result = run_cli(self.dir, "agency-import", "--roster", str(self.roster))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("2 new specialist(s), 1 non-agent file(s) skipped", result.stdout)
        listing = run_cli(self.dir, "agency-list")
        self.assertIn("[engineering] engineering-frontend-wizard - Frontend Wizard: Builds pixel perfect", listing.stdout)
        self.assertNotIn("PLAYBOOK", listing.stdout)
        self.assertNotIn("---", listing.stdout)

    def test_list_by_division(self):
        run_cli(self.dir, "agency-import", "--roster", str(self.roster))
        listing = run_cli(self.dir, "agency-list", "--division", "marketing")
        self.assertIn("Reddit Ninja", listing.stdout)
        self.assertNotIn("Frontend Wizard", listing.stdout)

    def test_assign_to_specialist_is_briefed_not_done(self):
        run_cli(self.dir, "agency-import", "--roster", str(self.roster))
        result = run_cli(self.dir, "agency-assign", "--specialist", "marketing-reddit-ninja", "--task", "Launch post")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Status: briefed", result.stdout)
        bad = run_cli(self.dir, "agency-assign", "--specialist", "nobody", "--task", "x")
        self.assertNotEqual(bad.returncode, 0)

    def test_import_missing_folder_fails(self):
        result = run_cli(self.dir, "agency-import", "--roster", str(Path(self.dir) / "nope"))
        self.assertNotEqual(result.returncode, 0)

    def test_list_empty_is_helpful(self):
        result = run_cli(self.dir, "agency-list")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("agency-import", result.stdout)

    def test_import_is_idempotent(self):
        run_cli(self.dir, "agency-import", "--roster", str(self.roster))
        second = run_cli(self.dir, "agency-import", "--roster", str(self.roster))
        self.assertIn("0 new specialist(s)", second.stdout)


class TestGrokBotGate(unittest.TestCase):
    def test_grokbot_backend_blocked_without_experimental_flag(self):
        with tempfile.TemporaryDirectory() as d:
            result = run_cli(d, "--backend", "grokbot", "assign", "--department", "finance", "--task", "x")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("experimental", result.stderr)


import os


@unittest.skipUnless(os.environ.get("AGENCY_ROSTER"), "set AGENCY_ROSTER to a real agency-agents clone")
class TestRealAgencyRoster(unittest.TestCase):
    def test_real_roster_imports_many_agents(self):
        with tempfile.TemporaryDirectory() as d:
            result = run_cli(d, "agency-import", "--roster", os.environ["AGENCY_ROSTER"])
            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads((Path(d) / "state.json").read_text())
            self.assertGreater(len(state["specialists"]), 200)
            self.assertTrue(all(v["summary"] and v["summary"] != "---" for v in state["specialists"].values()))


if __name__ == "__main__":
    unittest.main()
