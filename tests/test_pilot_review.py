"""Pilot agreement calculations exclude uncertain keep/skip judgments."""

import unittest

from scripts.score_pilot_reviews import binary_kappa, compare


class PilotReviewTests(unittest.TestCase):
    def test_agreement_and_disagreement_fields(self):
        first = {
            "a": {
                "action": "keep",
                "type": "decision",
                "scope": "project",
                "sensitivity": "ordinary",
                "source": "fictional_assistant_authored",
            },
            "b": {
                "action": "skip",
                "type": "transient",
                "scope": "session",
                "sensitivity": "ordinary",
                "source": "fictional_assistant_authored",
            },
            "c": {
                "action": "uncertain",
                "type": "uncertain",
                "scope": "uncertain",
                "sensitivity": "uncertain",
                "source": "uncertain",
            },
        }
        second = {key: value.copy() for key, value in first.items()}
        second["b"]["action"] = "keep"
        second["b"]["type"] = "fact"
        result = compare(first, second)
        self.assertEqual(result["keep_skip_rows"], 2)
        self.assertEqual(result["excluded_from_kappa_as_uncertain"], 1)
        self.assertEqual(result["keep_skip_agreement"], 0.5)
        self.assertEqual(result["keep_skip_cohens_kappa"], 0.0)
        self.assertEqual(result["type_rows"], 2)
        self.assertEqual(result["type_agreement"], 0.5)
        self.assertEqual(result["scope_rows"], 2)
        self.assertEqual(result["scope_agreement"], 1.0)
        self.assertEqual(
            result["disagreements"], [{"example_id": "b", "fields": ["action", "type"]}]
        )

    def test_kappa_undefined_when_both_reviewers_use_one_class(self):
        self.assertIsNone(binary_kappa([("keep", "keep")] * 3))


if __name__ == "__main__":
    unittest.main()
