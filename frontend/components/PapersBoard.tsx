"use client";

import { useMemo, useState } from "react";
import type { PaperAlert } from "@/lib/papers";
import { PaperCard } from "@/components/PaperCard";

const RECENT_WINDOW_DAYS = 90;
const ARCHIVE_START_YEAR = 2022;

type View = "recent" | "archive";

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
  const [view, setView] = useState<View>("recent");

  const filtered = selected ? papers.filter((p) => p.topics.includes(selected)) : papers;

  const { recent, archive } = useMemo(() => {
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - RECENT_WINDOW_DAYS);
    const archiveStart = new Date(`${ARCHIVE_START_YEAR}-01-01T00:00:00Z`);

    const recent: PaperAlert[] = [];
    const archive: PaperAlert[] = [];
    for (const paper of filtered) {
      const published = new Date(paper.published);
      if (published >= cutoff) {
        recent.push(paper);
      } else if (published >= archiveStart) {
        archive.push(paper);
      }
    }
    return { recent, archive };
  }, [filtered]);

  const activePapers = view === "recent" ? recent : archive;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex gap-2 border-b border-black/10 dark:border-white/10 pb-4">
        <ViewTab
          label="Recent"
          subtitle={`last ${RECENT_WINDOW_DAYS} days`}
          count={recent.length}
          active={view === "recent"}
          onClick={() => setView("recent")}
        />
        <ViewTab
          label="Archive"
          subtitle={`${ARCHIVE_START_YEAR} onwards`}
          count={archive.length}
          active={view === "archive"}
          onClick={() => setView("archive")}
        />
      </div>

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

      {activePapers.length === 0 ? (
        <p className="text-sm text-neutral-500 dark:text-neutral-400">
          {view === "recent" ? "No recent papers in this category yet." : "No older papers in this category yet."}
        </p>
      ) : (
        <div className="flex flex-col gap-4">
          {activePapers.map((paper) => (
            <PaperCard key={paper.id} paper={paper} />
          ))}
        </div>
      )}
    </div>
  );
}

function ViewTab({
  label,
  subtitle,
  count,
  active,
  onClick,
}: {
  label: string;
  subtitle: string;
  count: number;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`rounded-lg px-4 py-2 text-left transition-colors ${
        active
          ? "bg-foreground text-background"
          : "bg-black/5 dark:bg-white/10 text-neutral-600 dark:text-neutral-300 hover:bg-black/10 dark:hover:bg-white/15"
      }`}
    >
      <div className="text-sm font-semibold">
        {label} <span className="opacity-60 font-normal">{count}</span>
      </div>
      <div className="text-xs opacity-70">{subtitle}</div>
    </button>
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
