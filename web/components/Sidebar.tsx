"use client";

import type { Mode } from "@/lib/types";
import styles from "./Sidebar.module.css";

type Props = {
  apiUrl: string;
  onApiUrl: (v: string) => void;
  mode: Mode;
  onMode: (m: Mode) => void;
  prompt: string;
  onPrompt: (v: string) => void;
  maxTokens: number;
  onMaxTokens: (n: number) => void;
  loading: boolean;
  error: string;
  onGenerate: () => void;
  pageTitle: string;
  onPageTitle: (v: string) => void;
  onAddPage: () => void;
};

export default function Sidebar({
  apiUrl,
  onApiUrl,
  mode,
  onMode,
  prompt,
  onPrompt,
  maxTokens,
  onMaxTokens,
  loading,
  error,
  onGenerate,
  pageTitle,
  onPageTitle,
  onAddPage,
}: Props) {
  return (
    <aside className={styles.side}>
      <div className={styles.brand}>
        <p className={styles.mark}>Welles</p>
        <p className={styles.tag}>Oratorical. Cinematic. Deliberate.</p>
      </div>

      <label className={styles.label} htmlFor="apiUrl">
        Colab API URL
      </label>
      <input
        id="apiUrl"
        className={styles.input}
        type="url"
        value={apiUrl}
        onChange={(e) => onApiUrl(e.target.value)}
        placeholder="https://….ngrok-free.app"
      />

      <label className={styles.label} htmlFor="pageTitle">
        Page title
      </label>
      <input
        id="pageTitle"
        className={styles.input}
        value={pageTitle}
        onChange={(e) => onPageTitle(e.target.value)}
      />

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
