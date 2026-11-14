"""Origin grouping must preserve transitive connections across both fields."""

import unittest

from scripts.audit_admission_overlap import connected_groups


class OriginGroupingTests(unittest.TestCase):
    def test_paraphrase_reference_connects_to_original_row(self):
        rows = [dict(example_id=k, scenario_group=k, template_family=k) for k in "abc"]
        rows[1]["paraphrase_origin"] = "a"
        groups = connected_groups(rows)
        self.assertEqual(groups[0], groups[1])
        self.assertNotEqual(groups[0], groups[2])

    def test_parent_and_paraphrase_links(self):
        rows = [dict(example_id=k, scenario_group=k, template_family=k) for k in "abc"]
        rows[0]["parent_id"] = "b"
        rows[1]["paraphrase_origin"] = rows[2]["paraphrase_origin"] = "same"
        self.assertEqual(len(set(connected_groups(rows))), 1)
        rows[0]["parent_id"] = "missing"
        with self.assertRaises(ValueError):
            connected_groups(rows)

    def test_scenario_and_family_links_are_transitive(self):
        rows = [
            {"scenario_group": "a", "template_family": "one"},
            {"scenario_group": "a", "template_family": "two"},
            {"scenario_group": "b", "template_family": "two"},
            {"scenario_group": "c", "template_family": "three"},
        ]
        groups = connected_groups(rows)
        self.assertEqual(len(set(groups[:3])), 1)
        self.assertNotEqual(groups[0], groups[3])
