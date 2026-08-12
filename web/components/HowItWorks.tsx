"use client";

import styles from "./HowItWorks.module.css";

export default function HowItWorksPanel({ onClose }: { onClose: () => void }) {
  return (
    <div className={styles.panel} role="dialog" aria-labelledby="how-title">
      <div className={styles.body}>
        <div className={styles.head}>
          <h2 id="how-title">How it works</h2>
          <button type="button" className={styles.close} onClick={onClose}>
            Close
          </button>
        </div>
        <p>
          Welles is a writing desk in the browser. The UI lives on Vercel. The model
          runs on a GPU you start yourself (free Colab). You paste that GPU link into
          Settings.
        </p>

        <h3>1. Model on Hugging Face</h3>
        <p>
          The adapter is already on the Hub:{" "}
          <a href="https://huggingface.co/n0social/welles" target="_blank" rel="noreferrer">
            n0social/welles
          </a>
          . It sits on top of <code>Qwen/Qwen3-8B</code>. You do not download weights by
          hand for normal use — Colab pulls them.
        </p>

        <h3>2. Start Colab (GPU API)</h3>
        <ol>
          <li>
            Open{" "}
            <a href="https://colab.research.google.com/" target="_blank" rel="noreferrer">
              Google Colab
            </a>
            .
          </li>
          <li>
            Runtime → Change runtime type → <strong>T4 GPU</strong>.
          </li>
          <li>
            Upload / open <code>notebooks/welles_serve.ipynb</code> from the{" "}
            <a href="https://github.com/n0social/welles" target="_blank" rel="noreferrer">
              GitHub repo
            </a>
            .
          </li>
          <li>Run the cells. Install packages, load the model, start the API.</li>
          <li>
            When asked, paste a free{" "}
            <a
              href="https://dashboard.ngrok.com/get-started/your-authtoken"
              target="_blank"
              rel="noreferrer"
            >
              ngrok authtoken
            </a>{" "}
            so the internet (Vercel) can reach your Colab.
          </li>
          <li>
            Copy the printed URL, like <code>https://….ngrok-free.app</code>.
          </li>
        </ol>

        <h3>3. Paste the link here</h3>
        <p>
          Settings → <strong>Colab API URL</strong> → paste. Leave the Colab tab open
          while you write. If Colab disconnects, run the notebook again and paste the
          new URL.
        </p>

        <h3>4. Write</h3>
        <p>
          Upload manuscripts in Settings (multi-file). Chapters are detected from{" "}
          <code>#</code> / <code>##</code> headings or lines like <code>Chapter 1</code>.
          Long chapters split into pages. The desk shows{" "}
          <strong>Page # of Chapter #</strong> (plus a heading when the page has one).
          Generate from the sidebar; Welles types onto the open page.
        </p>

        <h3>Why not all on Vercel?</h3>
        <p>
          An 8B model needs a GPU. Vercel hosts the desk only. Colab is the engine for
          this free personal setup.
        </p>
      </div>
    </div>
  );
}
