"use client";

import { FormEvent, startTransition, useEffect, useState } from "react";
import styles from "./page.module.css";

type Mode = "Write" | "Rewrite" | "Continue";

const STORAGE_KEY = "welles_colab_api_url";

export default function HomePage() {
  const [apiUrl, setApiUrl] = useState("");
  const [mode, setMode] = useState<Mode>("Write");
  const [prompt, setPrompt] = useState("");
  const [maxTokens, setMaxTokens] = useState(768);
  const [output, setOutput] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const saved = window.localStorage.getItem(STORAGE_KEY);
    if (saved) setApiUrl(saved);
  }, []);

  function saveApiUrl(value: string) {
    setApiUrl(value);
    window.localStorage.setItem(STORAGE_KEY, value.trim());
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    setOutput("");

    const endpoint = apiUrl.trim();
    if (!endpoint) {
      setLoading(false);
      setError("Paste your Colab API URL first (from welles_serve.ipynb / ngrok).");
      return;
    }

    try {
      window.localStorage.setItem(STORAGE_KEY, endpoint);
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          apiUrl: endpoint,
          mode,
          prompt,
          maxNewTokens: maxTokens,
        }),
      });
      const data = (await res.json()) as { text?: string; error?: string };
      if (!res.ok) {
        throw new Error(data.error || `Request failed (${res.status})`);
      }
      startTransition(() => {
        setOutput(data.text || "");
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className={styles.stage}>
      <header className={styles.brand}>
        <p className={styles.mark}>Welles</p>
        <h1 className={styles.line}>Write in the tone of Orson Welles.</h1>
        <p className={styles.sub}>Personal demo — start Colab, paste the link, write.</p>
      </header>

      <form className={styles.desk} onSubmit={onSubmit}>
        <label className={styles.label} htmlFor="apiUrl">
          Colab API URL
        </label>
        <input
          id="apiUrl"
          className={styles.url}
          type="url"
          value={apiUrl}
          onChange={(e) => saveApiUrl(e.target.value)}
          placeholder="https://….ngrok-free.app"
          required
        />
        <p className={styles.hint}>
          Run <code>notebooks/welles_serve.ipynb</code> on a T4, copy the printed URL, paste here.
          Leave Colab open.
        </p>

        <div className={styles.modes} role="radiogroup" aria-label="Mode">
          {(["Write", "Rewrite", "Continue"] as Mode[]).map((m) => (
            <button
              key={m}
              type="button"
              className={mode === m ? styles.modeOn : styles.mode}
              aria-pressed={mode === m}
              onClick={() => setMode(m)}
            >
              {m}
            </button>
          ))}
        </div>

        <label className={styles.label} htmlFor="prompt">
          Brief or draft
        </label>
        <textarea
          id="prompt"
          className={styles.input}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          rows={12}
          placeholder="What should Welles write?"
          required
        />

        <div className={styles.row}>
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
            onChange={(e) => setMaxTokens(Number(e.target.value))}
          />
        </div>

        <button className={styles.submit} type="submit" disabled={loading}>
          {loading ? "On the air…" : "Generate"}
        </button>

        {error ? <p className={styles.error}>{error}</p> : null}
      </form>

      <section className={styles.out} aria-live="polite">
        <h2 className={styles.outLabel}>Output</h2>
        <div className={styles.script}>
          {output || (loading ? "Waiting on Colab GPU…" : "—")}
        </div>
      </section>
    </main>
  );
}
