# Kaggle sources for Welles / A24 / screenplay ingest

Survey date: 2026-11-24. Method: `site:kaggle.com` search, public dataset pages, Hugging Face cross-links noted where authors cite them.

## Local copy (this VM / Colab)

After `git pull`, run:

```bash
python3 scripts/fetch_external_datasets.py --hf inkwell,atum09
python3 scripts/fetch_external_datasets.py --dataverse-movie-corpus   # or --kaggle-movie-corpus
python3 scripts/convert_external_datasets.py --inkwell-eval --atum09-max 500
```

Files land in `data/external/` (gitignored). See `data/external/README.md`.

## Executive summary

| Topic | On Kaggle? |
|-------|------------|
| **Orson Welles–specific screenplays / scripts** | **No dedicated dataset.** Filter general script corpora by title, writer, or director metadata (e.g. *Citizen Kane*, *Touch of Evil*, writer `Orson Welles`). |
| **A24 full screenplay text** | **No.** A24 Kaggle sets are **film catalog metadata** (titles, budgets, writers credited on IMDb/Wikipedia), not script bodies. |
| **Indie / substitute screenplay corpora** | **Yes** — several large IMSDb-derived or multi-source script collections; plot/summary alternatives are safer for redistribution (see `data/ingest/README.md`). |

Welles SFT guidance matches the cinema tier: prefer **plot / staging / paraphrase** tasks over verbatim copyrighted dialogue unless license and use case are explicit.

---

## Findings table

| Title | URL | License / tags | Size (est.) | Fit for Welles SFT | Recommendation |
|-------|-----|----------------|-------------|-------------------|----------------|
| **Movie Scripts Corpus** | https://www.kaggle.com/datasets/gufukuro/movie-scripts-corpus | CC BY-NC-SA 4.0; screenplay, NLP, metadata | ~2.22 GB (2858 full scripts + metadata + character fragments) | **High** as *offline* screenplay pool; filter Welles titles via `writers` / `directors` in metadata | **Use (filtered, NC)** — structure/staging excerpts only in repo; full download manual/Kaggle only. Non-commercial. |
| **movie-screenplays-tokenized-dataset** | https://www.kaggle.com/datasets/raghavnimbalkar10/movie-screenplays-tokenized-dataset | MIT; `text`, tokenized LM | ~492 MB JSON; ~94M tokens, ~2400 scripts | **Medium** — good for format priors, not voice; 512-token blocks | **Manual-only** for training mix unless you re-decode to text and apply same excerpt policy as MovieSum. HF mirror: https://huggingface.co/datasets/raghavnimbalkar/movie-screenplays-tokenized-dataset |
| **IMSDb Movie Scripts** | https://www.kaggle.com/datasets/veeralakrishna/imsdb-movie-scripts | (page often rate-limited); IMSDb-sourced scripts | Varies (community scrape; see notebooks) | **Medium** — classic Hollywood scripts; may include Welles-era titles unlabeled | **Avoid verbatim ingest** in git; **manual-only** study. Copyright on scripts. DOI listings: 10.34740/kaggle/dsv/10096930 |
| **The Internet Movie Script Dataset** | https://www.kaggle.com/datasets/prasad22/the-internet-movie-script-dataset | CC0 (dataset page); IMSDb | ~694 KB xlsx (~60 scripts); Kaggle UI also lists larger CSV bundles (~121 MB) from other contributors | **Low–medium** — tiny labeled set; unclear Welles coverage | **Manual-only** for full scripts; CC0 claims do not clear underlying script copyright. |
| **Balanced Hollywood Movies Scripts Age Rating Data** | https://www.kaggle.com/datasets/pratik2kcn/balanced-hollywood-movies-scripts-age-rating-data | CC BY-NC 4.0; MPAA labels | 250 full `.txt` scripts | **Low** for Welles voice; **medium** for screenplay formatting / censorship research | **Avoid** default Welles mix (modern mainstream bias). NC license. |
| **Movies and Movie Scripts** | https://www.kaggle.com/datasets/torloweidadata/movies-and-movie-scripts | License unclear on page | Unknown | Unknown pairing of actors ↔ scripts | **Avoid** until license and content documented. |
| **Wikipedia Movie Plots** | https://www.kaggle.com/datasets/jrobischon/wikipedia-movie-plots | CC BY-SA 4.0; plots, metadata | ~81 MB CSV (~35k plots) | **High** — same lineage as HF `vishnupriyavr/wiki-movie-plots-with-summaries` (already in cinema ingest) | **Use** — primary Kaggle mirror for plot-tier ingest; boost `Director` contains `Welles`. |
| **Wikipedia Movie Plots with AI Plot Summaries** | https://www.kaggle.com/datasets/gabrieltardochi/wikipedia-movie-plots-with-plot-summaries | Derived from jrobischon | ~95 MB CSV | **Medium** — shorter spans for context limits | **Use** optional; summaries are model-generated, not Welles voice. |
| **Wikipedia Movie Articles [Wiki dump] + Vector Text** | https://www.kaggle.com/datasets/mauryansshivam/wikipedia-movies-articles-from-wikipedia-dump | CC BY-NC-SA 4.0 | ~475 MB | **Medium** — plots + infobox; includes *Citizen Kane* article text | **Use (NC)** for encyclopedic cinema prose; not screenplay register. |
| **Top 500 Movies Ranked…** | https://www.kaggle.com/datasets/prashant0kumar7/top-500-movies-ranked-by-combined-critics | Combined ratings | ~265 KB | **Low** — metadata + short plot; includes Kane/Welles row | **Use** only for Welles-title **metadata joins**, not text volume. |
| **Cornell Movie-Dialogs Corpus** | https://www.kaggle.com/datasets/rajathmc/cornell-moviedialog-corpus (mirror: `soumikrakshit/cornell-movie-dialogs-corpus`) | Research / classic distribution | ~20 MB text bundles | **Low** for Welles SFT — quoted dialogue | **Avoid** for redistributable SFT (aligns with `data/ingest/README.md`). |
| **A24 Studio movies dataset** | https://www.kaggle.com/datasets/sebastiansuliborski/a24-studio-movies-dataset | “Data files © Original Authors” | ~66 KB CSV | **N/A for scripts** — has `Written by`, `Screenplay by` columns | **Use** for **title list / join keys** to future script sources; not text. |
| **A24 Movie Database** | https://www.kaggle.com/datasets/dvdlws/a24-movie-database | CC BY-SA 4.0 | ~54 KB | **Metadata only** (IMDb, RT, Letterboxd) | **Use** for analysis cards; not SFT text. |
| **A24 Films** | https://www.kaggle.com/datasets/alsyab/a24-films | CC BY-NC-SA 4.0 | ~7 KB CSV | **Catalog** from a24films.com | **Use** lightweight title/year index; NC. |
| **IMDb Dataset - From 1888 to 2023** | https://www.kaggle.com/datasets/komalkhetlani/imdb-dataset | IMDb-derived; “Other” | ~488 MB multi-file | **Join layer** — find Welles writer/director credits, A24 titles | **Use** metadata joins; **not** screenplay text. |
| **Indian Movies and Web Series Scripts** | https://www.kaggle.com/datasets/himanshubajpai/indian-movies-and-web-series-scripts | Open scripts claimed | Small–medium | **Low** — wrong language/register for Welles voice | **Avoid** for this project unless doing multilingual experiments. |
| **Marvel Cinematic Universe Dialogue** | https://www.kaggle.com/datasets/pdunton/marvel-cinematic-universe-dialogue | Script/transcript mix | CSV per project | **Low** — franchise dialogue | **Avoid** for Welles tone. |

