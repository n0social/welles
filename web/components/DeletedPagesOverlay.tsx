"use client";

import {
  DELETED_PAGE_TTL_MS,
  cardSnippet,
  pageLabel,
  type DeletedPage,
} from "@/lib/types";
import styles from "./DeletedPagesOverlay.module.css";

type Props = {
  open: boolean;
  pages: DeletedPage[];
  onClose: () => void;
  onRestore: (id: string) => void;
  onPurge: (id: string) => void;
};

function daysLeft(deletedAt: number): number {
  const left = DELETED_PAGE_TTL_MS - (Date.now() - deletedAt);
  return Math.max(1, Math.ceil(left / (24 * 60 * 60 * 1000)));
}

export default function DeletedPagesOverlay({
  open,
  pages,
  onClose,
  onRestore,
  onPurge,
}: Props) {
  if (!open) return null;

  return (
    <div
      className={styles.backdrop}
      role="dialog"
      aria-modal="true"
      aria-labelledby="deleted-title"
      onClick={onClose}
    >
      <div className={styles.sheet} onClick={(e) => e.stopPropagation()}>
        <div className={styles.head}>
          <div>
            <h2 id="deleted-title">Deleted pages</h2>
            <p>Recoverable for about 30 days in this browser’s local storage.</p>
          </div>
          <button type="button" className={styles.close} onClick={onClose}>
            Close
          </button>
        </div>

        {pages.length === 0 ? (
          <p className={styles.empty}>No recently deleted pages.</p>
        ) : (
          <div className={styles.grid}>
            {pages.map((page) => (
              <div key={page.id} className={styles.card}>
                <button
                  type="button"
                  className={styles.purge}
                  title="Delete forever"
                  aria-label={`Delete ${pageLabel(page)} forever`}
                  onClick={() => onPurge(page.id)}
                >
                  <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
                    <path
                      fill="currentColor"
                      d="M9 3h6l1 2h4v2H4V5h4l1-2zm1 6h2v10h-2V9zm4 0h2v10h-2V9zM7 9h2v10H7V9z"
                    />
                  </svg>
                </button>
                <div className={styles.body}>
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
      </div>
    </div>
  );
}
