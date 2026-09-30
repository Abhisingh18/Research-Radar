"use client";

import { useMemo, useState } from "react";
import type { PaperAlert } from "@/lib/papers";
import { PaperCard } from "@/components/PaperCard";

const RECENT_WINDOW_DAYS = 90;
const ARCHIVE_START_YEAR = 2022;

export function PapersBoard({ papers }: { papers: PaperAlert[] }) {
  const topics = useMemo(() => {
    const counts = new Map<string, number>();
    for (const paper of papers) {
      for (const topic of paper.topics) {
        counts.set(topic, (counts.get(topic) ?? 0) + 1);
      }
    }
    return Array.from(counts.entries()).sort((a, b) => b[1] - a[1]);
  }, [papers]);

  const [selected, setSelected] = useState<string | null>(null);

  const visible = selected ? papers.filter((p) => p.topics.includes(selected)) : papers;

  const { recent, archive } = useMemo(() => {
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - RECENT_WINDOW_DAYS);
    const archiveStart = new Date(`${ARCHIVE_START_YEAR}-01-01T00:00:00Z`);

    const recent: PaperAlert[] = [];
    const archive: PaperAlert[] = [];
    for (const paper of visible) {
      const published = new Date(paper.published);
      if (published >= cutoff) {
        recent.push(paper);
      } else if (published >= archiveStart) {
        archive.push(paper);
      }
    }
    return { recent, archive };
  }, [visible]);

  return (
    <div className="flex flex-col gap-10">
      <div className="flex flex-wrap gap-2">
        <TopicChip
          label="All"
          count={papers.length}
          active={selected === null}
          onClick={() => setSelected(null)}
        />
        {topics.map(([topic, count]) => (
          <TopicChip
            key={topic}
            label={topic}
            count={count}
            active={selected === topic}
            onClick={() => setSelected(topic)}
          />
        ))}
      </div>

      <Section
        title="Latest"
        subtitle={`Last ${RECENT_WINDOW_DAYS} days`}
        papers={recent}
        emptyMessage="No recent papers in this category yet."
      />

      <Section
        title="Archive"
        subtitle={`${ARCHIVE_START_YEAR} onwards`}
        papers={archive}
        emptyMessage="No older papers in this category yet."
      />
    </div>
  );
}

function Section({
  title,
  subtitle,
  papers,
  emptyMessage,
}: {
  title: string;
  subtitle: string;
  papers: PaperAlert[];
  emptyMessage: string;
}) {
  return (
    <section className="flex flex-col gap-4">
      <div className="flex items-baseline gap-2">
        <h2 className="text-lg font-semibold">{title}</h2>
        <span className="text-sm text-neutral-400 dark:text-neutral-500">
          {subtitle} · {papers.length}
        </span>
      </div>

      {papers.length === 0 ? (
        <p className="text-sm text-neutral-500 dark:text-neutral-400">{emptyMessage}</p>
      ) : (
        <div className="flex flex-col gap-4">
          {papers.map((paper) => (
            <PaperCard key={paper.id} paper={paper} />
          ))}
        </div>
      )}
    </section>
  );
}

function TopicChip({
  label,
  count,
  active,
  onClick,
}: {
  label: string;
  count: number;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`rounded-full px-3.5 py-1.5 text-sm font-medium transition-colors border ${
        active
          ? "bg-foreground text-background border-foreground"
          : "bg-transparent text-neutral-600 dark:text-neutral-300 border-black/10 dark:border-white/15 hover:border-black/30 dark:hover:border-white/40"
      }`}
    >
      {label} <span className="opacity-60">{count}</span>
    </button>
  );
}
