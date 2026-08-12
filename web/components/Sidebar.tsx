"use client";

import { TOKEN_PRESETS, type TokenPresetId } from "@/lib/types";
import styles from "./Sidebar.module.css";

type Props = {
  manuscriptName: string;
  onManuscriptName: (name: string) => void;
  onManuscriptNameCommit: () => void;
  ideaPrompt: string;
  onIdeaPrompt: (v: string) => void;
  rewritePassage: string;
  onRewritePassage: (v: string) => void;
  tokenPreset: TokenPresetId;
  onTokenPreset: (id: TokenPresetId) => void;
  loading: boolean;
  error: string;
  onWrite: () => void;
  onRewrite: () => void;
  onOpenSettings: () => void;
};

export default function Sidebar({
  manuscriptName,
  onManuscriptName,
  onManuscriptNameCommit,
  ideaPrompt,
  onIdeaPrompt,
  rewritePassage,
  onRewritePassage,
  tokenPreset,
  onTokenPreset,
  loading,
  error,
  onWrite,
  onRewrite,
  onOpenSettings,
}: Props) {
  return (
    <aside className={styles.side}>
      <div className={styles.topBlock}>
        <div className={styles.brand}>
          <p className={styles.mark}>Welles</p>
          <p className={styles.tag}>Oratorical. Cinematic. Measured.</p>
          <label className={styles.srOnly} htmlFor="manuscript-title">
            Manuscript title
          </label>
          <input
            id="manuscript-title"
            className={styles.msInput}
            value={manuscriptName}
            onChange={(e) => onManuscriptName(e.target.value)}
            onBlur={onManuscriptNameCommit}
            placeholder="Untitled manuscript"
          />
        </div>

        <label className={styles.label} htmlFor="idea">
          Prompt
        </label>
        <p className={styles.hint}>
          New pages or paragraphs from an idea — what should follow the theme.
        </p>
        <textarea
          id="idea"
          className={styles.area}
          rows={4}
          value={ideaPrompt}
          onChange={(e) => onIdeaPrompt(e.target.value)}
          placeholder="I’m thinking of a paragraph that follows this section — write one that continues the theme…"
        />
        <button className={styles.go} type="button" onClick={onWrite} disabled={loading}>
          {loading ? "On the air…" : "Write onto page"}
        </button>

        <label className={styles.label} htmlFor="rewrite">
          Rewrite
        </label>
        <p className={styles.hint}>
          Paste a sentence or paragraph. Welles restages it a different way.
        </p>
        <textarea
          id="rewrite"
          className={styles.area}
          rows={4}
          value={rewritePassage}
          onChange={(e) => onRewritePassage(e.target.value)}
          placeholder="Paste the line or paragraph to rewrite…"
        />
        <button className={styles.goAlt} type="button" onClick={onRewrite} disabled={loading}>
          {loading ? "On the air…" : "Rewrite onto page"}
        </button>

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
        <p className={styles.hint}>{TOKEN_PRESETS.find((p) => p.id === tokenPreset)?.hint}</p>

        {error ? <p className={styles.error}>{error}</p> : null}
      </div>

      <button type="button" className={styles.settings} onClick={onOpenSettings}>
        Settings
      </button>
    </aside>
  );
}
