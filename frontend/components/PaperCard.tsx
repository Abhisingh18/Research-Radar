import type { PaperAlert } from "@/lib/papers";

const NOVELTY_STYLE: Record<string, string> = {
  HIGH: "bg-orange-500/15 text-orange-600 dark:text-orange-400",
  MEDIUM: "bg-yellow-500/15 text-yellow-700 dark:text-yellow-400",
  LOW: "bg-neutral-500/15 text-neutral-600 dark:text-neutral-400",
  UNKNOWN: "bg-neutral-500/15 text-neutral-600 dark:text-neutral-400",
};

export function PaperCard({ paper }: { paper: PaperAlert }) {
  const badgeClass = NOVELTY_STYLE[paper.novelty.novelty] ?? NOVELTY_STYLE.UNKNOWN;
  const publishedDate = new Date(paper.published).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });

  return (
    <article className="rounded-xl border border-black/10 dark:border-white/10 p-5 flex flex-col gap-3">
      <div className="flex items-start justify-between gap-3">
        <h2 className="text-base font-semibold leading-snug">
          <a href={paper.url} target="_blank" rel="noreferrer" className="hover:underline">
            {paper.title}
          </a>
        </h2>
        <span className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-medium ${badgeClass}`}>
          {paper.novelty.novelty}
        </span>
      </div>

      <div className="flex flex-wrap gap-1.5 text-xs">
        {paper.topics.map((topic) => (
          <span
            key={topic}
            className="rounded-full bg-black/5 dark:bg-white/10 px-2 py-0.5 text-neutral-600 dark:text-neutral-300"
          >
            {topic}
          </span>
        ))}
        <span className="text-neutral-400 dark:text-neutral-500">
          {publishedDate} · score {paper.score.toFixed(1)}/10
        </span>
      </div>

      {paper.novelty.why_interesting && (
        <p className="text-sm text-neutral-600 dark:text-neutral-300">{paper.novelty.why_interesting}</p>
      )}

      <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2 text-sm">
        <div>
          <dt className="font-medium text-neutral-500 dark:text-neutral-400">What&apos;s new</dt>
          <dd>{paper.novelty.new_contribution}</dd>
        </div>
        <div>
          <dt className="font-medium text-neutral-500 dark:text-neutral-400">Results</dt>
          <dd>{paper.novelty.results}</dd>
        </div>
      </dl>

      <div className="flex items-center justify-between text-xs text-neutral-500 dark:text-neutral-400 pt-1 border-t border-black/5 dark:border-white/10">
        <span>Code: {paper.novelty.code_available ? "Available" : "Not reported"}</span>
        <a href={paper.url} target="_blank" rel="noreferrer" className="hover:underline">
          Read paper →
        </a>
      </div>
    </article>
  );
}
