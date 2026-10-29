# NeuroBrain: Review of the 22-Paper Reading List

**Prepared:** 16 October 2026  
**Scope:** The 22 entries in `Elicit - NeuroBrain 22-paper research reading list.csv`, interpreted against `NEUROBRAIN.md`.

## Executive summary

The reading list supports NeuroBrain's central idea, but it also suggests a more practical project boundary than the current blueprint implies. For a mini-project, NeuroBrain should primarily be an **external, local memory system around a frozen or lightly adapted language model**, not a system that continually rewrites the language model's weights. The most transferable papers combine selective capture, episodic/event structure, temporal graphs, provenance, multi-granularity summaries, and retrieval-time filtering. These mechanisms are easier to inspect, benchmark, and delete than knowledge embedded in model weights.

The papers fall into four clusters:

1. **Long-term agent memory:** store only useful information, distinguish episodic/semantic/procedural memory, consolidate related events, retain provenance, and retrieve at the right granularity.
2. **Continual adaptation:** parameter updates and model merging can reduce catastrophic forgetting, but they add complexity and make user-controlled deletion harder to guarantee.
3. **Selective forgetting and privacy:** deleting a database row is not the same as machine unlearning. If NeuroBrain fine-tunes on private data, it must test residual leakage; if it keeps the base model frozen, deletion can be made more tractable through provenance-aware cascading removal.
4. **On-device deployment:** model choice must be based on measured accuracy, latency, energy, and memory—not parameter count alone. Quantization is the first optimization to test, and a small local classifier can route intents before invoking a larger generator.

## What this means for the NeuroBrain design

### Recommended v1 architecture

Use a local, inspectable pipeline:

`local event -> privacy gate -> importance/intent filter -> episodic event record -> temporal/associative links -> vector + graph indexes -> query-time retrieval/filtering -> local LLM`

Each stored memory should have at least:

- a stable memory ID;
- source/provenance pointer;
- timestamp and validity interval;
- people/entities, action, project/topic, location/context, and causal links where available;
- memory type: working, episodic, semantic, or procedural;
- sensitivity and user policy tags;
- confidence, importance, and last-access score;
- links to derived summaries, embeddings, graph edges, and generated skills.

### Recommended forgetting contract

For v1, “forget” should mean a verifiable cascade across the external memory system:

1. tombstone the source memory;
2. remove it from lexical/vector indexes;
3. remove or recompute graph edges and summaries derived from it;
4. invalidate caches and generated skills that cite it;
5. run a before/after retrieval test showing that the deleted fact is no longer returned;
6. retain only a non-sensitive deletion audit record.

Call this **memory deletion** or **provenance-aware forgetting**, not full machine unlearning. Reserve “machine unlearning” for the later case where private user data has changed model parameters and the project evaluates residual influence using membership-inference or comparable attacks.

### Evaluation plan suggested by the literature

- **Memory quality:** information extraction, multi-session reasoning, temporal reasoning, knowledge updates, conflict handling, and abstention on LongMemEval-style tasks.
- **Conversation continuity:** long-range factual, temporal, causal, and summarization tasks on LoCoMo-style dialogues.
- **Forgetting:** retrieval non-reappearance, derived-artifact cleanup, privacy leakage tests, and retained-knowledge utility.
- **Local performance:** accuracy, time to first token, tokens/second, peak RAM/VRAM, energy, and storage growth.
- **Ablations:** flat vector retrieval versus temporal graph; raw turns versus structured events; all memories versus importance filtering; fixed versus adaptive retrieval depth.

## Paper-by-paper review

> Status labels distinguish peer-reviewed publications from preprints/surveys. Results are reported in the setting used by each paper and should not be treated as guaranteed NeuroBrain performance.

### 1. Memory Matters: The Need to Improve Long-Term Memory in LLM-Agents

