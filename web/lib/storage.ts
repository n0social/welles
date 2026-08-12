import { newBlankPage, type DocumentMeta, type Page, type ViewMode } from "./types";

const PAGES_KEY = "welles_pages_v2";
const LEGACY_PAGES_KEY = "welles_pages_v1";
const ACTIVE_KEY = "welles_active_page_v1";
const VIEW_KEY = "welles_view_v1";
const API_KEY = "welles_colab_api_url";
const DOC_KEY = "welles_active_doc_v1";

export function loadApiUrl(): string {
  if (typeof window === "undefined") return "";
  return window.localStorage.getItem(API_KEY) || "";
}

export function saveApiUrl(url: string) {
  window.localStorage.setItem(API_KEY, url.trim());
}

function migrateLegacy(raw: string): Page[] {
  try {
    const parsed = JSON.parse(raw) as Array<{ id?: string; title?: string; html?: string }>;
    if (!Array.isArray(parsed) || !parsed.length) return [newBlankPage()];
    const documentId = `doc-migrated`;
    const documentName = "Untitled manuscript";
    return parsed.map((p, i) => ({
      id: p.id || `page-migrated-${i}`,
      html: p.html || "<p></p>",
      documentId,
      documentName,
      chapterIndex: 1,
      chapterTitle: p.title || "Chapter 1",
      pageInChapter: i + 1,
    }));
  } catch {
    return [newBlankPage()];
  }
}

export function loadPages(): Page[] {
  if (typeof window === "undefined") return [newBlankPage()];
  const v2 = window.localStorage.getItem(PAGES_KEY);
  if (v2) {
    try {
      const parsed = JSON.parse(v2) as Page[];
      if (Array.isArray(parsed) && parsed.length) return parsed;
    } catch {
      /* fall through */
    }
  }
  const legacy = window.localStorage.getItem(LEGACY_PAGES_KEY);
  if (legacy) {
    const migrated = migrateLegacy(legacy);
    savePages(migrated);
    return migrated;
  }
  return [newBlankPage()];
}

export function savePages(pages: Page[]) {
  window.localStorage.setItem(PAGES_KEY, JSON.stringify(pages));
}

export function documentsFromPages(pages: Page[]): DocumentMeta[] {
  const map = new Map<string, string>();
  for (const p of pages) {
    if (!map.has(p.documentId)) map.set(p.documentId, p.documentName);
  }
  return [...map.entries()].map(([id, name]) => ({ id, name }));
}

export function loadActiveId(pages: Page[]): string {
  if (typeof window === "undefined") return pages[0]?.id || "";
  const id = window.localStorage.getItem(ACTIVE_KEY);
  if (id && pages.some((p) => p.id === id)) return id;
  return pages[0]?.id || "";
}

export function saveActiveId(id: string) {
  window.localStorage.setItem(ACTIVE_KEY, id);
}

export function loadActiveDocId(pages: Page[]): string {
  if (typeof window === "undefined") return pages[0]?.documentId || "";
  const id = window.localStorage.getItem(DOC_KEY);
  if (id && pages.some((p) => p.documentId === id)) return id;
  return pages[0]?.documentId || "";
}

export function saveActiveDocId(id: string) {
  window.localStorage.setItem(DOC_KEY, id);
}

export function loadView(): ViewMode {
  if (typeof window === "undefined") return "single";
  return window.localStorage.getItem(VIEW_KEY) === "pages" ? "pages" : "single";
}

export function saveView(view: ViewMode) {
  window.localStorage.setItem(VIEW_KEY, view);
}
