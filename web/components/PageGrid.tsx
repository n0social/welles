"use client";

import {
  DELETED_PAGE_TTL_MS,
  cardSnippet,
  pageLabel,
  type DeletedPage,
  type Page,
} from "@/lib/types";
import styles from "./PageGrid.module.css";

type Props = {
  pages: Page[];
  deletedPages: DeletedPage[];
  activeId: string;
  onSelect: (id: string) => void;
  onAdd: () => void;
  onDelete: (id: string) => void;
  onRestore: (id: string) => void;
};

function daysLeft(deletedAt: number): number {
  const left = DELETED_PAGE_TTL_MS - (Date.now() - deletedAt);
  return Math.max(1, Math.ceil(left / (24 * 60 * 60 * 1000)));
}

export default function PageGrid({
  pages,
  deletedPages,
  activeId,
  onSelect,
  onAdd,
  onDelete,
  onRestore,
}: Props) {
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

      <section className={styles.trash}>
        <div className={styles.trashHead}>
          <h3>Deleted pages</h3>
          <p>Recoverable for about 30 days (while this browser keeps local storage).</p>
        </div>
        {deletedPages.length === 0 ? (
          <p className={styles.trashEmpty}>No recently deleted pages.</p>
        ) : (
          <div className={styles.grid}>
            {deletedPages.map((page) => (
              <div key={page.id} className={styles.trashCard}>
                <div className={styles.cardHit}>
                  <span className={styles.num}>{page.documentName}</span>
                  <span className={styles.title}>{pageLabel(page)}</span>
                  <span className={styles.preview}>{cardSnippet(page.html)}</span>
                  <span className={styles.ttl}>{daysLeft(page.deletedAt)}d left</span>
                </div>
                <button
                  type="button"
                  className={styles.restore}
                  onClick={() => onRestore(page.id)}
                >
                  Recover
                </button>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
