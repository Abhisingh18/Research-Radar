import { getPapers } from "@/lib/papers";
import { PapersBoard } from "@/components/PapersBoard";
import { StatsStrip } from "@/components/StatsStrip";
import { ThemeToggle } from "@/components/ThemeToggle";

export const dynamic = "force-dynamic";

export default async function Home() {
  const papers = await getPapers();

  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-50 to-white dark:from-black dark:to-neutral-950">
      <main className="mx-auto w-full max-w-5xl px-6 py-14">
        <header className="mb-8 flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <span className="relative flex h-3 w-3 shrink-0">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-orange-500 opacity-60" />
              <span className="relative inline-flex h-3 w-3 rounded-full bg-orange-500" />
            </span>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Research Radar</h1>
              <p className="mt-0.5 text-sm text-neutral-500 dark:text-neutral-400">
                ASR · TTS · Speech LLMs · VLMs · Multimodal · AI Agents — genuinely new papers only.
              </p>
            </div>
          </div>
          <ThemeToggle />
        </header>

        {papers.length === 0 ? (
          <p className="text-sm text-neutral-500 dark:text-neutral-400">
            No alerts yet. Run{" "}
            <code className="rounded bg-black/[.06] px-1.5 py-0.5 font-mono text-[0.85em] dark:bg-white/[.08]">
              python -m research_radar run
            </code>{" "}
            from the repo root to populate data/papers.json.
          </p>
        ) : (
          <div className="flex flex-col gap-8">
            <StatsStrip papers={papers} />
            <PapersBoard papers={papers} />
          </div>
        )}

        <footer className="mt-16 pt-6 border-t border-black/5 dark:border-white/10 flex flex-wrap items-center justify-between gap-2 text-xs text-neutral-400 dark:text-neutral-500">
          <span>Sourced from arXiv · scored by an LLM via OpenRouter</span>
          <a
            href="https://github.com/Abhisingh18/Research-Radar"
            target="_blank"
            rel="noreferrer"
            className="hover:text-neutral-600 dark:hover:text-neutral-300 transition-colors"
          >
            View source →
          </a>
        </footer>
      </main>
    </div>
  );
}
