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

After PDF upload:
```bash
python3 scripts/import_uploaded_pdfs.py --studio welles --full-screenplay
python3 scripts/ingest_scripts.py --dataset manual --filter welles --screenplay-mode full --max-pairs 0
```