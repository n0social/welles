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
};

export default function DocumentEditor({ html, editable = true, onChange, writing }: Props) {
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

  if (!editor) return <div className={styles.sheet} />;

  return (
    <div className={styles.wrap}>
      <div className={styles.toolbar} role="toolbar" aria-label="Format">
        <button
          type="button"
          className={editor.isActive("bold") ? styles.toolOn : styles.tool}
          onClick={() => editor.chain().focus().toggleBold().run()}
          disabled={writing}
        >
          Bold
        </button>
        <button
          type="button"
          className={editor.isActive("italic") ? styles.toolOn : styles.tool}
          onClick={() => editor.chain().focus().toggleItalic().run()}
          disabled={writing}
        >
          Italic
        </button>
        <button
          type="button"
          className={editor.isActive("highlight") ? styles.toolOn : styles.tool}
          onClick={() => editor.chain().focus().toggleHighlight().run()}
          disabled={writing}
        >
          Highlight
        </button>
        <button
          type="button"
          className={styles.tool}
          onClick={() => editor.chain().focus().unsetAllMarks().run()}
          disabled={writing}
        >
          Clear marks
        </button>
      </div>
      <div className={`${styles.sheet} ${writing ? styles.writing : ""}`}>
        <EditorContent editor={editor} />
        {writing ? <p className={styles.live}>Welles is on the page…</p> : null}
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
