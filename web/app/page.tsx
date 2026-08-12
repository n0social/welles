"use client";

import DocumentEditor, { appendPlainAsHtml } from "@/components/DocumentEditor";
import HowItWorksPanel from "@/components/HowItWorks";
import PageGrid from "@/components/PageGrid";
import Settings from "@/components/Settings";
import Sidebar from "@/components/Sidebar";
import {
  documentsFromPages,
  loadActiveDocId,
  loadActiveId,
  loadApiUrl,
  loadPages,
  loadView,
  saveActiveDocId,
  saveActiveId,
  saveApiUrl,
  savePages,
  saveView,
} from "@/lib/storage";
import {
  TOKEN_PRESETS,
  newBlankPage,
  pagesFromManuscript,
  type Mode,
  type Page,
  type TokenPresetId,
  type ViewMode,
} from "@/lib/types";
import { startTransition, useEffect, useMemo, useState } from "react";
import styles from "./page.module.css";

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

export default function HomePage() {
  const [ready, setReady] = useState(false);
  const [pages, setPages] = useState<Page[]>([newBlankPage()]);
  const [activeId, setActiveId] = useState("");
  const [activeDocId, setActiveDocId] = useState("");
  const [view, setView] = useState<ViewMode>("single");
  const [apiUrl, setApiUrl] = useState("");
  const [mode, setMode] = useState<Mode>("Write");
  const [prompt, setPrompt] = useState("");
  const [tokenPreset, setTokenPreset] = useState<TokenPresetId>("novelist");
  const [loading, setLoading] = useState(false);
  const [writing, setWriting] = useState(false);
  const [error, setError] = useState("");
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [howOpen, setHowOpen] = useState(false);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    const loaded = loadPages();
    setPages(loaded);
    setActiveId(loadActiveId(loaded));
    setActiveDocId(loadActiveDocId(loaded));
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
    if (!ready || !activeDocId) return;
    saveActiveDocId(activeDocId);
  }, [activeDocId, ready]);

  useEffect(() => {
    if (!ready) return;
    saveView(view);
  }, [view, ready]);

  const documents = useMemo(() => documentsFromPages(pages), [pages]);

  const docPages = useMemo(
    () => pages.filter((p) => p.documentId === activeDocId),
    [pages, activeDocId],
  );

  const activePage = useMemo(() => {
    const inDoc = docPages.find((p) => p.id === activeId);
    return inDoc || docPages[0] || pages[0];
  }, [docPages, activeId, pages]);

  function updateActive(patch: Partial<Page>) {
    if (!activePage) return;
    setPages((prev) => prev.map((p) => (p.id === activePage.id ? { ...p, ...patch } : p)));
  }

  function addPage() {
    if (!activePage) return;
    const siblings = pages.filter(
      (p) =>
        p.documentId === activePage.documentId && p.chapterIndex === activePage.chapterIndex,
    );
    const page = newBlankPage({
      documentId: activePage.documentId,
      documentName: activePage.documentName,
    });
    page.chapterIndex = activePage.chapterIndex;
    page.chapterTitle = activePage.chapterTitle;
    page.pageInChapter = siblings.length + 1;
    setPages((prev) => [...prev, page]);
    setActiveId(page.id);
    setView("single");
  }

  function selectPage(id: string) {
    const page = pages.find((p) => p.id === id);
    if (page) setActiveDocId(page.documentId);
    setActiveId(id);
    setView("single");
  }

  function selectDoc(id: string) {
    setActiveDocId(id);
    const first = pages.find((p) => p.documentId === id);
    if (first) setActiveId(first.id);
    setSettingsOpen(false);
    setView("pages");
  }

  async function onUploadFiles(files: FileList) {
    const incoming: Page[] = [];
    for (const file of Array.from(files)) {
      const text = await file.text();
      incoming.push(...pagesFromManuscript(file.name, text));
    }
    if (!incoming.length) return;
    setPages((prev) => [...prev, ...incoming]);
    setActiveDocId(incoming[0].documentId);
    setActiveId(incoming[0].id);
    setSettingsOpen(false);
    setView("pages");
  }

  async function typeOntoPage(fullText: string) {
    if (!activePage) return;
    setWriting(true);
    const startHtml = activePage.html;
    const pageId = activePage.id;
    let built = "";
    const tokens = fullText.split(/(\s+)/);
    for (const token of tokens) {
      built += token;
      const html = appendPlainAsHtml(startHtml, built);
      startTransition(() => {
        setPages((prev) => prev.map((p) => (p.id === pageId ? { ...p, html } : p)));
      });
      await sleep(token.trim() ? 22 : 8);
    }
    setWriting(false);
  }

  async function onGenerate() {
    setError("");
    const endpoint = apiUrl.trim();
    if (!endpoint) {
      setError("Open Settings and paste your Colab API URL.");
      setSettingsOpen(true);
      return;
    }
    if (!prompt.trim()) {
      setError("Give Welles a brief.");
      return;
    }

    saveApiUrl(endpoint);
    setLoading(true);
    const maxNewTokens =
      TOKEN_PRESETS.find((p) => p.id === tokenPreset)?.tokens ?? 896;
    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          apiUrl: endpoint,
          mode,
          prompt,
          maxNewTokens,
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
        mode={mode}
        onMode={setMode}
        prompt={prompt}
        onPrompt={setPrompt}
        tokenPreset={tokenPreset}
        onTokenPreset={setTokenPreset}
        loading={loading || writing}
        error={error}
        onGenerate={onGenerate}
        onAddPage={addPage}
        onOpenSettings={() => setSettingsOpen(true)}
        manuscriptName={activePage.documentName}
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
              onClick={() => {
                setExpanded(false);
                setView("pages");
              }}
            >
              All pages
            </button>
          </div>
        </header>

        <div className={styles.stage}>
          {view === "single" ? (
            <DocumentEditor
              html={activePage.html}
              onChange={(html) => updateActive({ html })}
              writing={writing || loading}
              expanded={expanded}
              onToggleExpand={() => setExpanded((v) => !v)}
            />
          ) : (
            <PageGrid
              pages={docPages}
              activeId={activePage.id}
              onSelect={selectPage}
              onAdd={addPage}
            />
          )}
        </div>
      </section>

      <Settings
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        apiUrl={apiUrl}
        onApiUrl={(v) => {
          setApiUrl(v);
          saveApiUrl(v);
        }}
        documents={documents}
        activeDocId={activeDocId}
        onSelectDoc={selectDoc}
        onUploadFiles={onUploadFiles}
        onOpenHowItWorks={() => {
          setSettingsOpen(false);
          setHowOpen(true);
        }}
      />

      {howOpen ? <HowItWorksPanel onClose={() => setHowOpen(false)} /> : null}
    </div>
  );
}
