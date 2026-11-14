"""Run on Kaggle with the frozen training and development rows supplied by the notebook."""
import hashlib
import json
import math
import time
from pathlib import Path

import torch
from huggingface_hub import model_info
from peft import LoraConfig, PeftModel, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, set_seed

TRAIN_HASH = '06563d7ec80747609a5d4d6d4e56a7a2d4b587d31909dc1375498e3f8dd1e0cd'
DEV_HASH = 'ef479d2a43706540d4897d2929216d7b345661ca6c354c08bdc9db72855b2f32'

set_seed(17)
out = Path('/kaggle/working/neurobrain_compact_v1')
out.mkdir(exist_ok=True)
def load_rows(name, digest):
    raw = (out / name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == digest
    return [json.loads(line)['messages'] for line in raw.splitlines()]

train = load_rows('train.jsonl', TRAIN_HASH)
dev = load_rows('development.jsonl', DEV_HASH)
assert len(train) == 13 and len(dev) == 9
repo = 'Qwen/Qwen3.5-4B'
rev = model_info(repo).sha
tok = AutoTokenizer.from_pretrained(repo, revision=rev)
quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4', bnb_4bit_compute_dtype=torch.float16)
base = AutoModelForCausalLM.from_pretrained(repo, revision=rev, quantization_config=quant,
    device_map={'': 0}, dtype=torch.float16, attn_implementation='eager')
base = prepare_model_for_kbit_training(base, use_gradient_checkpointing=False)
def prompt(row):
    text = tok.apply_chat_template(row[:-1], tokenize=False, add_generation_prompt=True, enable_thinking=False)
    return tok.encode(text, add_special_tokens=False)

def evaluate(model, name):
    model.eval()
    answers = []
    with torch.inference_mode():
        for row in dev:
            x = torch.tensor([prompt(row)], device='cuda')
            start = time.monotonic()
            y = model.generate(x, attention_mask=torch.ones_like(x), max_new_tokens=180,
                               do_sample=False, pad_token_id=tok.eos_token_id)
            answer = tok.decode(y[0, x.shape[1]:], skip_special_tokens=True)
            answers.append({'answer': answer, 'seconds': time.monotonic()-start})
    (out / (name+'.json')).write_text(json.dumps(answers, indent=2))
    print(name, json.dumps([a['answer'] for a in answers]), flush=True)

evaluate(base, 'baseline')
model = get_peft_model(base, LoraConfig(r=8, lora_alpha=16, target_modules=['q_proj','v_proj'], task_type='CAUSAL_LM'))
model.train()
optimizer = torch.optim.AdamW((p for p in model.parameters() if p.requires_grad), lr=0.0001)
losses = []
for epoch in range(2):
    for idx in torch.randperm(len(train)).tolist():
        row = train[idx]
        prefix = prompt(row)
        target = tok.encode(row[-1]['content'], add_special_tokens=False) + [tok.eos_token_id]
        assert len(prefix)+len(target) <= 1024
        x = torch.tensor([prefix+target], device='cuda')
        labels = torch.tensor([[-100]*len(prefix)+target], device='cuda')
        optimizer.zero_grad()
        loss = model(x, labels=labels, use_cache=False).loss
        loss.backward()
        norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0, error_if_nonfinite=True)
        assert math.isfinite(loss.item()) and norm.item() > 0
        optimizer.step()
        losses.append(loss.item())
        if len(losses) == 20:
            break
model.save_pretrained(out/'adapter')
base = model.unload()
model = PeftModel.from_pretrained(base, out/'adapter')
evaluate(model, 'reloaded')
print('COMPACT_DONE', rev, len(losses), round(torch.cuda.max_memory_allocated()/2**30, 2), flush=True)
(out/'run.json').write_text(json.dumps({'revision':rev,'losses':losses,'seed':17,'gpu':torch.cuda.get_device_name()}, indent=2))
