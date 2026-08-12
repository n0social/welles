"use client";

import type { Mode } from "@/lib/types";
import styles from "./Sidebar.module.css";

type Props = {
  mode: Mode;
  onMode: (m: Mode) => void;
  prompt: string;
  onPrompt: (v: string) => void;
  maxTokens: number;
  onMaxTokens: (n: number) => void;
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
  maxTokens,
  onMaxTokens,
  loading,
  error,
  onGenerate,
  onAddPage,
  onOpenSettings,
  manuscriptName,
}: Props) {
  return (
    <aside className={styles.side}>
      <div className={styles.brand}>
        <p className={styles.mark}>Welles</p>
        <p className={styles.tag}>Oratorical. Cinematic. Measured.</p>
        <p className={styles.ms}>{manuscriptName}</p>
      </div>

      <button type="button" className={styles.ghost} onClick={onOpenSettings}>
        Settings
      </button>

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
        Brief for Welles
      </label>
      <textarea
        id="prompt"
        className={styles.area}
        rows={8}
        value={prompt}
        onChange={(e) => onPrompt(e.target.value)}
        placeholder="What should land on this page?"
      />

      <label className={styles.label} htmlFor="tokens">
        Max tokens: {maxTokens}
      </label>
      <input
        id="tokens"
        className={styles.slider}
        type="range"
        min={256}
        max={2048}
        step={128}
        value={maxTokens}
        onChange={(e) => onMaxTokens(Number(e.target.value))}
      />

      <button className={styles.go} type="button" onClick={onGenerate} disabled={loading}>
        {loading ? "On the air…" : "Generate onto page"}
      </button>
      <button className={styles.ghost} type="button" onClick={onAddPage}>
        New page
      </button>

      {error ? <p className={styles.error}>{error}</p> : null}
    </aside>
  );
}
