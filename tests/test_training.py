"""Training safety checks; skipped when optional training libraries are absent."""

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

AVAILABLE = all(
    importlib.util.find_spec(m) for m in ("torch", "sentence_transformers", "sklearn")
)


@unittest.skipUnless(AVAILABLE, "Optional training libraries not installed")
class TrainingDataTests(unittest.TestCase):
    def setUp(self):
        from scripts.train_admission import load_rows

        self.load_rows = load_rows
        self.path = (
            Path(__file__).resolve().parents[1] / "data/admission_pilot_v0.jsonl"
        )
        self.rows = load_rows(self.path, allow_draft=True)

    def check_rejected(self, rows):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.jsonl"
            path.write_text("\n".join(json.dumps(row) for row in rows))
            with self.assertRaises(ValueError):
                self.load_rows(path, allow_draft=True)

    def test_draft_cannot_accidentally_be_treated_as_reviewed(self):
        with self.assertRaisesRegex(ValueError, "Unreviewed labels"):
            self.load_rows(self.path)

    def test_related_scenarios_cannot_cross_partitions(self):
        rows = copy.deepcopy(self.rows)
        rows[-1]["scenario_group"] = rows[0]["scenario_group"]
        self.check_rejected(rows)

    def test_template_origins_cannot_cross_partitions(self):
        rows = copy.deepcopy(self.rows)
        rows[-1]["template_family"] = rows[0]["template_family"]
        self.check_rejected(rows)

    def test_duplicate_text_is_rejected_even_with_new_id(self):
        rows = copy.deepcopy(self.rows)
        rows[-1]["candidate_text"] = rows[0]["candidate_text"].upper()
        self.check_rejected(rows)

    def test_private_provenance_not_accepted(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["provenance"]["kind"] = "user_notes"
        self.check_rejected(rows)


if __name__ == "__main__":
    unittest.main()