**Status:** Short conceptual review/perspective in the *Proceedings of the AAAI Symposium Series* 2(1), 2024; the paper originated at the 2023 AAAI Fall Symposium. [Primary paper](https://ojs.aaai.org/index.php/AAAI-SS/article/download/27688/27461/31739)

- **What it studies:** How LLM agents currently use working and long-term memory, especially vector databases, and what is missing from a cognitively meaningful architecture.
- **Key ideas/results:** It distinguishes procedural, semantic, and episodic long-term memory. It argues that flat top-k similarity, mixed memory types, unlimited accumulation, and repeated failed procedures cause poor retrieval, contradictions, and loops. It recommends metadata such as reliability, success/failure frequency, time, and preference, plus ontology or knowledge-graph links.
- **Conclusion:** Agent memory needs organization and lifecycle management, not merely a larger vector store.
- **Limitations:** Four-page review; no system, dataset, or empirical validation.
- **Effect on NeuroBrain:** Strong rationale for separate working/episodic/semantic/procedural stores and success/failure metadata for generated skills. It supports the design direction, not a performance claim.

### 2. Development of a Human-inspired Long-Term Memory for Interactive Conversational Agents

**Status:** IEEE MetroXRAINE 2025, pp. 657–662, DOI 10.1109/MetroXRAINE66377.2025.11340339. [Bibliographic record and abstract](https://eurekamag.com/research/104/990/104990477.php)

- **What it studies:** Whether a conversational agent can keep only salient structured information instead of storing every dialogue turn.
- **Method:** A hierarchical episodic/declarative memory, graph-based persona, NoSQL storage, and an LLM agent that chooses what structured information to retain and retrieve.
- **Key result/conclusion:** The accessible abstract reports preliminary performance competitive with existing approaches while reducing the need to store full dialogue histories.
- **Limitations:** The accessible record provides no dataset, metrics, or numerical results; the performance claim could not be independently examined from full text.
- **Effect on NeuroBrain:** Supports selective admission, episodic/declarative separation, and a persona graph. NeuroBrain should treat this as a design precedent and validate the idea itself.

### 3. Structured Episodic Event Memory (SEEM)

**Status:** Peer-reviewed ACL 2026 long paper, pp. 6125–6141, DOI 10.18653/v1/2026.acl-long.277—not just the arXiv preprint listed in the CSV. [ACL paper](https://aclanthology.org/2026.acl-long.277/) · [Full HTML](https://arxiv.org/html/2601.06411v2)

- **What it studies:** How to replace fragmented, flat RAG retrieval with structured memory that preserves narrative and relational dependencies.
- **Method:** A Graph Memory Layer stores temporal `(subject, relation, object, time)` facts. An Episodic Memory Layer stores event frames containing a summary, participants, action, time, place, cause, manner, and provenance pointers. Associative fusion merges related frames; Reverse Provenance Expansion reconstructs supporting context.
- **Key results:** On LoCoMo, SEEM reports BLEU-1 56.1, F1 61.1, and judge score 78.0. On LongMemEval it reports 65.0 accuracy versus 60.6 for HippoRAG2, a 4.4-point gain.
- **Conclusion:** A linked event-frame and temporal-graph hierarchy improves temporal, multihop, and narrative retrieval over flatter baselines.
- **Limitations:** LLM extraction/fusion costs tokens and latency; extraction errors can corrupt persistent memory; fixed event slots may miss abstractions; persistent personal memory raises privacy risks.
- **Effect on NeuroBrain:** This is the clearest architectural blueprint in the list. Implement event frames, immutable source pointers, temporal graph links, fusion, and provenance expansion—but add confidence, rebuild tools, and deletion propagation.

### 4. EMA: An Episodic Memory Agent for Efficient and Selective Memory

**Status:** Findings of ACL 2026, pp. 5088–5102, DOI 10.18653/v1/2026.findings-acl.250. The CSV misspells third author Zhengjia Zhong. [ACL paper](https://aclanthology.org/2026.findings-acl.250/)

- **What it studies:** How to reduce redundant history and inference cost while retaining useful conversational memory.
- **Method:** Episodic Memory Units store event, time, participants, tags, summary, importance, and confidence. A MemDecider filters information before storage; later components organize, update, and retrieve the units.
- **Key results:** Across LoCoMo and LongMT+, adding MemDecider to memory methods reduced token use by 11.48% on average while generally maintaining or improving performance. The paper reports a decision threshold near 0.4 as a useful accuracy/efficiency balance.
- **Conclusion:** Admission filtering before memory construction is an effective and portable efficiency mechanism.
- **Limitations:** Text-only, small benchmark subsets, no explicit consent controls, and no strong guarantees of lifelong consistency.
- **Effect on NeuroBrain:** Add a pre-storage importance/confidence gate and periodic consolidation. Explicit user policy must override learned importance: “do not store” is never a model decision.

### 5. MINGLE: Mixture of Null-Space Gated Low-Rank Experts for Test-Time Continual Model Merging

**Status:** NeurIPS 2025 main-conference paper, DOI 10.52202/085713-4814; publication is confirmed. [NeurIPS record](https://proceedings.neurips.cc/paper_files/paper/2025/hash/d3a07e8ec40511778a757a30d1b83820-Abstract-Conference.html) · [Full HTML](https://arxiv.org/html/2505.11883v3)

- **What it studies:** Sequentially merging independently fine-tuned models while adapting to current unlabeled data and limiting catastrophic forgetting.
- **Method:** Rank-64 LoRA task experts, input-conditioned gating, null-space projection that protects earlier task representations, and adaptive relaxation between stability and plasticity.
- **Key results:** The authors report average gains of 7–9 points. One eight-task ViT-B/32 setting reaches 85.8 accuracy with backward transfer of -0.6, versus 75.5 and -6.3 for OPCM; GLUE results reach 83.3 accuracy and +0.1 backward transfer.
- **Conclusion:** Small test-time buffers plus protected low-rank experts can adapt with little measured forgetting in model-merging benchmarks.
- **Limitations:** Assumes common backbone/initialization; focuses mainly on classification and merging, not personal-memory retrieval; requires test samples and extra experts.
- **Effect on NeuroBrain:** Relevant only to an optional future parametric-adaptation layer. Keep it outside the external-memory MVP; if tested, isolate LoRA experts and measure backward transfer and local resource cost.

### 6. In Prospect and Retrospect: Reflective Memory Management for Long-term Personalized Dialogue Agents

**Status:** ACL 2025 long paper, pp. 8416–8439, DOI 10.18653/v1/2025.acl-long.413. [ACL paper](https://aclanthology.org/2025.acl-long.413/) · [Full HTML](https://arxiv.org/html/2503.08026v2)

- **What it studies:** The problems caused by fixed chunk sizes and fixed retrieval strategies in changing conversations.
- **Method:** Prospective Reflection creates topic-based summaries across utterance, turn, and session boundaries. Retrospective Reflection trains a lightweight residual reranker online with reinforcement learning from LLM evidence/citation feedback.
- **Key results:** With GTE retrieval, the paper reports MSC METEOR 33.4/BERTScore 57.1 and LongMemEval recall 69.8/accuracy 70.4. In a Contriever ablation, full RMM improves LongMemEval recall/accuracy from 54.3/58.8 to 60.4/61.2.
- **Conclusion:** Semantic consolidation plus adaptive reranking improves personalized retrieval.
- **Limitations:** Online RL adds cost; text-only evaluation; privacy is left for future work.
- **Effect on NeuroBrain:** Segment by topic/event rather than fixed token blocks, and log evidence attribution as retrieval feedback. Prefer cheap or batched reranking for the local MVP.

### 7. LLM Agnostic Query Response Personalization via Temporal Knowledge Graph Database

**Status:** IEEE NAECON 2026, pp. 66–71, DOI 10.1109/NAECON70028.2026.11674911. [DOI record](https://doi.org/10.1109/NAECON70028.2026.11674911)

- **What it studies:** Persistent personalization that does not depend on one LLM vendor.
- **Method:** A separate temporal knowledge graph per user stores interaction history and preferences and can be queried by any tool-capable LLM.
- **Key result/conclusion:** The paper proposes an LLM-agnostic temporal graph interface for personalized organizational search. The accessible record exposes no benchmark, metric, or quantitative result.
- **Limitations:** Performance evidence could not be independently assessed from accessible full text.
- **Effect on NeuroBrain:** Supports a model-agnostic local memory API and per-user isolation. Require timestamps, validity intervals, provenance, access controls, and graph-wide deletion cascades; benchmark against a vector-only baseline.

### 8. Private Data Protection With Machine Unlearning for Next-Generation Networks

**Status:** IEEE Open Journal of the Communications Society, vol. 6 (2025); online first 16 December 2024, DOI 10.1109/OJCOMS.2024.3518503. [IEEE record](https://ieeexplore.ieee.org/abstract/document/10804198)

- **What it studies:** Faster approximate instance-level unlearning without retraining a model from scratch.
- **Method:** Perturb the target model, then iteratively steer it toward a reference model trained on a subset of retained data. Evaluate forgetting with ordinary accuracy, membership inference, and a planted backdoor.
- **Benchmarks/results:** Five image-classification settings spanning MNIST, Fashion-MNIST, SVHN, and CIFAR-10 with several neural architectures. It reports about 15× speedup over retraining; a cited backdoor measure falls from roughly 98% to below 20% while retained performance remains close.
- **Conclusion:** A small retained-data reference model can guide faster approximate unlearning.
- **Limitations:** Image classifiers and a network/federated framing, not LLM graph memory; needs reference data and tuned hyperparameters; empirical attacks are not a formal deletion guarantee.
- **Effect on NeuroBrain:** Borrow the verification philosophy, not the weight-update algorithm, for v1. Delete raw data and every derivative, then test for residual retrieval/leakage. Parametric unlearning matters only after private data changes model weights.

### 9. Fast and Accurate Class-Level Machine Unlearning using Impair–Repair and Noise-Induced Forgetting Mechanisms

**Status:** *Cognitive Computation* 18, article 48 (2026), DOI 10.1007/s12559-026-10597-4. [Springer article](https://link.springer.com/article/10.1007/s12559-026-10597-4)

- **What it studies:** Fast removal of one or more target classes without retraining or destroying retained-class utility.
- **Method:** USI(F)R learns error-maximizing noise, performs an impair step, then repairs on retained data. DNF skips noise training and directly injects Gaussian noise before repair. Tests cover ResNet18, AllCNN, MobileNetV2, and ViT.
- **Key results:** Target-class accuracy is often driven to 0%. In CIFAR-10/ResNet18, retained accuracy is 74.97% for USI(F)R and 74.45% for DNF versus 71.06% for UNSIR. A cited DNF run takes 1.5 seconds versus 92 seconds. The paper itself inconsistently describes the test collection as ten versus twelve datasets.
- **Conclusion:** Trained noise may be unnecessary; direct noise plus repair can be much faster.
- **Limitations:** Class-level image classification, not per-record text/graph deletion; hyperparameters vary by model/data; zero target accuracy does not prove erasure.
- **Effect on NeuroBrain:** Only relevant if user data changes trainable weights. It does not justify calling graph-record deletion “machine unlearning.”

### 10. AdaProb: Efficient Machine Unlearning via Adaptive Probability

**Status:** Current v3 of arXiv:2411.02622, revised 9 April 2026; preprint, with a workshop version associated with DATA-FM at ICLR 2026. [Current arXiv record](https://arxiv.org/abs/2411.02622) · [v3 HTML](https://arxiv.org/html/2411.02622v3)

- **What it studies:** Approximate unlearning that makes forgotten examples behave more like data never seen while reducing computation and membership-inference risk.
- **Method:** Replace forget-set output probabilities with uniform pseudo-probabilities, refine forget/retain distributions under constraints, then backpropagate those targets into model weights.
- **Key results:** On CIFAR/Lacuna image tasks with ResNet18 and ALL-CNN, it claims more than 20% improvement in forgetting error and less than half SCRUB's runtime. Several membership-inference results approach chance, although a reported ResNet selective setting remains at 58%. Results reveal a strong retain/forget tradeoff controlled by the objective weight.
- **Conclusion:** Output-distribution refinement can approximate retraining more cheaply and reduce the tested leakage signal.
- **Limitations:** Approximate, classifier-only, narrow attacks/models, and no certified erasure or generative-LLM deletion.
- **Effect on NeuroBrain:** If online adaptation changes weights, compare the deleted model with a retain-only retrained oracle and add output-distance and membership tests. This method cannot be directly applied to inference-only GGUF models.

### 11. Pseudo-Probability Unlearning: Towards Efficient and Privacy-Preserving Machine Unlearning

**Status:** This is the **superseded v1 of the same arXiv record, 2411.02622**, not an independent current paper. [Frozen v1](https://arxiv.org/html/2411.02622v1)

- **What it studied:** The earlier PPU version used uniform/random pseudo-probabilities for forget examples, retained/refined other outputs, and updated weights on CIFAR-10 and Lacuna-10 classifiers.
- **Key result/conclusion:** It reported greater than 20% improvement over earlier methods, lower compute, and membership-inference results near chance in several settings.
- **Important bibliography issue:** v1 had six authors and the PPU title; v2/v3 became AdaProb with four authors. Rows 10 and 11 therefore double-count one evolving manuscript.
- **Effect on NeuroBrain:** Cite current AdaProb as the main reference; mention v1 only to document the method's evolution. It provides no second independent line of evidence.

### 12. Towards Benchmarking Privacy Vulnerabilities in Selective Forgetting with Large Language Models

**Status:** AAAI-26 Special Track on AI Alignment, *Proceedings of AAAI* 40(44), 37839–37848, DOI 10.1609/aaai.v40i44.41120. The CSV's 2025/preprint status is outdated. [AAAI paper](https://ojs.aaai.org/index.php/AAAI/article/view/41120)

- **What it studies:** How to compare privacy leakage after unlearning across inconsistent attacks, models, data, and deployment changes.
- **Method:** PrivUB evaluates membership inference, reconstruction, and knowledge leakage against deleted and retained data, before/after unlearning, fine-tuning, perturbation, and quantization. It covers 21 attack/defense methods, ten unlearning methods, eleven datasets, and ten vision/language models.
- **Key findings:** Combining attacks strengthens privacy tests; data perturbations can improve membership attacks; post-unlearning fine-tuning leaks more than quantization; attacks can transfer across deep networks and LLMs; defenses often weaken as attack sample count rises.
- **Conclusion:** Recall failure or one privacy metric is not enough; selective forgetting requires standardized multi-attack evaluation.
- **Limitations:** A benchmark, not a new deletion method; unseen adaptive attacks remain possible, and no single metric certifies erasure.
- **Effect on NeuroBrain:** Make this the Privacy Shield acceptance philosophy: test deleted and retained memories before and after adaptation and quantization, using membership, reconstruction, and knowledge-recovery/relearning probes.

### 13. On-device Large Language Models: A Survey of Model Compression and System Optimization

**Status:** *Artificial Intelligence Review* 59, article 191 (2026), DOI 10.1007/s10462-026-11538-1. [Springer article](https://link.springer.com/article/10.1007/s10462-026-11538-1)

- **What it studies:** How quantization, pruning, distillation, low-rank adaptation, runtimes, kernels, hardware, and KV-cache management combine in practical on-device systems.
- **Method/contribution:** A taxonomy plus the ALEM scorecard: Accuracy, Latency, Energy, and Memory. Its own small evaluation spans roughly 1B/4B models, several compression families, reasoning tasks, and latency/energy/VRAM measures.
- **Key conclusion:** Quantization is usually the first optimization for memory and time-to-first-token; distillation can improve throughput/energy; LoRA is useful for specialization but should be merged for serving; pruning needs sparse-aware kernels; KV cache must be treated as a first-class subsystem. There is no universal best method.
- **Limitations:** Hardware- and runtime-sensitive; narrow benchmark workload; not measured on NeuroBrain's exact target device or Ollama/GGUF stack.
- **Effect on NeuroBrain:** Adopt ALEM as the deployment scorecard and explicitly test long-context/KV-cache growth caused by retrieved memories.

### 14. A Systematic Evaluation of On-Device LLMs: Quantization, Performance, and Resources

**Status:** arXiv:2505.15030, current v5 dated 16 March 2026; no verified archival venue. [arXiv record](https://arxiv.org/abs/2505.15030) · [Full HTML](https://arxiv.org/html/2505.15030v5)

- **What it studies:** Capability, throughput, memory, CPU load, and power across realistic model sizes and llama.cpp quantizers on commodity hardware.
- **Method:** Qwen2.5/Qwen3/Llama3 models from roughly 0.5B–14B, multiple Q8/Q5/Q4/Q3/Q2 formats, five capability benchmarks, and synthetic prefill/decode workloads.
- **Key findings:** A larger heavily quantized model often beats a smaller high-precision model; capability drops sharply below roughly 3.5 effective bits per weight; memory scales approximately with bit width, while CPU/power also depend on operator efficiency. Large models tend to become bandwidth-bound; very small long-context models can become compute-bound.
- **Conclusion:** Around 4-bit larger models are often a good accuracy balance, but latency-oriented deployments may prefer a compact 4-bit model.
- **Limitations:** Preprint, one main laptop/OS, three runs per case, synthetic workload, and no memory-agent ingestion/retrieval or privacy tests.
- **Effect on NeuroBrain:** Directly relevant to GGUF selection. Benchmark larger-Q4 versus smaller-Q8 on the actual machine using ingestion, episodic retrieval, and skill-generation workloads.

### 15. MobileQuant: Mobile-friendly Quantization for On-device Language Models

**Status:** Findings of EMNLP 2024, pp. 9761–9771, DOI 10.18653/v1/2024.findings-emnlp.570—not merely an unverified preprint. [ACL paper](https://aclanthology.org/2024.findings-emnlp.570/)

- **What it studies:** Whether static integer-only weight-and-activation post-training quantization can preserve quality while exploiting mobile NPUs.
- **Method:** Jointly optimize equivalent weight transforms and activation ranges, then fold transforms into weights. Tests include W8A8/W4A8 variants of TinyLLaMA-1.1B, StableLM-2 1.6B, and Gemma-2B.
- **Key results:** On a Galaxy S24/Snapdragon 8 Gen 3, TinyLLaMA prompt latency drops from 510 ms to 276 ms and energy from 1000 mJ to 490 mJ for W8A8 versus W8A16. W4A8 improves Gemma-2B prompt/generation latency by 39%/33% versus W8A8 while remaining near-lossless on tested benchmarks.
- **Conclusion:** Hardware-friendly activation quantization matters for actual latency and energy, not just file size.
- **Limitations:** Small models, mainly one high-end mobile SoC, toolchain restrictions, and results that do not automatically transfer to CPU GGUF/Ollama.
- **Effect on NeuroBrain:** Supports a future mobile/NPU path. For the present desktop-local build, measure real runtime operators rather than assuming weight-only compression gives the same gains.

### 16. On-device Query Intent Prediction with Lightweight LLMs to Support Ubiquitous Conversations

**Status:** *Scientific Reports* 14, 12731 (2024), DOI 10.1038/s41598-024-63380-6. [Nature article](https://www.nature.com/articles/s41598-024-63380-6)

- **What it studies:** Whether sub-2GB pretrained encoders fine-tuned locally can classify user intent competitively with ChatGPT while keeping data on device.
- **Method:** Nine BERT-family models plus fine-tuned GPT-3.5, trained/evaluated on 1,317 GUI-related queries across scope, purpose, response format, and information-feature labels.
- **Key results:** RoBERTa Large reaches balanced accuracy of 84.2% for scope, 75.8% for purpose, and 62.8% for information feature; RoBERTa Base reaches about 89.9% for response format. Fine-tuned local models match or outperform the ChatGPT comparison in the tested classification tasks.
- **Conclusion:** A small, task-specific local intent router is viable.
- **Limitations:** Training used a V100; there was no real phone deployment, runtime, battery, online-learning, or broad-domain evaluation. The dataset is small and noisy.
- **Effect on NeuroBrain:** Use a small local intent/privacy-policy router before retrieval or tool execution, with abstention for ambiguity. This does not show that a full generative assistant runs well on device.

### 17. ScrapMem: A Bio-inspired Framework for On-device Personalized Agent Memory via Optical Forgetting

**Status:** arXiv:2605.03804v2 (25 May 2026); preprint, no verified peer-reviewed venue. [Full HTML](https://arxiv.org/html/2605.03804)

- **What it studies:** Years of multimodal personal memory under tight edge-device storage.
- **Method:** Time-grouped multimodal scrapbook pages, OCR/VLM descriptions and visual-token nodes, a causal-temporal Episodic Memory Graph, and progressive image resolution/JPEG degradation called Optical Forgetting.
- **Key results:** On ATM-Bench, the no-forgetting system reaches Joint@10 51.0 and Recall@10 70.3 versus 48.6 Joint@10 for ATM-RAG. A gentle timed policy uses 299.5 MiB versus 4302.9 MiB raw (93% saving) with Joint@10 46.3. However, 568 of 1,013 timed-gentle answers are strictly wrong; 58.6% of failures are retrieval failures.
- **Conclusion:** Visual consolidation and graph paths offer a useful storage/accuracy tradeoff.
- **Limitations:** Compression destroys exact details; graph extraction is noisy; real open-world tool use is untested.
- **Effect on NeuroBrain:** Adopt tiered retention—recent raw evidence plus compressed archive and graph—but never equate lossy compression with privacy deletion. Protected facts and identifiers need lossless policy-aware handling.

### 18. Graph-Based Personalized Memory for LLM Agents: Representation, Evolution, Retrieval, and Evaluation

**Status:** arXiv:2609.08599v1 (8 September 2026); survey preprint. [Full HTML](https://arxiv.org/html/2609.08599)

- **What it studies:** The complete lifecycle of graph-based personalized memory.
- **Contribution:** A taxonomy covering representation (flat, hierarchical, hypergraph, hybrid, multiple graphs), evolution (admission, integration, conflict resolution, consolidation, removal), retrieval, and evaluation. It distinguishes reducing exposure/weight/resolution from actual deletion.
- **Key conclusions:** Evidence-rich memories improve provenance and correction; compressed abstractions save space but can propagate extraction errors; “newest wins” is insufficient because supersession, correction, and context-dependent coexistence are different.
- **Limitations:** No new experiment; young and mostly text-based field; weak evaluation of graph-internal correctness and little lifelong real-world evidence.
- **Effect on NeuroBrain:** Shape the memory API around immutable evidence, versioned active facts, validity intervals, explicit admission/consolidation/conflict/deletion operations, and graph-correctness tests—not answer accuracy alone.

### 19. DYNA: Dynamic Episodic Memory Networks for Augmenting Large Language Models with Temporal Knowledge Graphs in Continuous Learning

**Status:** arXiv:2606.15778 (14 June 2026); preprint. [arXiv paper](https://arxiv.org/abs/2606.15778)

- **What it studies:** Whether a frozen LLM can absorb sequential temporal events through an external graph, without retraining.
- **Method:** Timestamped event nodes and temporal edges with decay/pruning; semantic seeds, weighted random walks, and centrality ranking retrieve a subgraph for Llama-3-8B-Instruct.
- **Key results:** Across TimeQA, ChronoScope, TIME, and LoCoMo, DYNA reports temporal ordering accuracy 71.42, temporal-scope stability 66.23, catastrophic-forgetting rate 1.12, and P@5 50.28, versus RAG at 61.85/55.34/2.14/38.24. Removing random walks costs 7.59 ordering points. Top-1 precision remains only 21.28%.
- **Conclusion:** Temporal graph structure can improve sequential recall without updating the base model.
- **Limitations:** Weak top-1 precision, cold-start underperformance, about 0.9-second retrieval at 10k nodes, simplified tasks, and one 8B model. The CSV says three tasks, while the paper evaluates four datasets.
- **Effect on NeuroBrain:** Strong support for external temporal memory with frozen weights. Use hybrid vector retrieval during cold start, then graph traversal when relationships become dense; benchmark latency and top-1 retrieval.

### 20. CAMPHOR: Collaborative Agents for Multi-input Planning and High-Order Reasoning On Device

**Status:** REALM 2025 workshop at ACL, pp. 33–51, DOI 10.18653/v1/2025.realm-1.3. The CSV's 2024 date is the first arXiv date. [ACL paper](https://aclanthology.org/2025.realm-1.3/)

- **What it studies:** Whether shared on-device small models can decompose composite requests, retrieve personal context, and call tools without cloud communication.
- **Method:** One shared Phi-3.5 or Gemma-2 behind a high-level orchestrator and role-specific agents for personal context, device state, perception, external knowledge, and task completion; dynamic prompts and prompt compression.
- **Key results:** On 3,410 synthetic/human-reviewed device queries, fine-tuned Phi-3.5 scores Tool F1 67.84, delexicalized Plan F1 44.85, and Plan F1 38.77, versus Claude-3.5 at 51.31/30.07/27.96. Untuned Phi-3.5 is far worse, showing that specialization is essential.
- **Conclusion:** A specialized local small-model orchestrator can beat prompted cloud models on this narrow simulated task.
- **Limitations:** Single-turn, simulated devices, mostly synthetic data, happy-path execution, and no direct privacy attack or real-device latency evidence.
- **Effect on NeuroBrain:** Useful for skill synthesis and routing: shared quantized backbone plus role-specific prompts, plan decomposition, local context gates, and explicit permission/confirmation around actions.

### 21. Federated Meta Unlearning Based on Model Decomposition and Weighted Aggregation

**Status:** *Scientia Sinica Informationis* 55(11), p. 2722 (2025), DOI 10.1360/SSI-2025-0221. The accessible publisher/index record lists six authors, whereas the CSV lists twelve. [Publisher PDF link](https://www.sciengine.com/doi/pdf/3A8C50FABCA846AE9C8FCFDEF820D2C1)

- **What it studies:** Selective unlearning in federated learning with less retraining cost.
- **Method:** MAML-based meta-unlearning, hierarchical decomposition of a global model into editable modules, targeted parameter adjustment/removal, and weighted reaggregation.
- **Key result/conclusion:** The accessible abstract claims lower computation than retraining, MAML retraining, SISA, and gradient methods while retaining performance across multiple/cross-modal tasks. Full quantitative details could not be independently verified from accessible text.
- **Limitations:** Federated global models differ materially from NeuroBrain's single-device external memory; abstract-only numbers should not guide implementation.
- **Effect on NeuroBrain:** The modularity lesson is useful: keep user-specific adaptations independently removable. Build deterministic external-memory deletion first; weight unlearning needs attack-based verification.

### 22. TAPE: A Temporal Graph-Based Memory System for Personal LLM Agents

**Status:** ICDE 2026 demo paper, pp. 4168–4171, DOI 10.1109/ICDE65706.2026.00318. [Official ICDE demo list](https://icde2026.github.io/demo-papers.html) · [DBLP record](https://dblp.uni-trier.de/rec/conf/icde/LuoLZG26.html)

- **What it studies:** Persistent personal memory that models how facts and preferences change over time.
- **Method:** Extract entities, relations, and temporal metadata from multiple user sources into a temporal graph, then retrieve historical context with two community-search algorithms.
- **Key result/conclusion:** The four-page demo claims qualitative improvements in temporal reasoning and personalization, but accessible records expose no dataset, quantitative table, or sufficient algorithm detail.
- **Limitations:** Closed-access short demo; insufficient public evidence for a performance claim. Some indexes normalize the second author differently; the official conference listing agrees with the CSV's Qing Liu.
- **Effect on NeuroBrain:** Direct architectural precedent for multi-source ingestion, temporal graphs, and community/subgraph retrieval. Treat it as design inspiration and benchmark the prototype against vector-only and time-filtered baselines.

## Cross-paper conclusions for NeuroBrain

### What the literature strongly supports

- **External memory before parametric learning.** SEEM, EMA, RMM, DYNA, and the graph-memory survey all support structured memory around an LLM. This is easier to inspect, update, and delete than continuous weight updates.
- **Hybrid representation.** Use vector similarity for candidate recall, event/temporal graphs for structure, summaries for compression, and raw evidence pointers for verification.
- **Admission and consolidation.** Not every event deserves long-term storage. Combine learned salience with hard user privacy policies and periodic event/topic consolidation.
- **Time and provenance are mandatory.** Personal facts change. Store validity intervals, source evidence, version history, and links from every summary/edge/skill to its inputs.
- **Local deployment must be measured.** Quantization can help, but actual gains depend on bit width, kernels, runtime, KV cache, and hardware.

### What the literature does not yet justify

- A claim that NeuroBrain has human-like memory merely because it uses cognitive labels.
- A claim that a temporal or associative graph is always better than vector RAG without an ablation on the same workload.
- A claim that deletion from a vector/graph store is full machine unlearning.
- A claim that failed recall, 0% target accuracy, local execution, or quantization alone proves privacy.
- A claim that Titans/Mamba-style online weight updates are necessary for the first prototype.

## Recommended implementation priorities

1. **Build an auditable external-memory MVP:** privacy gate, structured episodic events, raw provenance, temporal links, vector index, and local retrieval.
2. **Implement deletion correctly:** cascade through source records, embeddings, graph edges, summaries, caches, and skills; produce a deletion manifest and residual-retrieval test.
3. **Add conflict/version handling:** distinguish correction, supersession, and context-dependent coexistence.
4. **Benchmark memory:** vector-only vs graph-assisted; raw turns vs event frames; no filter vs admission filter; fixed vs adaptive retrieval.
5. **Benchmark local inference using ALEM:** accuracy, TTFT/tokens per second, energy, RAM/VRAM, and KV-cache growth on the real target computer.
6. **Only then test parametric adaptation:** isolate LoRA/test-time experts, track backward transfer, and add PrivUB-style privacy attacks before claiming unlearning.

## Reading priority for the team

**Read first:** 3 (SEEM), 4 (EMA), 6 (RMM), 12 (PrivUB), 13 (on-device survey), 14 (on-device evaluation), 18 (graph-memory survey).

**Read for implementation details:** 16 (intent router), 19 (DYNA), 20 (CAMPHOR), 15 (MobileQuant).

**Read as future/advanced work:** 5 (MINGLE), 8–11 and 21 (weight unlearning), 17 (multimodal archival compression), 22 (TAPE demo).

## Bibliography and metadata corrections

- Paper 3 is now an ACL 2026 paper, not only an arXiv preprint.
- Paper 4 is Findings of ACL 2026; the third author is Zhengjia Zhong.
- Paper 5 is published at NeurIPS 2025.
- Paper 6 is an ACL 2025 long paper.
- Papers 10 and 11 are versions of the same arXiv record and should not count as independent evidence.
- Paper 12 is an AAAI 2026 paper, not merely a 2025 preprint.
- Paper 14 remains a preprint as verified here.
- Paper 15 is Findings of EMNLP 2024.
- Paper 20 is a REALM 2025 workshop paper; 2024 is its arXiv submission year.
- Paper 21's accessible records list six authors, not the twelve in the CSV.

## Methodology and confidence

The CSV and NeuroBrain blueprint were read locally. Each paper was checked against an official publisher, conference anthology, DOI record, or arXiv full text where available. Claims were kept at the level supported by accessible evidence. Papers 2, 7, 21, and 22 had limited accessible full text or quantitative detail, so their performance claims are treated as low-confidence design context rather than implementation evidence. The remaining summaries have medium-to-high confidence, but reported results have not been independently reproduced.

