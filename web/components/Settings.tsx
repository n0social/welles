"use client";

import type { DocumentMeta } from "@/lib/types";
import { useRef } from "react";
import styles from "./Settings.module.css";

type Props = {
  open: boolean;
  onClose: () => void;
  apiUrl: string;
  onApiUrl: (v: string) => void;
  documents: DocumentMeta[];
  activeDocId: string;
  onSelectDoc: (id: string) => void;
  onUploadFiles: (files: FileList) => void;
  onOpenHowItWorks: () => void;
};

export default function Settings({
  open,
  onClose,
  apiUrl,
  onApiUrl,
  documents,
  activeDocId,
  onSelectDoc,
  onUploadFiles,
  onOpenHowItWorks,
}: Props) {
  const fileRef = useRef<HTMLInputElement>(null);
  if (!open) return null;

  return (
    <div className={styles.backdrop} role="dialog" aria-labelledby="settings-title">
      <div className={styles.sheet}>
        <div className={styles.head}>
          <h2 id="settings-title">Settings</h2>
          <button type="button" className={styles.close} onClick={onClose}>
            Close
          </button>
        </div>

        <label className={styles.label} htmlFor="settings-api">
          Colab API URL
        </label>
        <input
          id="settings-api"
          className={styles.input}
          type="url"
          value={apiUrl}
          onChange={(e) => onApiUrl(e.target.value)}
          placeholder="https://….ngrok-free.app"
        />
        <p className={styles.hint}>From welles_serve.ipynb after ngrok starts. Keep Colab open.</p>

        <button type="button" className={styles.linkBtn} onClick={onOpenHowItWorks}>
          How it works
        </button>

        <label className={styles.label} htmlFor="uploads">
          Upload manuscripts
        </label>
        <input
          id="uploads"
          ref={fileRef}
          className={styles.file}
          type="file"
          accept=".txt,.md,.markdown,text/plain,text/markdown"
          multiple
          onChange={(e) => {
            if (e.target.files?.length) onUploadFiles(e.target.files);
            e.target.value = "";
          }}
        />
        <p className={styles.hint}>
          Multi-select .txt / .md. Chapters from # headings or “Chapter N”. Split into
          pages automatically.
        </p>

        {documents.length ? (
          <>
            <p className={styles.label}>Manuscripts</p>
            <ul className={styles.docs}>
              {documents.map((d) => (
                <li key={d.id}>
                  <button
                    type="button"
                    className={d.id === activeDocId ? styles.docOn : styles.doc}
                    onClick={() => onSelectDoc(d.id)}
                  >
                    {d.name}
                  </button>
                </li>
              ))}
            </ul>
          </>
        ) : null}
      </div>
    </div>
  );
}
