export type ViewMode = "single" | "pages";

export type Mode = "Write" | "Rewrite" | "Continue";

export type Page = {
  id: string;
  title: string;
  html: string;
};

export function newPage(partial?: Partial<Page>): Page {
  const n = Math.floor(Math.random() * 9000) + 1000;
  return {
    id: `page-${Date.now()}-${n}`,
    title: partial?.title || "Untitled page",
    html: partial?.html || "<p></p>",
  };
}

export function plainPreview(html: string, max = 160): string {
  const text = html
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  if (!text) return "Empty page";
  return text.length > max ? `${text.slice(0, max)}…` : text;
}
