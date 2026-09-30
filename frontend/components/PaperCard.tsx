import type { PaperAlert } from "@/lib/papers";

const NOVELTY_ACCENT: Record<string, string> = {
  HIGH: "before:bg-orange-500",
  MEDIUM: "before:bg-yellow-500",
  LOW: "before:bg-neutral-400",
  UNKNOWN: "before:bg-neutral-400",
};

const NOVELTY_BADGE: Record<string, string> = {
  HIGH: "bg-orange-500/10 text-orange-600 dark:text-orange-400 ring-1 ring-orange-500/20",
  MEDIUM: "bg-yellow-500/10 text-yellow-700 dark:text-yellow-400 ring-1 ring-yellow-500/20",
  LOW: "bg-neutral-500/10 text-neutral-600 dark:text-neutral-400 ring-1 ring-neutral-500/20",
  UNKNOWN: "bg-neutral-500/10 text-neutral-600 dark:text-neutral-400 ring-1 ring-neutral-500/20",
};

function scoreColor(score: number): string {
  if (score >= 9) return "text-orange-600 dark:text-orange-400";
  if (score >= 7) return "text-yellow-600 dark:text-yellow-400";
  return "text-neutral-500 dark:text-neutral-400";
}

export function PaperCard({ paper }: { paper: PaperAlert }) {
  const accent = NOVELTY_ACCENT[paper.novelty.novelty] ?? NOVELTY_ACCENT.UNKNOWN;
  const badgeClass = NOVELTY_BADGE[paper.novelty.novelty] ?? NOVELTY_BADGE.UNKNOWN;
  const publishedDate = new Date(paper.published).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });

  return (
    <article
      className={`group relative overflow-hidden rounded-2xl bg-white dark:bg-white/[0.03] ring-1 ring-black/5 dark:ring-white/10 shadow-sm hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200 pl-6 pr-5 py-5 flex flex-col gap-4 before:content-[''] before:absolute before:left-0 before:top-0 before:bottom-0 before:w-1.5 ${accent}`}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex flex-col gap-1.5 min-w-0">
          <h2 className="text-base font-semibold leading-snug tracking-tight">
            <a
              href={paper.url}
              target="_blank"
              rel="noreferrer"
              className="text-neutral-900 dark:text-neutral-50 hover:text-orange-600 dark:hover:text-orange-400 transition-colors"
            >
              {paper.title}
            </a>
          </h2>
          <div className="flex flex-wrap items-center gap-1.5">
            {paper.topics.map((topic) => (
              <span
                key={topic}
                className="rounded-full bg-black/[0.04] dark:bg-white/10 px-2 py-0.5 text-[11px] font-medium text-neutral-600 dark:text-neutral-300"
              >
                {topic}
              </span>
            ))}
            <span className="text-[11px] text-neutral-400 dark:text-neutral-500">{publishedDate}</span>
          </div>
        </div>

        <div className="flex shrink-0 flex-col items-end gap-1.5">
          <span className={`rounded-full px-2.5 py-1 text-[11px] font-semibold tracking-wide ${badgeClass}`}>
            {paper.novelty.novelty}
          </span>
          <span className={`text-lg font-bold tabular-nums leading-none ${scoreColor(paper.score)}`}>
            {paper.score.toFixed(1)}
            <span className="text-xs font-medium text-neutral-400 dark:text-neutral-500">/10</span>
          </span>
        </div>
      </div>

      {paper.novelty.why_interesting && (
        <p className="text-sm leading-relaxed text-neutral-600 dark:text-neutral-300 border-l-2 border-black/10 dark:border-white/10 pl-3">
          {paper.novelty.why_interesting}
        </p>
      )}

      <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-3 text-sm">
        <div>
          <dt className="text-[11px] font-semibold uppercase tracking-wide text-neutral-400 dark:text-neutral-500 mb-0.5">
            What&apos;s new
          </dt>
          <dd className="text-neutral-700 dark:text-neutral-300">{paper.novelty.new_contribution}</dd>
        </div>
        <div>
          <dt className="text-[11px] font-semibold uppercase tracking-wide text-neutral-400 dark:text-neutral-500 mb-0.5">
            Results
          </dt>
          <dd className="text-neutral-700 dark:text-neutral-300">{paper.novelty.results}</dd>
        </div>
      </dl>

      <div className="flex items-center justify-between text-xs pt-3 border-t border-black/[0.06] dark:border-white/10">
        <span className="inline-flex items-center gap-1.5 text-neutral-500 dark:text-neutral-400">
          <span
            className={`h-1.5 w-1.5 rounded-full ${
              paper.novelty.code_available ? "bg-emerald-500" : "bg-neutral-300 dark:bg-neutral-600"
            }`}
          />
          Code {paper.novelty.code_available ? "available" : "not reported"}
        </span>
        <a
          href={paper.url}
          target="_blank"
          rel="noreferrer"
          className="font-medium text-neutral-500 dark:text-neutral-400 group-hover:text-orange-600 dark:group-hover:text-orange-400 transition-colors"
        >
          Read paper →
        </a>
      </div>
    </article>
  );
}
