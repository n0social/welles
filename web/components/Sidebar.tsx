"use client";

import { MODE_BRIEF, TOKEN_PRESETS, type Mode, type TokenPresetId } from "@/lib/types";
import styles from "./Sidebar.module.css";

type Props = {
  mode: Mode;
  onMode: (m: Mode) => void;
  prompt: string;
  onPrompt: (v: string) => void;
  tokenPreset: TokenPresetId;
  onTokenPreset: (id: TokenPresetId) => void;
  loading: boolean;
  error: string;
  onGenerate: () => void;
  onAddPage: () => void;
  onOpenSettings: () => void;
  manuscriptName: string;
};

export default function Sidebar({
  mode,
  onMode,
  prompt,
  onPrompt,
  tokenPreset,
  onTokenPreset,
  loading,
  error,
  onGenerate,
  onAddPage,
  onOpenSettings,
  manuscriptName,
}: Props) {
  const brief = MODE_BRIEF[mode];

  return (
    <aside className={styles.side}>
      <div className={styles.topBlock}>
        <div className={styles.brand}>
          <p className={styles.mark}>Welles</p>
          <p className={styles.tag}>Oratorical. Cinematic. Measured.</p>
          <p className={styles.ms}>{manuscriptName}</p>
        </div>

        <div className={styles.modes} role="radiogroup" aria-label="Mode">
          {(["Write", "Rewrite", "Continue"] as Mode[]).map((m) => (
            <button
              key={m}
              type="button"
              className={mode === m ? styles.modeOn : styles.mode}
              aria-pressed={mode === m}
              onClick={() => onMode(m)}
            >
              {m}
            </button>
          ))}
        </div>

        <label className={styles.label} htmlFor="prompt">
          {brief.label}
        </label>
        <p className={styles.hint}>{brief.hint}</p>
        <textarea
          id="prompt"
          className={styles.area}
          rows={5}
          value={prompt}
          onChange={(e) => onPrompt(e.target.value)}
          placeholder={brief.placeholder}
        />

        <p className={styles.label}>Length</p>
        <div className={styles.presets} role="radiogroup" aria-label="Length">
          {TOKEN_PRESETS.map((p) => (
            <button
              key={p.id}
              type="button"
              className={tokenPreset === p.id ? styles.presetOn : styles.preset}
              aria-pressed={tokenPreset === p.id}
              title={p.hint}
              onClick={() => onTokenPreset(p.id)}
            >
              {p.label}
            </button>
          ))}
        </div>
        <p className={styles.hint}>
          {TOKEN_PRESETS.find((p) => p.id === tokenPreset)?.hint}
        </p>

        <button className={styles.go} type="button" onClick={onGenerate} disabled={loading}>
          {loading ? "On the air…" : "Generate onto page"}
        </button>
        <button className={styles.ghost} type="button" onClick={onAddPage}>
          New page
        </button>

        {error ? <p className={styles.error}>{error}</p> : null}
      </div>

      <button type="button" className={styles.settings} onClick={onOpenSettings}>
        Settings
      </button>
    </aside>
  );
}
