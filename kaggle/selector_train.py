"""NeuroBrain citation-selector QLoRA on one Kaggle T4. Self-contained: runs from a fresh kernel.

Kaggle settings: Accelerator = GPU T4 x1, Internet = On. Start it with Save Version -> Save & Run All
(a background run); an idle interactive session is killed and loses /kaggle/working.
Before running, set COMMIT to the pushed commit that contains data/selector_v1.
Outputs in /kaggle/working/selector_v1: adapter/, checkpoints, run.json, dev_*.json, adapter.zip.
"""

# %% [1] Packages (Qwen3.5 needs a recent transformers)
import subprocess
import sys

subprocess.run(
    [sys.executable, "-m", "pip", "install", "-q", "-U",
     "transformers>=5.0", "peft>=0.17", "bitsandbytes>=0.46", "accelerate>=1.10"],
    check=True,
)

# %% [2] Data: fetched from the public repo at a pinned commit, hash-checked
import hashlib
import json
import math
import random
import re
import time
import urllib.request
from pathlib import Path

COMMIT = "REPLACE_WITH_COMMIT_SHA"
REPO = "https://raw.githubusercontent.com/Anm0l-17/NEUROBRAIN"
OUT = Path("/kaggle/working/selector_v1")
OUT.mkdir(parents=True, exist_ok=True)
assert re.fullmatch(r"[0-9a-f]{40}", COMMIT), "Set COMMIT to the full pushed commit SHA"

manifest = json.loads(urllib.request.urlopen(f"{REPO}/{COMMIT}/data/selector_v1/manifest.json").read())


def fetch(name):
    raw = urllib.request.urlopen(f"{REPO}/{COMMIT}/data/selector_v1/{name}").read()
    assert hashlib.sha256(raw).hexdigest() == manifest["files"][name], f"{name} hash mismatch"
    (OUT / name).write_bytes(raw)
    return [json.loads(line) for line in raw.decode().splitlines()]


train = fetch("train.jsonl")
dev = fetch("dev.jsonl")
# The sealed evaluation file is deliberately not downloaded here.
print(len(train), "train rows,", len(dev), "dev rows")

# %% [3] Model: Qwen3.5-4B, 4-bit NF4, pinned revision
import torch
from huggingface_hub import model_info
from peft import LoraConfig, PeftModel, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, set_seed

SEED, LR, ACCUM, EPOCHS, MAX_LEN, SAVE_EVERY = 17, 2e-4, 8, 1, 1536, 50
set_seed(SEED)
REPO_ID = "Qwen/Qwen3.5-4B"
REV = model_info(REPO_ID).sha
tok = AutoTokenizer.from_pretrained(REPO_ID, revision=REV)
quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                           bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
base = AutoModelForCausalLM.from_pretrained(REPO_ID, revision=REV, quantization_config=quant,
                                            device_map={"": 0}, dtype=torch.float16)
base = prepare_model_for_kbit_training(base, use_gradient_checkpointing=True)


def prompt_ids(messages):
    text = tok.apply_chat_template(messages[:-1], tokenize=False, add_generation_prompt=True,
                                   enable_thinking=False)
    return tok.encode(text, add_special_tokens=False)


# %% [4] Dev scoring: same metrics as scripts/eval_selector.py
def predict(model, row):
    x = torch.tensor([prompt_ids(row["messages"])], device="cuda")
    with torch.inference_mode():
        y = model.generate(x, attention_mask=torch.ones_like(x), max_new_tokens=120,
                           do_sample=False, pad_token_id=tok.eos_token_id)
    text = tok.decode(y[0, x.shape[1]:], skip_special_tokens=True)
    try:
        got = json.loads(text[text.index("{"): text.rindex("}") + 1])["citations"]
        allowed = {e["citation"] for e in row["evidence"]}
        return {c for c in got if c in allowed}
    except (ValueError, KeyError, TypeError):
        return None


