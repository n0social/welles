# Full screenplay task types (ingest)

Each **scene chunk** from a `*_full.txt` file can emit several training rows (`--task-mix`):

| Task | Prompt prefix | Teaches |
|------|----------------|---------|
| **verbatim** | `SCREENPLAY. Full scene block…` | Complete scene text (slugline, action, cues, dialogue) |
| **continue** | `SCREENPLAY. Continue this scene…` | Mid-scene forward writing (start → finish inside a scene) |
| **compose** | `COMPOSE. From this staging…` | Action/slugline spine → full staged scene (composition + language) |
| **bridge** | `SCREENPLAY. Write the next scene…` | Scene-to-scene continuity from prior ending |
| **structure** | `STRUCTURE. Analyze beat function…` | Scene role in the script (beat, hinge, pressure) |

**Path to a full script:** many scenes ingested in order → `bridge` + `continue` + `verbatim` teach local and sequential text; `compose` ties **mise-en-scène** to page form; `welles_gold` stays the **desk voice** for polished prose outside raw slugline paste.

## Collect all scripts, then train (two phases)

**Phase 1 — build corpus** (all PDFs → one local file):

```bash
python3 scripts/build_script_corpus.py
# → data/ingest/script_pairs.jsonl (gitignored; re-run when you add PDFs)
```

**Phase 2 — mix + train:**

```bash
python3 scripts/prepare_data.py --fetch-scripts --scripts-cache data/ingest/script_pairs.jsonl \
  --max-scripts 0 --gold-repeat 3 --max-cinema 40
python3 scripts/train.py
```

Use `--build-train` on `build_script_corpus.py` to run prepare in one shot.