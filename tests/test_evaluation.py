import json
import tempfile
import unittest
from pathlib import Path

from scripts.evaluate_baseline import load_cases, run


class BaselineEvaluationTests(unittest.TestCase):
    def test_fictional_corpus_passes_current_baseline(self):
        path = Path(__file__).parents[1] / "data/evaluation_v0.jsonl"
        result = run(load_cases(path))
        self.assertTrue(result["passed"], result)
        self.assertEqual(result["answerable_recall"], 1.0)
        self.assertEqual(result["unsupported_abstention"], 1.0)
        self.assertEqual(result["citation_validity"], 1.0)
        self.assertTrue(all(item["passed"] for item in result["deletions"]))

    def test_loader_rejects_duplicate_case_ids(self):
        path = Path(__file__).parents[1] / "data/evaluation_v0.jsonl"
        cases = path.read_text(encoding="utf-8").splitlines()
        duplicate = json.loads(cases[0])
        with tempfile.TemporaryDirectory() as directory:
            duplicate_path = Path(directory) / "duplicate.jsonl"
            duplicate_path.write_text("\n".join([cases[0], json.dumps(duplicate)]))
            with self.assertRaisesRegex(ValueError, "Duplicate evaluation case"):
                load_cases(duplicate_path)

    def test_runner_requires_deletion_and_retained_cases(self):
        path = Path(__file__).parents[1] / "data/evaluation_v0.jsonl"
        cases = [case for case in load_cases(path) if case["kind"] == "answerable"]
        with self.assertRaisesRegex(ValueError, "deletion and retained"):
            run(cases)

    def test_loader_rejects_note_path_escape(self):
        path = Path(__file__).parents[1] / "data/evaluation_v0.jsonl"
        case = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
        case["note"] = "../outside.md"
        with tempfile.TemporaryDirectory() as directory:
            invalid_path = Path(directory) / "invalid.jsonl"
            invalid_path.write_text(json.dumps(case))
            with self.assertRaisesRegex(ValueError, "Invalid note path"):
                load_cases(invalid_path)

    def test_loader_rejects_missing_or_duplicate_fixture_notes(self):
        path = Path(__file__).parents[1] / "data/evaluation_v0.jsonl"
        cases = load_cases(path)
        cases[0]["note"] = ""
        with tempfile.TemporaryDirectory() as directory:
            invalid_path = Path(directory) / "missing.jsonl"
            invalid_path.write_text(json.dumps(cases[0]))
            with self.assertRaisesRegex(ValueError, "Missing note"):
                load_cases(invalid_path)

        cases = load_cases(path)
        cases[1]["note"] = "./" + cases[0]["note"]
        with tempfile.TemporaryDirectory() as directory:
            invalid_path = Path(directory) / "duplicate.jsonl"
            invalid_path.write_text("\n".join(json.dumps(case) for case in cases[:2]))
            with self.assertRaisesRegex(ValueError, "Duplicate note path"):
                load_cases(invalid_path)

        cases = load_cases(path)
        cases[0]["expected_terms"] = []
        with tempfile.TemporaryDirectory() as directory:
            invalid_path = Path(directory) / "terms.jsonl"
            invalid_path.write_text(json.dumps(cases[0]))
            with self.assertRaisesRegex(ValueError, "Expected terms"):
                load_cases(invalid_path)

    def test_runner_checks_nested_and_multiple_deletions(self):
        path = Path(__file__).parents[1] / "data/evaluation_v0.jsonl"
        cases = load_cases(path)
        nested = next(case for case in cases if case["kind"] == "deletion").copy()
        nested.update(
            {
                "case_id": "delete_nested_canary",
                "note": "nested/to_forget.md",
                "text": "NestedDeleteCanary must also disappear.",
                "query": "NestedDeleteCanary",
                "expected_terms": ["NestedDeleteCanary"],
                "expected_source": "nested/to_forget.md",
            }
        )
        result = run([*cases, nested])
        self.assertTrue(result["passed"], result)
        self.assertEqual(len(result["deletions"]), 2)


if __name__ == "__main__":
    unittest.main()
