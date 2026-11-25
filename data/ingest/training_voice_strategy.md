# Training voice strategy (Sky / Welles LoRA)

**North star:** **Start-to-end screenplay writing** — structure and language first, **scene composition** (Welles-scale blocking, depth, lens), then chained scenes across a whole script.

**Layers:**

1. **Structure & language** — full scenes in industry format (`STRUCTURE`, `SCREENPLAY` verbatim); beat and turn awareness.
2. **Composition** — staging → full scene (`COMPOSE`: action/slugline spine expanded to dialogue and blocking).
3. **Continuity** — in-scene `CONTINUE` and cross-scene `BRIDGE` from your uploaded PDFs (Kane heaviest).

**Anchor:** **Citizen Kane** (highest weight). Welles PDFs = primary. A24 = optional **format** diversity (not voice target).

Legacy **staging-only** mode (short action excerpts, dialogue stripped) is for quick experiments; **use full mode** for your goal.

---

## What you're training (and what you're not)

| Signal | Role in SFT |
|--------|-------------|
| `data/welles_gold.jsonl` | Desk-matched **WRITE / REWRITE / CONTINUE** — primary **voice** |
| `data/style_samples/` | Oratorical, deliberate nonfiction / broadcast register |
| **Citizen Kane** staging (MovieSum NC excerpts, manual Kane PDF → excerpt `.txt`) | **Gold-adjacent** script register: angles, doorways, deep focus, theatrical scale |
| Other **Welles-directed** script chunks (manual or HF when available) | High priority manual set; same prompt family as Kane |
| **A24** scripts (manual excerpts only) | **Scene grammar** only — teach *layout*, not *voice* |
| `ingest_cinema.py` wiki plots | Cinematic *substance* under Welles prompts; capped so gold dominates |

**Not a target:** Verbatim A24 quips, therapy-speak, minimalist indie dialogue, or “literary screenplay” interior monologue that never appeared in Welles's staged world.

---

## Citizen Kane = highest weight (recipe)

1. **Gold loop:** `prepare_data.py --gold-repeat 4` (or higher) — Kane-specific *gold rows* stay in `welles_gold.jsonl`; repeat applies to all gold, which is already Kane-heavy in intent.
2. **Script tier:** Prefer MovieSum + manual Kane before anything else:
   ```bash
   python3 scripts/ingest_scripts.py --dataset moviesum --filter welles --max-pairs 30 \
     --boost-titles "citizen kane" --boost-repeat 3
   ```
3. **Prepare merge:** Boost Kane script rows again at train-mix time:
   ```bash
   python3 scripts/prepare_data.py --gold-repeat 4 --citizen-kane-repeat 3 \
     --max-scripts 40 --max-cinema 60
   ```
4. **Manual Kane PDF:** Drop `Citizen_Kane_1941.pdf` in `data/scripts/welles/incoming/`, run `import_uploaded_pdfs.py --studio welles`, ingest with `--dataset manual --filter welles`. Welles manual chunks use **WRITE** prompts (native register); A24 manual uses **STAGE** (see below).

**Order of precedence for script pairs in the mix:** Kane (Welles) → other Welles manual → MovieSum Welles filter → A24 manual (STAGE) → A24 MovieSum excerpts (capped).

---

## SFT task shapes

Use the same system prompt (`prompts/welles_system.md`) for all rows.

| Prefix | When | Assistant should |
|--------|------|------------------|
| **WRITE.** | Gold, style samples, Kane / Welles manual, MovieSum Welles | New prose in Welles voice; staging register; **no quoted dialogue** |
| **REWRITE.** | Gold desk tasks | Same image, Welles diction and rhythm |
| **STAGE.** | **A24 manual** drops (and optional REWRITE exercises on thin action) | **Restage** the scene: oratorical camera, scale, shadow, blocking — **do not** mimic A24 character voice |

**Manual A24 prompt wrapper (enforced in `ingest_scripts.py`):**

> STAGE. Restage this scene direction in Orson Welles's cinematic prose — deep space, theatrical lighting, deliberate camera rhythm. Keep slugline logic; no contemporary indie dialogue tone. Source: `{title}`.

**Manual Welles prompt (native):**

> WRITE. New prose in Welles's voice. Deliver prose in screenplay staging register — angles, light, doorways — without quoted dialogue. Manual welles drop: `{title}`.

---

## Full screenplay mode (dialogue + scenes)

**Default until now:** `staging` — strip most dialogue, 3 short action chunks per PDF (Welles *prose* / A24 *STAGE* rewrite).

**If you want the model to learn real screenplay format** (sluglines, cues, dialogue, action), use **full** mode:

1. Extract:
   ```bash
   python3 scripts/import_uploaded_pdfs.py --studio welles --full-screenplay
   python3 scripts/import_uploaded_pdfs.py --studio a24 --full-screenplay
   ```
   Writes `data/scripts/<studio>/{stem}_full.txt` — entire PDF text, dialogue kept.

