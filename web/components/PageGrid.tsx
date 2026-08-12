"use client";

import { cardSnippet, pageLabel, type Page } from "@/lib/types";
import styles from "./PageGrid.module.css";

type Props = {
  pages: Page[];
  activeId: string;
  onSelect: (id: string) => void;
  onAdd: () => void;
  onDelete: (id: string) => void;
};

export default function PageGrid({ pages, activeId, onSelect, onAdd, onDelete }: Props) {
  return (
    <div className={styles.gridWrap}>
      <div className={styles.grid}>
        {pages.map((page) => (
          <div
            key={page.id}
            className={page.id === activeId ? styles.cardOn : styles.card}
          >
            <button
              type="button"
              className={styles.cardHit}
              onClick={() => onSelect(page.id)}
            >
              <span className={styles.num}>{page.documentName}</span>
              <span className={styles.title}>{pageLabel(page)}</span>
              <span className={styles.preview}>{cardSnippet(page.html)}</span>
            </button>
            <button
              type="button"
              className={styles.delete}
              title="Delete page"
              aria-label={`Delete ${pageLabel(page)}`}
              onClick={(e) => {
                e.stopPropagation();
                onDelete(page.id);
              }}
            >
              <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
                <path
                  fill="currentColor"
                  d="M9 3h6l1 2h4v2H4V5h4l1-2zm1 6h2v10h-2V9zm4 0h2v10h-2V9zM7 9h2v10H7V9z"
                />
              </svg>
            </button>
          </div>
        ))}
        <button type="button" className={styles.add} onClick={onAdd}>
          + New page
        </button>
      </div>
    </div>
  );
}