def dev_score(model, name):
    model.eval()
    preds = [predict(model, r) for r in dev]
    n = len(dev)
    gold = [set(r["target"]) for r in dev]
    ok = [p for p in preds if p is not None]
    empty_gold = sum(not g for g in gold)
    empty_pred = sum(p is not None and not p for p in preds)
    tp = sum(p is not None and not p and not g for p, g in zip(preds, gold))
    answerable = [(p, g) for p, g in zip(preds, gold) if g and p is not None]
    result = {
        "exact_match": round(sum(p == g for p, g in zip(preds, gold)) / n, 3),
        "abstain_recall": round(tp / empty_gold, 3),
        "abstain_precision": round(tp / empty_pred, 3) if empty_pred else None,
        "over_select_rate": round(sum(bool(p - g) for p, g in answerable) / len(answerable), 3),
        "parse_errors": n - len(ok),
    }
    (OUT / f"dev_{name}.json").write_text(json.dumps(
        {"metrics": result, "predictions": [sorted(p) if p is not None else None for p in preds]}, indent=2))
    print(name, result, flush=True)
    return result


base_dev = dev_score(base, "base")

# %% [5] QLoRA training, checkpoint every SAVE_EVERY optimizer steps
TARGETS = r"^(?!.*(visual|mtp)).*\.(q_proj|k_proj|v_proj|o_proj|gate_proj|up_proj|down_proj|in_proj_qkv|in_proj_z|out_proj)$"
model = get_peft_model(base, LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05,
                                        target_modules=TARGETS, task_type="CAUSAL_LM"))
model.print_trainable_parameters()
optimizer = torch.optim.AdamW((p for p in model.parameters() if p.requires_grad), lr=LR, weight_decay=0.0)
total_steps = math.ceil(len(train) * EPOCHS / ACCUM)
schedule = torch.optim.lr_scheduler.LambdaLR(
    optimizer, lambda s: min(1.0, (s + 1) / 20) * max(0.0, 1 - s / total_steps))
losses, step, started = [], 0, time.monotonic()
model.train()
order = [i for _ in range(EPOCHS) for i in random.Random(SEED).sample(range(len(train)), len(train))]
for k, idx in enumerate(order):
    msgs = train[idx]["messages"]
    prefix = prompt_ids(msgs)
    # Render the whole conversation so the answer ends with Qwen's real turn end (<|im_end|>).
    full = tok.encode(tok.apply_chat_template(msgs, tokenize=False, enable_thinking=False),
                      add_special_tokens=False)
    assert full[: len(prefix)] == prefix, "chat template prefix mismatch"
    if len(full) > MAX_LEN:
        continue
    x = torch.tensor([full], device="cuda")
    labels = torch.tensor([[-100] * len(prefix) + full[len(prefix):]], device="cuda")
    loss = model(x, labels=labels, use_cache=False).loss / ACCUM
    assert math.isfinite(loss.item())
    loss.backward()
    losses.append(loss.item() * ACCUM)
    if (k + 1) % ACCUM == 0:
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0, error_if_nonfinite=True)
        optimizer.step()
        schedule.step()
        optimizer.zero_grad()
        step += 1
        if step % 10 == 0:
            print(f"step {step}/{total_steps} loss {sum(losses[-80:]) / len(losses[-80:]):.4f} "
                  f"{time.monotonic() - started:.0f}s", flush=True)
        if step % SAVE_EVERY == 0:
            model.save_pretrained(OUT / f"checkpoint-{step}")

# %% [6] Save, reload from disk, score on dev
model.save_pretrained(OUT / "adapter")
base = model.unload()
model = PeftModel.from_pretrained(base, OUT / "adapter")
adapter_dev = dev_score(model, "adapter")

# %% [7] Record the run and zip the adapter for download
(OUT / "run.json").write_text(json.dumps({
    "base": REPO_ID, "revision": REV, "commit": COMMIT, "seed": SEED, "lr": LR,
    "accumulation": ACCUM, "epochs": EPOCHS, "optimizer_steps": step, "lora_r": 16,
    "targets": TARGETS, "train_rows": len(train), "losses": losses,
    "seconds": round(time.monotonic() - started), "gpu": torch.cuda.get_device_name(),
    "peak_gib": round(torch.cuda.max_memory_allocated() / 2**30, 2),
    "dev_base": base_dev, "dev_adapter": adapter_dev,
}, indent=2))
subprocess.run(["zip", "-qr", str(OUT / "adapter.zip"), "adapter", "run.json", "dev_base.json",
                "dev_adapter.json"], cwd=OUT, check=True)
print("SELECTOR_DONE", REV, step, "steps; download /kaggle/working/selector_v1/adapter.zip")
