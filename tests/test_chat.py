import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from neurobrain.chat import chat, main, needs_thinking
from scripts.evaluate_chat import score


class ChatTests(unittest.TestCase):
    @patch("builtins.print")
    @patch(
        "builtins.input", side_effect=["hello", "failed request", "try again", "/bye"]
    )
    @patch(
        "neurobrain.chat.chat",
        side_effect=[{"answer": "Hi"}, TimeoutError("timeout"), {"answer": "Done"}],
    )
    def test_failed_interactive_turn_preserves_successful_history(
        self, requester, input_mock, output
    ):
        self.assertEqual(main([]), 0)
        self.assertEqual(
            requester.call_args.args[0],
            [
                dict(role="user", content="hello"),
                dict(role="assistant", content="Hi"),
                dict(role="user", content="try again"),
            ],
        )

    @patch("builtins.print")
    @patch("neurobrain.chat.chat", return_value={"answer": "Hey!"})
    def test_launcher_defaults_to_auto(self, requester, output):
        self.assertEqual(main(["hey"]), 0)
        requester.assert_called_once_with([dict(role="user", content="hey")], "auto")
        output.assert_called_once_with("Hey!")

    def test_fixture_routes(self):
        cases = json.loads(
            (Path(__file__).parent / "fixtures/chat_accuracy.json").read_text()
        )
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertEqual(
                    needs_thinking([dict(role="user", content=case["prompt"])]),
                    case["think"],
                )

    def test_followups_use_thinking_and_greetings_stay_fast(self):
        history = [
            dict(role="user", content="Solve this problem"),
            dict(role="assistant", content="Okay"),
        ]
        self.assertTrue(
            needs_thinking([*history, dict(role="user", content="Which is best?")])
        )
        self.assertFalse(
            needs_thinking([*history, dict(role="user", content="thanks")])
        )

    def test_unseen_difficult_and_ambiguous_requests(self):
        for prompt in (
            "What is 123 multiplied by 456?",
            "What if the deadline changes?",
            "Which architecture is better?",
            "Help me with this",
            "Design a cache",
        ):
            with self.subTest(prompt=prompt):
                self.assertTrue(needs_thinking([dict(role="user", content=prompt)]))

    def test_access_code_is_a_lookup_but_programming_uses_thinking(self):
        self.assertFalse(
            needs_thinking([dict(role="user", content="What is my access code?")])
        )
        for prompt in (
            "Write code to sort a list",
            "What does this code do?",
            "What is the complexity of this algorithm?",
        ):
            self.assertTrue(needs_thinking([dict(role="user", content=prompt)]))

    @patch("neurobrain.chat.build_opener")
    def test_payload_modes_and_hidden_trace(self, opener):
        response = MagicMock()
        response.read.return_value = json.dumps(
            dict(done_reason="stop", message=dict(content="888", thinking="trace"))
        ).encode()
        opener.return_value.open.return_value.__enter__.return_value = response
        for mode, expected in [("auto", True), ("fast", False), ("think", True)]:
            result = chat([dict(role="user", content="Calculate 37 * 24")], mode)
            payload = json.loads(opener.return_value.open.call_args.args[0].data)
            self.assertEqual(payload["think"], expected)
            self.assertEqual(result["answer"], "888")
            self.assertNotIn("trace", result["answer"])
        response.read.return_value = b'{"done_reason":"length"}'
        with self.assertRaises(ValueError):
            chat([dict(role="user", content="hey")])
        response.read.return_value = b"x" * 262145
        with self.assertRaises(ValueError):
            chat([dict(role="user", content="hey")])

    def test_reject_invalid_input(self):
        for messages in (
            [],
            [None],
            "hello",
            [dict(role="system", content="test")],
            [dict(role="user", content="")],
            [dict(role="user", content="x" * 12001)],
        ):
            with self.assertRaises(ValueError):
                chat(messages)
        with self.assertRaises(ValueError):
            chat([dict(role="user", content="hey")], "unknown")

    def test_accuracy_score_rejects_missing_or_conflicting_answer(self):
        case = dict(required=["russia"], forbidden=["canada is the largest"])
        self.assertTrue(score(case, "Russia, by area."))
        self.assertFalse(score(case, "Canada."))
        self.assertFalse(score(case, "Canada is the largest, followed by Russia."))
