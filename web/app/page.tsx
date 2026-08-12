"use client";

import DocumentEditor, { appendPlainAsHtml } from "@/components/DocumentEditor";
import PageGrid from "@/components/PageGrid";
import Sidebar from "@/components/Sidebar";
import {
  loadActiveId,
  loadApiUrl,
  loadPages,
  loadView,
  saveActiveId,
  saveApiUrl,
  savePages,
  saveView,
} from "@/lib/storage";
import { newPage, type Mode, type Page, type ViewMode } from "@/lib/types";
import { startTransition, useEffect, useMemo, useState } from "react";
import styles from "./page.module.css";

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

export default function HomePage() {
  const [ready, setReady] = useState(false);
  const [pages, setPages] = useState<Page[]>([newPage({ title: "Page 1" })]);
  const [activeId, setActiveId] = useState("");
  const [view, setView] = useState<ViewMode>("single");
  const [apiUrl, setApiUrl] = useState("");
  const [mode, setMode] = useState<Mode>("Write");
  const [prompt, setPrompt] = useState("");
  const [maxTokens, setMaxTokens] = useState(768);
  const [loading, setLoading] = useState(false);
  const [writing, setWriting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const loaded = loadPages();
    setPages(loaded);
    setActiveId(loadActiveId(loaded));
    setView(loadView());
    setApiUrl(loadApiUrl());
    setReady(true);
  }, []);

  useEffect(() => {
    if (!ready) return;
    savePages(pages);
  }, [pages, ready]);

  useEffect(() => {
    if (!ready || !activeId) return;
    saveActiveId(activeId);
  }, [activeId, ready]);

  useEffect(() => {
    if (!ready) return;
    saveView(view);
  }, [view, ready]);

  const activePage = useMemo(
    () => pages.find((p) => p.id === activeId) || pages[0],
    [pages, activeId],
  );

  function updateActive(patch: Partial<Page>) {
    if (!activePage) return;
    setPages((prev) => prev.map((p) => (p.id === activePage.id ? { ...p, ...patch } : p)));
  }

  function addPage() {
    const page = newPage({ title: `Page ${pages.length + 1}` });
    setPages((prev) => [...prev, page]);
    setActiveId(page.id);
    setView("single");
  }

  function selectPage(id: string) {
    setActiveId(id);
    setView("single");
  }

  async function typeOntoPage(fullText: string) {
    if (!activePage) return;
    setWriting(true);
    const startHtml = activePage.html;
    let built = "";
    const tokens = fullText.split(/(\s+)/);
    for (const token of tokens) {
      built += token;
      const html = appendPlainAsHtml(startHtml, built);
      startTransition(() => {
        setPages((prev) =>
          prev.map((p) => (p.id === activePage.id ? { ...p, html } : p)),
        );
      });
      await sleep(token.trim() ? 22 : 8);
    }
    setWriting(false);
  }

  async function onGenerate() {
    setError("");
    const endpoint = apiUrl.trim();
    if (!endpoint) {
      setError("Paste your Colab API URL first.");
      return;
    }
    if (!prompt.trim()) {
      setError("Give Welles a brief.");
      return;
    }

    saveApiUrl(endpoint);
    setLoading(true);
    try {
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
      if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
      setLoading(false);
      setView("single");
      await typeOntoPage((data.text || "").trim());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      setLoading(false);
      setWriting(false);
    }
  }

  if (!ready || !activePage) {
    return <div className={styles.boot}>Opening the desk…</div>;
  }

  return (
    <div className={styles.app}>
      <Sidebar
        apiUrl={apiUrl}
        onApiUrl={(v) => {
          setApiUrl(v);
          saveApiUrl(v);
        }}
        mode={mode}
        onMode={setMode}
        prompt={prompt}
        onPrompt={setPrompt}
        maxTokens={maxTokens}
        onMaxTokens={setMaxTokens}
        loading={loading || writing}
        error={error}
        onGenerate={onGenerate}
        pageTitle={activePage.title}
        onPageTitle={(title) => updateActive({ title })}
        onAddPage={addPage}
      />

      <section className={styles.workspace}>
        <header className={styles.top}>
          <div className={styles.views} role="tablist" aria-label="View">
            <button
              type="button"
              role="tab"
              aria-selected={view === "single"}
              className={view === "single" ? styles.tabOn : styles.tab}
              onClick={() => setView("single")}
            >
              Single page
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={view === "pages"}
              className={view === "pages" ? styles.tabOn : styles.tab}
              onClick={() => setView("pages")}
            >
              All pages
            </button>
          </div>
          <p className={styles.crumb}>
            {view === "single"
              ? activePage.title
              : `${pages.length} page${pages.length === 1 ? "" : "s"}`}
          </p>
        </header>

        <div className={styles.stage}>
          {view === "single" ? (
            <DocumentEditor
              html={activePage.html}
              onChange={(html) => updateActive({ html })}
              writing={writing || loading}
            />
          ) : (
            <PageGrid
              pages={pages}
              activeId={activePage.id}
              onSelect={selectPage}
              onAdd={addPage}
            />
          )}
        </div>
      </section>
    </div>
  );
}