2. Ingest (all scenes, no per-file chunk cap):
   ```bash
   python3 scripts/ingest_scripts.py --dataset manual --filter welles \
     --screenplay-mode full --max-pairs 0 --max-words 380 \
     --boost-titles "citizen kane" --boost-repeat 3
   ```

3. Ingest **multi-task** rows per scene (`--task-mix`):
   ```bash
   python3 scripts/ingest_scripts.py --dataset manual --filter welles \
     --screenplay-mode full --max-pairs 0 \
     --task-mix "verbatim,continue,compose,bridge,structure" \
     --boost-titles "citizen kane" --boost-repeat 3
   ```

4. Train mix:
   ```bash
   python3 scripts/prepare_data.py --gold-repeat 3 --max-scripts 0 \
     --script-screenplay-mode full --fetch-scripts --script-dataset manual \
     --script-filter all --max-script-ingest 0 --citizen-kane-repeat 3
   ```

**Note:** One 120-page PDF becomes **many** SFT rows (one per scene chunk), not one row. `train.py` uses `max_length=2048` so chunks fit. **Copyright:** full scripts in `train.jsonl` / Hub weights is higher risk than staging excerpts — use private repo and accept licensing limits.

**Voice vs format:** Full mode teaches **format and content of the script text**; `welles_gold` still carries **Welles desk voice** for the product UI. Blend both in the mix.

---

## A24 scripts: keep, but filter how you *use* them

**Tone mismatch (honest):** A24 house style skews toward naturalistic speech, irony, and literary PDF formatting. Welles skews toward **declamation, baroque composition, and visible craft**. Training on A24 **dialogue** or **unfiltered action** risks pulling the LoRA toward MFA-screenplay cadence.

**Recommendation:**

| Keep in repo? | Use in SFT? |
|---------------|-------------|
| **Yes** — full PDF library in `incoming/` for study and extraction | **Partial** — ingest **action / sluglines only** (existing `strip_dialogue_plain`), **STAGE** prompts, **low cap** (`--max-scripts` 25–40 total; A24 subset ≤ 50% of script rows) |
| Titles closest to Welles energy (*The Tragedy of Macbeth*, *The Zone of Interest*, *The Brutalist*, *White Noise*) | Slightly higher manual priority if you hand-pick excerpts — still **STAGE**, not verbatim |
| Pure talk pieces (*The Humans*, *Past Lives*, *Minari*) | Deprioritize or skip for voice LoRA; fine for scene-structure drills only |

**Do not** commit real copyrighted PDFs to a **public** GitHub repo unless you accept redistribution risk; placeholders in `incoming/` are fine for pipeline tests.

---

## Welles film scripts: priority manual set

After Kane, prioritize uploads (PDF → excerpt `.txt`) for:

Touch of Evil, The Lady from Shanghai, The Magnificent Ambersons, Chimes at Midnight, F for Fake, The Trial, Othello (1952), Macbeth (1948).

Use `import_uploaded_pdfs.py --studio welles` then `ingest_scripts.py --dataset manual --filter welles`.

Metadata index: `data/ingest/welles_script_slug_index.json` (study links only; not auto-scraped).

---

## Metadata in `script_pairs.jsonl`

Each pair may include:

- `source_studio`: `welles` | `a24` | `moviesum` | `movies`
- `source_title`: human title string
- `boosted`: true if duplicated by `--boost-titles`

`prepare_data.py` reads only `prompt` / `completion`; metadata is for auditing and future weighting.

---

## One-shot train mix (voice-first)

```bash
# Cache script staging (HF + optional manual after real PDFs extracted)
python3 scripts/ingest_scripts.py --dataset moviesum --filter welles --max-pairs 20 \
  --boost-titles "citizen kane" --boost-repeat 2
python3 scripts/ingest_scripts.py --dataset manual --filter all --max-pairs 30  # after .txt exists

python3 scripts/prepare_data.py \
  --gold-repeat 4 \
  --citizen-kane-repeat 2 \
  --max-examples 150 \
  --max-cinema 60 \
  --max-scripts 35 \
  --scripts-cache data/ingest/script_pairs.jsonl
```

`data/ingest/script_pairs.jsonl` is **gitignored** — regenerate locally; rely on `welles_script_pairs_sample.jsonl` for CI smoke.

---

## Summary for Sky

- **Target:** Welles **mise-en-scène** prose, Kane-weighted.
- **A24:** Keep files for breadth; train on **stripped action + STAGE prompts** only; expect **tone drift** if you raise A24 caps or include dialogue.
- **Kane:** `--boost-titles citizen kane`, `--citizen-kane-repeat`, and high `--gold-repeat` — stack all three for anchor strength.