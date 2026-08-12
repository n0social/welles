export type ViewMode = "single" | "pages";

export type Page = {
  id: string;
  html: string;
  documentId: string;
  documentName: string;
  chapterIndex: number;
  chapterTitle: string;
  pageInChapter: number;
};

export type DocumentMeta = {
  id: string;
  name: string;
};

/** Generation length presets (clamped server-side 256–2048). */
export const TOKEN_PRESETS = [
  { id: "light", label: "Light", tokens: 384, hint: "A short beat or paragraph" },
  { id: "novelist", label: "Novelist", tokens: 896, hint: "A scene or page stretch" },
  { id: "robust", label: "Robust", tokens: 1536, hint: "A long chapter push" },
] as const;

export type TokenPresetId = (typeof TOKEN_PRESETS)[number]["id"];

export function newId(prefix: string) {
  const n = Math.floor(Math.random() * 9000) + 1000;
  return `${prefix}-${Date.now()}-${n}`;
}

export function newBlankPage(doc?: Partial<Pick<Page, "documentId" | "documentName">>): Page {
  const documentId = doc?.documentId || newId("doc");
  const documentName = doc?.documentName || "Untitled manuscript";
  return {
    id: newId("page"),
    html: "<p></p>",
    documentId,
    documentName,
    chapterIndex: 1,
    chapterTitle: "Chapter 1",
    pageInChapter: 1,
  };
}

export function firstHeading(html: string): string | null {
  const match = html.match(/<h[1-3][^>]*>(.*?)<\/h[1-3]>/i);
  if (!match) return null;
  const text = match[1].replace(/<[^>]+>/g, "").trim();
  return text || null;
}

/** Card label — Page N of Chapter M only. */
export function pageLabel(page: Page): string {
  return `Page ${page.pageInChapter} of Chapter ${page.chapterIndex}`;
}

/** Short card teaser: start of the first sentence + ellipsis. */
export function cardSnippet(html: string, maxChars = 72): string {
  const text = html
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  if (!text) return "Empty page";

  const sentenceMatch = text.match(/^(.+?[.!?])(\s|$)/);
  let snippet = (sentenceMatch?.[1] || text).trim();
  if (snippet.length > maxChars) {
    snippet = snippet.slice(0, maxChars).replace(/\s+\S*$/, "").trim();
  }
  return snippet.endsWith("...") ? snippet : `${snippet}...`;
}

function escapeHtml(s: string) {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

export function textToHtml(text: string): string {
  const paras = text
    .split(/\n{2,}/)
    .map((p) => p.trim())
    .filter(Boolean)
    .map((p) => `<p>${escapeHtml(p).replace(/\n/g, "<br>")}</p>`);
  return paras.join("") || "<p></p>";
}

const WORDS_PER_PAGE = 380;

function chunkByWords(text: string, maxWords = WORDS_PER_PAGE): string[] {
  const words = text.trim().split(/\s+/).filter(Boolean);
  if (!words.length) return [""];
  const chunks: string[] = [];
  for (let i = 0; i < words.length; i += maxWords) {
    chunks.push(words.slice(i, i + maxWords).join(" "));
  }
  return chunks;
}

type ChapterDraft = { title: string; body: string };

function splitChapters(raw: string, fallbackTitle: string): ChapterDraft[] {
  const text = raw.replace(/\r\n/g, "\n").trim();
  if (!text) return [{ title: fallbackTitle, body: "" }];

  const chapterRe =
    /(?:^|\n)(?:#{1,2}\s+|Chapter\s+\d+[.:)\s-]*|CHAPTER\s+\d+[.:)\s-]*)([^\n]*)\n/g;
  const marks: { index: number; title: string }[] = [];
  let m: RegExpExecArray | null;
  while ((m = chapterRe.exec(text))) {
    marks.push({
      index: m.index + (m[0].startsWith("\n") ? 1 : 0),
      title: (m[1] || "").trim() || `Chapter ${marks.length + 1}`,
    });
  }

  if (!marks.length) {
    return [{ title: fallbackTitle, body: text }];
  }

  const chapters: ChapterDraft[] = [];
  for (let i = 0; i < marks.length; i++) {
    const start = marks[i].index;
    const end = i + 1 < marks.length ? marks[i + 1].index : text.length;
    const block = text.slice(start, end);
    const firstLineEnd = block.indexOf("\n");
    const body = (firstLineEnd === -1 ? "" : block.slice(firstLineEnd + 1)).trim();
    chapters.push({
      title: marks[i].title || `Chapter ${i + 1}`,
      body,
    });
  }
  return chapters;
}

/** Turn one uploaded text file into pages under a document. */
export function pagesFromManuscript(filename: string, raw: string): Page[] {
  const documentId = newId("doc");
  const documentName = filename.replace(/\.(txt|md|markdown)$/i, "") || "Manuscript";
  const chapters = splitChapters(raw, "Chapter 1");
  const pages: Page[] = [];

  chapters.forEach((ch, ci) => {
    const chapterIndex = ci + 1;
    const chapterTitle = ch.title || `Chapter ${chapterIndex}`;
    const pieces = chunkByWords(ch.body);
    pieces.forEach((piece, pi) => {
      const pageInChapter = pi + 1;
      const headingHtml = pi === 0 ? `<h2>${escapeHtml(chapterTitle)}</h2>` : "";
      const bodyHtml = textToHtml(piece);
      pages.push({
        id: newId("page"),
        html: `${headingHtml}${bodyHtml}` || "<p></p>",
        documentId,
        documentName,
        chapterIndex,
        chapterTitle,
        pageInChapter,
      });
    });
  });

  return pages.length ? pages : [newBlankPage({ documentId, documentName })];
}
