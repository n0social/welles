import { newPage, type Page, type ViewMode } from "./types";

const PAGES_KEY = "welles_pages_v1";
const ACTIVE_KEY = "welles_active_page_v1";
const VIEW_KEY = "welles_view_v1";
const API_KEY = "welles_colab_api_url";

export function loadApiUrl(): string {
  if (typeof window === "undefined") return "";
  return window.localStorage.getItem(API_KEY) || "";
}

export function saveApiUrl(url: string) {
  window.localStorage.setItem(API_KEY, url.trim());
}

export function loadPages(): Page[] {
  if (typeof window === "undefined") return [newPage({ title: "Page 1" })];
  try {
    const raw = window.localStorage.getItem(PAGES_KEY);
    if (!raw) return [newPage({ title: "Page 1" })];
    const parsed = JSON.parse(raw) as Page[];
    return Array.isArray(parsed) && parsed.length ? parsed : [newPage({ title: "Page 1" })];
  } catch {
    return [newPage({ title: "Page 1" })];
  }
}

export function savePages(pages: Page[]) {
  window.localStorage.setItem(PAGES_KEY, JSON.stringify(pages));
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

export function loadView(): ViewMode {
  if (typeof window === "undefined") return "single";
  return window.localStorage.getItem(VIEW_KEY) === "pages" ? "pages" : "single";
}

export function saveView(view: ViewMode) {
  window.localStorage.setItem(VIEW_KEY, view);
}
