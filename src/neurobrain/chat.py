"""Adaptive local chat: direct answers for simple requests, thinking otherwise."""

import argparse
import json
import re
from urllib.error import URLError
from urllib.request import ProxyHandler, Request, build_opener

from .cloud import NoRedirect


def needs_thinking(messages):
    question = messages[-1]["content"].strip().lower()
    if re.fullmatch(r"(hi|hey|hello|thanks|thank you)[!. ]*", question):
        return False
    # shortcut: surface cues cannot measure difficulty; evaluate misses before widening the fast path.
    if sum(len(m["content"]) for m in messages) > 6000:
        return True
    if re.search(
        r"\b(why|how|compare|explain|analy[sz]e|solve|calculate|prove|debug|"
        r"python|javascript|function|algorithm|complexity|"
        r"plan|design|reason|step|optimi[sz]e|evaluate|tradeoff|trade-off|"
        r"multiply|multiplied|divide|divided|times|best|better|recommend)\b|"
        r"\bwhat\s+(if|should)\b|\d\s*[-+*/\N{MULTIPLICATION SIGN}\N{DIVISION SIGN}]|```|"
        r"\b(percent|probability|equation)\b|"
        r"\b(write|review|fix|generate)\b.{0,25}\bcode\b|"
        r"\bcode\b.{0,25}\b(do|work|fail|bug)\b",
        question,
    ):
        return True
    # Follow-ups can depend on a difficult earlier task.
    if len(messages) > 1:
        return True
    return not bool(re.search(r"\b(what|who|when|where|which|name)\b", question))


def chat(messages, mode="auto"):
    if (
        not isinstance(messages, list)
        or not messages
        or any(
            not isinstance(m, dict)
            or m.get("role") not in ("user", "assistant")
            or not isinstance(m.get("content"), str)
            for m in messages
        )
        or messages[-1]["role"] != "user"
        or not messages[-1]["content"].strip()
    ):
        raise ValueError("Provide a nonempty user message and valid chat history.")
    if mode not in ("auto", "fast", "think"):
        raise ValueError("Unknown thinking mode.")
    if sum(len(m["content"]) for m in messages) > 12000:
        raise ValueError("Chat is too long; start a fresh session.")
    thinking = needs_thinking(messages) if mode == "auto" else mode == "think"
    payload = dict(
        model="neurobrain-test",
        messages=messages,
        think=thinking,
        stream=False,
        options={
            "temperature": 0,
            "num_ctx": 16384,
            "num_predict": 8192 if thinking else 2048,
        },
    )
    request = Request(
        "http://127.0.0.1:11434/api/chat",
        json.dumps(payload).encode(),
        {"Content-Type": "application/json"},
    )
    with build_opener(ProxyHandler({}), NoRedirect()).open(
        request, timeout=600
    ) as response:
        raw = response.read(262145)
    if len(raw) > 262144:
        raise ValueError("Model response exceeded the size limit.")
    result = json.loads(raw)
    if not isinstance(result, dict) or result.get("done_reason") != "stop":
        raise ValueError("Model hit its generation limit; answer was not completed.")
    content = result["message"]["content"]
    if not isinstance(content, str) or not content.strip():
        raise ValueError("Model returned no answer.")
    return dict(
        answer=content,
        thinking=thinking,
        thinking_tokens_present=bool(result["message"].get("thinking")),
        eval_count=result.get("eval_count"),
        total_duration=result.get("total_duration"),
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="NeuroBrain Test adaptive chat")
    parser.add_argument("prompt", nargs="?")
    parser.add_argument("--mode", choices=("auto", "fast", "think"), default="auto")
    args = parser.parse_args(argv)
    if args.prompt is not None and not args.prompt.strip():
        parser.error("The prompt must not be empty.")
    messages = []
    try:
        while True:
            question = args.prompt if args.prompt is not None else input(">>> ")
            if question.strip() in ("/bye", "/exit"):
                return 0
            if not question.strip():
                continue
            pending = [*messages, dict(role="user", content=question)]
            try:
                result = chat(pending, args.mode)
            except (URLError, OSError, ValueError, KeyError, TypeError) as exc:
                print(f"Chat failed: {exc}")
                if args.prompt is not None:
                    return 1
                continue
            print(result["answer"])
            messages = [*pending, dict(role="assistant", content=result["answer"])]
            if args.prompt is not None:
                return 0
    except (EOFError, KeyboardInterrupt):
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
