import json
import unittest
from pathlib import Path

from scripts.freeze_admission_grouped_exploratory import freeze


class AdmissionReleaseTests(unittest.TestCase):
    def test_exploratory_freeze_keeps_uncertainty_and_groups(self):
        root = Path(__file__).resolve().parents[1]
        output, report, manifest = freeze(root)
        self.assertTrue(output.exists())
        self.assertTrue(report.exists())
        self.assertEqual(manifest["row_count"], 1584)
        self.assertEqual(manifest["null_action_labels"], 96)
        self.assertEqual(
            {split: details["rows"] for split, details in manifest["splits"].items()},
            {"train": 1500, "validation": 24, "test": 60},
        )
        rows = [json.loads(line) for line in output.read_text().splitlines()]
        self.assertEqual(
            {row["origin_component"] for row in rows if row["split"] == "train"},
            set(manifest["splits"]["train"]["group_ids"]),
        )
        self.assertTrue(
            all(row["label"] is None for row in rows if row["action"] == "uncertain")
        )


if __name__ == "__main__":
    unittest.main()