---

## Orson Welles: closest neighbors on Kaggle

No dataset is labeled “Orson Welles screenplays.” Practical paths:

1. **Wikipedia Movie Plots** (`jrobischon/…` or HF mirror) — rows with `Director` = Orson Welles or titles such as *Citizen Kane*, *The Magnificent Ambersons*, *Touch of Evil*, *The Lady from Shanghai*, *Macbeth* (1948), *Othello*, *The Trial*, *Chimes at Midnight*, *F for Fake*.
2. **Movie Scripts Corpus** — query metadata `writers` / `directors` for `Welles`; extract **scene description** snippets, not dialogue blocks, if NC research training is allowed.
3. **Manual / PD** — Welles radio scripts and PD-era materials belong in `data/style_samples/` or gold, not scraped IMSDb dumps in git.

Confirmed: **no Kaggle hit** for “Orson Welles screenplay” as a standalone corpus.

---

## A24: closest neighbors on Kaggle

**No A24 screenplay corpus** on Kaggle. Available resources:

- Catalog CSVs with **screenwriter credits** (not body text).
- For indie **screenplay style** substitute, use general corpora and **filter** to A24-adjacent eras/genres (arthouse drama, horror A24 wave) via metadata — still copyrighted if taking full dialogue from IMSDb-class sets.

Suggested workflow: maintain `a24_titles.csv` (from Kaggle metadata) → join when/if scripts are sourced legally elsewhere (e.g. licensed PDFs, author-permitted indie corpora).

---

## AlexPMorton/A24-Movies-EDA (GitHub — **not** a Kaggle dataset)

