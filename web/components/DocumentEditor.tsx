"use client";

import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Highlight from "@tiptap/extension-highlight";
import Placeholder from "@tiptap/extension-placeholder";
import { useEffect, useState } from "react";
import styles from "./DocumentEditor.module.css";

type RewriteBubble = {
  top: number;
  left: number;
  text: string;
};

type Props = {
  html: string;
  editable?: boolean;
  onChange: (html: string) => void;
  writing?: boolean;
  expanded?: boolean;
  onToggleExpand?: () => void;
  onAddPage?: () => void;
  onRewriteSelection?: (text: string) => void;
};

export default function DocumentEditor({
  html,
  editable = true,
  onChange,
  writing,
  expanded,
  onToggleExpand,
  onAddPage,
  onRewriteSelection,
}: Props) {
  const [rewriteBubble, setRewriteBubble] = useState<RewriteBubble | null>(null);

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

  useEffect(() => {
    if (!editor || !onRewriteSelection) return;

    const syncBubble = () => {
      if (writing) {
        setRewriteBubble(null);
        return;
      }
      const { from, to, empty } = editor.state.selection;
      if (empty) {
        setRewriteBubble(null);
        return;
      }
      const text = editor.state.doc.textBetween(from, to, " ").replace(/\s+/g, " ").trim();
      if (text.length < 2) {
        setRewriteBubble(null);
        return;
      }
      const domSel = window.getSelection();
      if (!domSel || domSel.rangeCount === 0 || domSel.isCollapsed) {
        setRewriteBubble(null);
        return;
      }
      const rect = domSel.getRangeAt(0).getBoundingClientRect();
      if (rect.width === 0 && rect.height === 0) {
        setRewriteBubble(null);
        return;
      }
      setRewriteBubble({
        top: rect.top,
        left: rect.left + rect.width / 2,
        text,
      });
    };

    let blurTimer = 0;
    const onBlur = () => {
      window.clearTimeout(blurTimer);
      blurTimer = window.setTimeout(() => {
        if (!window.getSelection()?.toString().trim()) setRewriteBubble(null);
      }, 180);
    };

    const onScroll = () => syncBubble();
    editor.on("selectionUpdate", syncBubble);
    editor.on("blur", onBlur);
    window.addEventListener("scroll", onScroll, true);
    window.addEventListener("resize", onScroll);

    return () => {
      window.clearTimeout(blurTimer);
      editor.off("selectionUpdate", syncBubble);
      editor.off("blur", onBlur);
      window.removeEventListener("scroll", onScroll, true);
      window.removeEventListener("resize", onScroll);
    };
  }, [editor, onRewriteSelection, writing]);

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

      {rewriteBubble && onRewriteSelection && !writing ? (
        <button
          type="button"
          className={styles.rewriteBubble}
          style={{ top: rewriteBubble.top, left: rewriteBubble.left }}
          onMouseDown={(e) => e.preventDefault()}
          onClick={() => {
            onRewriteSelection(rewriteBubble.text);
            setRewriteBubble(null);
            editor.commands.setTextSelection(editor.state.selection.to);
          }}
        >
          Rewrite?
        </button>
      ) : null}
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
