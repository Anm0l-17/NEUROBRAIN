"""Training safety checks; skipped when optional training libraries are absent."""

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

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

    def test_uncertain_action_is_kept_as_ambiguity_not_binary_label(self):
        from scripts.train_admission import filter_rows_for_head

        rows = copy.deepcopy(self.rows)
        rows[0]["action"] = "uncertain"
        rows[0]["label"] = None
        usable, ambiguity = filter_rows_for_head(rows, "action")
        self.assertEqual(len(usable), len(rows) - 1)
        self.assertEqual([r["example_id"] for r in ambiguity], [rows[0]["example_id"]])

    def test_action_filter_rejects_invalid_or_missing_nonlegacy_values(self):
        from scripts.train_admission import filter_rows_for_head

        for row in (
            {"label": 0},
            {"label": None},
            {"label": True, "action": "keep"},
            {"label": 1.0, "action": "keep"},
            {"action": "uncertain"},
        ):
            with self.subTest(row=row), self.assertRaises(ValueError):
                filter_rows_for_head([row], "action")

    def test_action_and_binary_label_must_agree(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["action"] = "skip"
        self.check_rejected(rows)

    def test_non_integer_binary_labels_are_rejected(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["label"] = 1.0
        self.check_rejected(rows)

    def test_snapshot_features_do_not_depend_on_row_order(self):
        from scripts.train_admission import build_features

        class Tokenizer:
            def encode(self, text, add_special_tokens=False):
                return [ord(char) % 97 for char in text]

            def num_special_tokens_to_add(self, pair=False):
                return 0

            def decode(self, tokens, skip_special_tokens=True):
                return " ".join(map(str, tokens))

        class Encoder:
            tokenizer = Tokenizer()
            max_seq_length = 256

            def eval(self):
                return self

            def parameters(self):
                return []

            def encode(self, texts, **kwargs):
                return np.asarray(
                    [[(sum(map(ord, text)) % 101) / 101] * 384 for text in texts],
                    dtype=np.float32,
                )

        rows = self.rows[:4]
        forward, _, _ = build_features(rows, Encoder())
        reverse, _, _ = build_features(list(reversed(rows)), Encoder())
        by_id = {row["example_id"]: row for row in rows}
        for index, row in enumerate(reversed(rows)):
            original_index = rows.index(by_id[row["example_id"]])
            np.testing.assert_allclose(reverse[index], forward[original_index])
        self.assertTrue(np.all(forward[:, -1] == 0))


if __name__ == "__main__":
    unittest.main()
