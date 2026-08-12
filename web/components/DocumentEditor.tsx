"use client";

import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Highlight from "@tiptap/extension-highlight";
import Placeholder from "@tiptap/extension-placeholder";
import { useEffect } from "react";
import styles from "./DocumentEditor.module.css";

type Props = {
  html: string;
  editable?: boolean;
  onChange: (html: string) => void;
  writing?: boolean;
  expanded?: boolean;
  onToggleExpand?: () => void;
  onAddPage?: () => void;
};

export default function DocumentEditor({
  html,
  editable = true,
  onChange,
  writing,
  expanded,
  onToggleExpand,
  onAddPage,
}: Props) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Highlight.configure({ multicolor: false }),
      Placeholder.configure({
        placeholder: "The page is blank. Ask Welles — or begin.",
      }),
    ],
    content: html,
    editable,
    immediatelyRender: false,
    onUpdate: ({ editor: ed }) => {
      onChange(ed.getHTML());
    },
    editorProps: {
      attributes: {
        class: styles.prose,
        spellcheck: "true",
      },
    },
  });

  useEffect(() => {
    if (!editor) return;
    const current = editor.getHTML();
    if (html !== current) {
      editor.commands.setContent(html, false);
    }
  }, [html, editor]);

  useEffect(() => {
    if (!editor) return;
    editor.setEditable(editable && !writing);
  }, [editable, writing, editor]);

  useEffect(() => {
    if (!expanded || !onToggleExpand) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onToggleExpand();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [expanded, onToggleExpand]);

  if (!editor) return <div className={styles.sheet} />;

  return (
    <div className={styles.wrap}>
      {!expanded ? (
        <div className={styles.toolbar} role="toolbar" aria-label="Format">
          <button
            type="button"
            title="Bold (Ctrl+B)"
            aria-label="Bold"
            aria-pressed={editor.isActive("bold")}
            className={editor.isActive("bold") ? styles.toolOn : styles.tool}
            onClick={() => editor.chain().focus().toggleBold().run()}
            disabled={writing}
          >
            <b>B</b>
          </button>
          <button
            type="button"
            title="Italic (Ctrl+I)"
            aria-label="Italic"
            aria-pressed={editor.isActive("italic")}
            className={editor.isActive("italic") ? styles.toolOn : styles.tool}
            onClick={() => editor.chain().focus().toggleItalic().run()}
            disabled={writing}
          >
            <i>I</i>
          </button>
          <button
            type="button"
            title="Highlight"
            aria-label="Highlight"
            aria-pressed={editor.isActive("highlight")}
            className={editor.isActive("highlight") ? styles.toolOn : styles.tool}
            onClick={() => editor.chain().focus().toggleHighlight().run()}
            disabled={writing}
          >
            <span className={styles.hi}>H</span>
          </button>
          <button
            type="button"
            title="Clear formatting"
            aria-label="Clear formatting"
            className={styles.tool}
            onClick={() => editor.chain().focus().unsetAllMarks().run()}
            disabled={writing}
          >
            Tx
          </button>
          {onAddPage ? (
            <button
              type="button"
              title="New page"
              aria-label="New page"
              className={styles.toolWide}
              onClick={onAddPage}
              disabled={writing}
            >
              New page
            </button>
          ) : null}
        </div>
      ) : null}

      <div className={`${styles.pageStage} ${expanded ? styles.pageExpanded : ""}`}>
        <div className={`${styles.sheet} ${writing ? styles.writing : ""}`}>
          <EditorContent editor={editor} />
          {writing ? <p className={styles.live}>Welles is on the page…</p> : null}
        </div>

        {onToggleExpand ? (
          <button
            type="button"
            className={styles.expand}
            onClick={onToggleExpand}
            title={expanded ? "Exit expand" : "Expand page"}
          >
            {expanded ? "Close" : "Expand page"}
          </button>
        ) : null}
      </div>
    </div>
  );
}

/** Append plain text into HTML as paragraphs for typewriter sessions. */
export function appendPlainAsHtml(existingHtml: string, plain: string): string {
  const chunks = plain
    .split(/\n{2,}/)
    .map((p) => p.trim())
    .filter(Boolean)
    .map((p) => `<p>${escapeHtml(p).replace(/\n/g, "<br>")}</p>`)
    .join("");
  const base = existingHtml.replace(/<p><\/p>/g, "").trim();
  if (!base || base === "<p></p>") return chunks || "<p></p>";
  return `${base}${chunks}`;
}

function escapeHtml(s: string) {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
