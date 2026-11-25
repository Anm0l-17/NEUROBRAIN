#!/usr/bin/env bash
# Merge a Kaggle selector adapter into Qwen3.5-4B and serve it from Ollama, the same
# route used for the converted-base comparator (reports/selector_v1/README.md).
#
# Usage: scripts/deploy_selector.sh path/to/adapter_dir ollama-model-name
# Needs: .neurobrain/qwen35_4b (HF weights @ 851bf6e), a llama.cpp checkout at
# 1a0b56c in .neurobrain/llama.cpp-premerge (the converter just before qwen tensors
# were fused; Ollama 0.40.16's runtime expects the unfused names), Homebrew
# llama-quantize, and a Python with torch, transformers and peft.
set -euo pipefail
ADAPTER=$1
NAME=$2
PY=${PY:-python}
NB=.neurobrain
WORK=$NB/merged_$NAME
test "$(git -C $NB/llama.cpp-premerge rev-parse HEAD)" = 1a0b56cec73dac938e0602c974b21dc8e2862830

"$PY" - "$ADAPTER" "$WORK" <<'EOF'
import sys
import torch
from peft import PeftModel, get_peft_model_state_dict
from safetensors import safe_open
from transformers import AutoModelForCausalLM, AutoTokenizer
adapter, out = sys.argv[1], sys.argv[2]
base = AutoModelForCausalLM.from_pretrained(".neurobrain/qwen35_4b", dtype=torch.float16)
model = PeftModel.from_pretrained(base, adapter)
# peft only warns on unmatched keys; a name mismatch would silently merge nothing.
with safe_open(f"{adapter}/adapter_model.safetensors", "pt") as f:
    saved = set(f.keys())
live = set(get_peft_model_state_dict(model).keys())
assert saved == live, f"adapter keys do not match the model: {sorted(saved ^ live)[:5]}"
merged = model.merge_and_unload()
merged.save_pretrained(out, safe_serialization=True)
AutoTokenizer.from_pretrained(".neurobrain/qwen35_4b").save_pretrained(out)
EOF
cp $NB/qwen35_4b/chat_template.jinja "$WORK/" 2>/dev/null || true

PYTHONPATH=$NB/llama.cpp-premerge/gguf-py "$PY" $NB/llama.cpp-premerge/convert_hf_to_gguf.py \
  "$WORK" --outtype f16 --outfile "$WORK/f16.gguf"
llama-quantize "$WORK/f16.gguf" "$WORK/q4km.gguf" Q4_K_M
sed "s#^FROM .*#FROM ./merged_$NAME/q4km.gguf#" scripts/selector.Modelfile > $NB/Modelfile.$NAME
(cd $NB && ollama create "$NAME" -f "Modelfile.$NAME")
echo "Now score it: PYTHONPATH=src python scripts/eval_selector.py data/selector_v1/eval_sealed.jsonl --model $NAME --out reports/selector_v1/${NAME}_eval.json"
