import type { PaperAlert } from "@/lib/papers";

export function StatsStrip({ papers }: { papers: PaperAlert[] }) {
  const total = papers.length;
  const avgScore = total ? papers.reduce((sum, p) => sum + p.score, 0) / total : 0;
  const topicCount = new Set(papers.flatMap((p) => p.topics)).size;
  const withCode = papers.filter((p) => p.novelty.code_available).length;

  const stats = [
    { label: "Papers tracked", value: total.toString() },
    { label: "Avg score", value: avgScore.toFixed(1) },
    { label: "Topics covered", value: topicCount.toString() },
    { label: "With code", value: withCode.toString() },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-px rounded-2xl overflow-hidden ring-1 ring-black/5 dark:ring-white/10 bg-black/5 dark:bg-white/10">
      {stats.map((stat) => (
        <div key={stat.label} className="bg-white dark:bg-neutral-950 px-4 py-3.5">
          <div className="text-xl font-bold tabular-nums tracking-tight">{stat.value}</div>
          <div className="text-[11px] text-neutral-500 dark:text-neutral-400">{stat.label}</div>
        </div>
      ))}
    </div>
  );
}
