import json, sys, time
from pathlib import Path
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

if len(sys.argv) not in (4, 5):
    raise SystemExit('Usage: generate_answers.py MODEL_PATH ADAPTER_PATH_OR_EMPTY OUTPUT_JSON [DATA_JSONL]')
model_path, adapter, output_path = sys.argv[1:4]
data_path = sys.argv[4] if len(sys.argv) == 5 else 'data/generator_pilot_v0/valid.jsonl'
if not Path(model_path).is_dir():
    raise SystemExit('MODEL_PATH must be a downloaded local checkpoint directory')
model, tokenizer = load(model_path, adapter_path=adapter or None)
rows = [json.loads(line) for line in Path(data_path).read_text().splitlines()]
assert rows and all(len(row['messages']) == 3 for row in rows)
results = []
for i, row in enumerate(rows):
    prompt = tokenizer.apply_chat_template(row['messages'][:-1], tokenize=False, add_generation_prompt=True, enable_thinking=False)
    start = time.monotonic()
    answer = generate(model, tokenizer, prompt=prompt, max_tokens=180, sampler=make_sampler(temp=0))
    results.append({'case': i, 'answer': answer, 'expected': row['messages'][-1]['content'], 'elapsed_seconds': time.monotonic()-start})
    print(i, answer, flush=True)
assert len(results)==len(rows) and all(r['answer'].strip() for r in results)
Path(output_path).write_text(json.dumps(results, indent=2)+'\n')
