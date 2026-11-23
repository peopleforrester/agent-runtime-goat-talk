# ABOUTME: Checks that every copy calling gVisor non-CNCF carries the 2026-09-28 Sandbox correction.
# ABOUTME: Run with `python3 -m unittest discover -s tests` from the repo root; stdlib only.

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOT_CNCF = re.compile(r"not cncf|not a cncf|non-cncf|outside the cncf", re.IGNORECASE)
ACCEPTED = "2026-09-28"
# A correction may sit on the claim's own line or in the note that follows it.
WINDOW = 12


class GvisorCncfStatusTest(unittest.TestCase):
    def test_each_not_cncf_claim_carries_the_sandbox_correction(self):
        files = sorted((ROOT / "abstract").glob("*.md")) + sorted((ROOT / "research").glob("*.md"))
        self.assertTrue(files)
        for path in files:
            lines = path.read_text(encoding="utf-8").splitlines()
            for number, line in enumerate(lines):
                if "gvisor" not in line.lower() or not NOT_CNCF.search(line):
                    continue
                with self.subTest(file=path.name, line=number + 1):
                    nearby = "\n".join(lines[number:number + WINDOW + 1])
                    self.assertIn(ACCEPTED, nearby,
                                  "gVisor is called non-CNCF without the dated Sandbox correction")

    def test_verification_record_lists_gvisor_as_sandbox(self):
        text = (ROOT / "research" / "2026-10-11-verification.md").read_text(encoding="utf-8")
        self.assertRegex(text, r"\| gVisor \| Sandbox \| 2026-09-28 \| https://www\.cncf\.io/sandbox-projects/")

    def test_plan_names_gvisor_a_cncf_sandbox_project_for_scoreboard_and_deck(self):
        text = (ROOT / "PROJECT_STATE.md").read_text(encoding="utf-8")
        plan = text.split("\n## Current Plan\n", 1)[1].split("\n## ", 1)[0]
        self.assertIn("in the scoreboard and in the deck: gVisor is a CNCF Sandbox project", plan)


if __name__ == "__main__":
    unittest.main()
