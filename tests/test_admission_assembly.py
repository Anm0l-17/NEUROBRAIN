"""Checks the reviewed snapshot against known corrections and ambiguity rows."""

import unittest
from pathlib import Path

from scripts.assemble_admission_reviewed import assemble


class AssemblyTests(unittest.TestCase):
    def test_review_corrections_notes_and_independent_label_states_survive(self):
        rows, hashes = assemble(Path(__file__).resolve().parents[1])
        self.assertEqual(len(rows), 1584)
        self.assertEqual(len(hashes), 18)
        self.assertEqual(sum(r["label"] is None for r in rows), 96)
        by_id = {r["example_id"]: r for r in rows}
        privacy = by_id["batch-b-07-01"]
        self.assertEqual(privacy["sensitivity"], "uncertain")
        self.assertTrue(privacy["adjudication_note"])
        fresh = by_id["eval-fresh-01-05-3"]
        self.assertIsNone(fresh["label"])
        self.assertEqual(fresh["label_state"]["action"], "unresolved")
        self.assertEqual(fresh["label_state"]["sensitivity"], "reviewed")
        self.assertEqual(fresh["sensitivity"], "restricted")
        self.assertTrue(by_id["eval-fresh-01-00-0"]["review_notes"])
        for example_id in (
            "eval-fresh-02-00-07",
            "eval-fresh-02-02-07",
            "eval-fresh-02-04-07",
        ):
            self.assertEqual(by_id[example_id]["scope"], "person")
            self.assertEqual(by_id[example_id]["action"], "skip")
        self.assertEqual(by_id["eval-fresh-02-04-09"]["sensitivity"], "restricted")
        self.assertIsNone(by_id["eval-fresh-02-04-09"]["label"])
        self.assertEqual({r["split"] for r in rows}, {"unassigned"})
