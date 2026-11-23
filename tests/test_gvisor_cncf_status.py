# ABOUTME: Checks that no abstract or research text calls gVisor non-CNCF without a dated correction.
# ABOUTME: gVisor became a CNCF Sandbox project on 2026-09-28 (issue #15); stdlib only.

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIELDS = ROOT / "abstract" / "sessionize-fields.md"
SESSION = ROOT / "abstract" / "kubecon-eu-2027-session.md"

# gVisor and a "not CNCF" phrase in the same clause, either order.
CLAIM = re.compile(
    r"gVisor[^.;\n]{0,120}?(not CNCF|outside the CNCF)|non-CNCF[^.;\n]{0,40}gVisor",
    re.IGNORECASE)
INLINE = re.compile(r"correct(ed|ion of) 2026-11-23", re.IGNORECASE)


def following_blockquote(lines, index):
    """The blockquote right after line `index`, skipping blank lines, joined; '' if none."""
    i = index + 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    quote = []
    while i < len(lines) and lines[i].startswith(">"):
        quote.append(lines[i])
        i += 1
    return " ".join(quote)


def section(path, heading):
    text = path.read_text(encoding="utf-8")
    return text.split(f"\n## {heading}\n", 1)[1].split("\n## ", 1)[0]


class GvisorStatusTest(unittest.TestCase):
    def test_every_not_cncf_claim_carries_a_dated_correction(self):
        paths = sorted((ROOT / "abstract").glob("*.md")) + sorted((ROOT / "research").glob("*.md"))
        for path in paths:
            lines = path.read_text(encoding="utf-8").splitlines()
            for n, line in enumerate(lines):
                if not CLAIM.search(line) or INLINE.search(line):
                    continue
                quote = following_blockquote(lines, n)
                with self.subTest(file=path.name, line=n + 1):
                    self.assertIn("2026-11-23", quote, "no dated correction below the claim")
                    self.assertIn("CNCF Sandbox", quote)

    def test_submitted_projects_field_kept_as_entered(self):
        field = section(FIELDS, "Relevant CNCF/Open Source Projects")
        self.assertIn("gVisor (not CNCF), Kata Containers on QEMU and Firecracker (not CNCF)", field)
        self.assertIn("> Correction of 2026-11-23 (#15), not entered on Sessionize", field)

    def test_submitted_value_paragraph_kept_as_entered(self):
        submitted = "gVisor and Kata Containers, the two strongest runtime options, are open source projects outside the CNCF, and the session says so."
        for path in (FIELDS, SESSION):
            value = section(path, "Value to the community")
            with self.subTest(file=path.name):
                self.assertIn(submitted, value)
                self.assertIn("> Correction of 2026-11-23 (#15), not entered on Sessionize", value)

    def test_working_project_list_names_gvisor_as_sandbox(self):
        projects = section(SESSION, "Relevant CNCF/Open Source Projects")
        self.assertIn("- gVisor (Google, open source; CNCF Sandbox, accepted 2026-09-28)", projects)


if __name__ == "__main__":
    unittest.main()
