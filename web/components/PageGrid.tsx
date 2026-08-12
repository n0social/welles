"use client";

import { pageLabel, plainPreview, type Page } from "@/lib/types";
import styles from "./PageGrid.module.css";

type Props = {
  pages: Page[];
  activeId: string;
  onSelect: (id: string) => void;
  onAdd: () => void;
};

export default function PageGrid({ pages, activeId, onSelect, onAdd }: Props) {
  return (
    <div className={styles.gridWrap}>
      <div className={styles.grid}>
        {pages.map((page) => (
          <button
            key={page.id}
            type="button"
            className={page.id === activeId ? styles.cardOn : styles.card}
            onClick={() => onSelect(page.id)}
          >
            <span className={styles.num}>{page.documentName}</span>
            <span className={styles.title}>{pageLabel(page)}</span>
            <span className={styles.preview}>{plainPreview(page.html, 90)}</span>
          </button>
        ))}
        <button type="button" className={styles.add} onClick={onAdd}>
          + New page
        </button>
      </div>
    </div>
  );
}
