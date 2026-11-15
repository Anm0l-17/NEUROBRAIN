# Attribution and scoped forget evaluation, 16 November 2026

Loaded the saved compact adapter from Kaggle notebook output. SHA-256 was 78bbf6fb49959a38dd95e4d84701d0ee64624703000eb3e19c84631fcdce5110. Used the original pinned base, NF4, greedy decoding, thinking disabled and 180-token output limit. The reference answers were excluded from generation. After the six paired probes, one expanded system instruction was tested on both models across the original nine plus the six new prompts. Only the prompt changed. The notebook records the wording. The original nine under the original prompt are the 14 November measurements.

| Model and prompt | Original nine | New six | Complete pairs |
|---|---:|---:|---:|
| Base, original | 6/9 | 5/6 | 2/3 |
| Compact adapter, original | 8/9 | 5/6 | 2/3 |
| Base, expanded | 7/9 | 4/6 | 1/3 |
| Compact adapter, expanded | 9/9 | 4/6 | 1/3 |

Manual scoring requires supported content, correct ownership, a direct answer and the E1 citation. On the original nine with the expanded instruction, the base omitted the medication citation and answered “My cousin” in the assistant voice, which fails the previous strict ownership rule. On the new comic question the expanded base correctly identified the character's home but omitted that the user's residence is unknown. Giving credit for implied abstention raises only that model's new score to 5/6. It still misattributed the radio narrator's occupation.

Both original-prompt models failed the fictional courier residence and passed the other five new cases. The expanded adapter fixed the old vineyard error, kept the courier error and newly attributed the radio narrator's occupation to the author. All four configurations preserved direct or confirmed facts and correctly interpreted both forget instructions. All 12 expanded-adapter and original-adapter answers across the new probes cited E1. Citation presence does not identify the correct owner.

Decision: keep the expanded prompt experimental. Next candidate intervention is paired fictional and autobiographical training examples with different facts, plus a new frozen evaluation set prior to training. These six are now development regressions. Generalization, storage deletion, retrieval and live behavior remain untested.