| Field | Detail |
|-------|--------|
| **URL** | https://github.com/AlexPMorton/A24-Movies-EDA |
| **On Kaggle?** | **No** — `site:kaggle.com AlexPMorton` returns no matching dataset. Users sometimes conflate this repo with Kaggle A24 CSVs. |
| **Contents** | Jupyter EDA notebook (`A24_EDA.ipynb`), scraped **metadata** for A24 theatrical releases through **2022-09-26**, plus Oscar-winner join. **No screenplay text.** |
| **License** | No explicit OSS license in repo root; treat files as **author’s tables** — fine for title/box-office research, not for republishing as a “script corpus.” |
| **Size** | ~118 released-movie rows in `A24 Released Movies/A24_Released_Movies_2022_09_26.csv` (~11 KB CSV); joined Oscar file ~11 KB; notebook ~1.1 MB. |
| **Primary CSV columns** | `title`, `release_date`, `genre`, `director`, `budget`, `domestic_revenue`, `international_revenue`, `worldwide_revenue`, `runtime`, `MPAA_rating` (Oscars file adds `oscar_win` YES/NO; uses `mpaa_rating` lowercase) |
| **Upstream sources (per README)** | a24films.com catalog, Wikipedia genres/budgets, Box Office Mojo / The Numbers revenues, Wikipedia Academy Award winners list (scraped). |
| **Fit for Welles SFT** | **High** for **title list / year / director joins** to MovieSum keys and manual `data/scripts/a24/` drops. **Zero** script staging text. |
| **Wired in repo** | `scripts/scrape_a24_metadata.py` (GitHub default; Kaggle CLI if creds) → `a24_titles.json` + CSV; `ingest_a24_metadata.py` CSV-only shorthand |

### Kaggle overlap (newer / richer metadata than AlexPMorton snapshot)

| Kaggle slug | Extra fields vs AlexPMorton | Use |
|-------------|----------------------------|-----|
| `sebastiansuliborski/a24-studio-movies-dataset` | `Written by`, `Screenplay by`, starring, cinematography, IMDb/RT scores | Preferred when you need **writer credits**; ~66 KB |
| `dvdlws/a24-movie-database` | Letterboxd / popcornmeter | CC BY-SA 4.0; ratings-focused |
| `alsyab/a24-films` | Catalog through **2026** from a24films.com | CC BY-NC-SA 4.0; good for **upcoming** title slugs |

Download locally:

```bash
# Example — requires Kaggle CLI auth on your machine
kaggle datasets download -d sebastiansuliborski/a24-studio-movies-dataset -f a24_data_cleaned.csv
python3 scripts/ingest_a24_metadata.py --source local --input a24_data_cleaned.csv \
  --input-label kaggle/sebastiansuliborski -o data/ingest/a24_titles.csv
```

---

## IMSDB / screenplay / dialogue (substitutes)

| Kind | Kaggle examples | Welles pipeline note |
|------|-------------------|----------------------|
| Full scripts | gufukuro, veeralakrishna, prasad22, pratik2kcn | Manual download; **do not commit** full scripts; excerpt policy in `ingest_cinema.py` |
| Tokenized blocks | raghavnimbalkar10 | MIT tokens; upstream Movie-Script-Database / 9 web sources |
| Dialogue only | Cornell mirrors, MCU dialogue | Skip for v1 SFT |
| Plots / summaries | jrobischon, gabrieltardochi | **Preferred** for repo-backed ingest |

---

## Hugging Face cross-links (not Kaggle but cited on Kaggle pages)

| HF dataset | Kaggle / upstream pointer |
|------------|---------------------------|
| `vishnupriyavr/wiki-movie-plots-with-summaries` | jrobischon Wikipedia Movie Plots |
| `raghavnimbalkar/movie-screenplays-tokenized-dataset` | raghavnimbalkar10 Kaggle |
| `rohitsaxena/MovieSum` | (not on Kaggle in survey) — wired in `scripts/ingest_cinema.py` |

---

## Recommended next steps (ingest code)

1. Keep **HF wiki plots** as default cinema path (`data/ingest/README.md`).
2. Optional Kaggle CLI download of `jrobischon/wikipedia-movie-plots` for offline boxes without HF.
3. Script-tier: add **title filter** module using IMDb Kaggle crew/basics + Welles/A24 title lists — still **no verbatim script commit**.
4. Run `scripts/ingest_a24_metadata.py` (GitHub AlexPMorton default or Kaggle `--source local`) → committed `data/ingest/a24_titles.csv` (metadata only).

---

## Search queries used

- `site:kaggle.com Orson Welles screenplay script`
- `site:kaggle.com A24 screenplay script movie`
- `site:kaggle.com movie screenplay IMSDB dataset`
- `site:kaggle.com film dialogue screenplay corpus NLP`
- `site:kaggle.com jrobischon wikipedia movie plots`
- `site:kaggle.com komalkhetlani internet movie script`