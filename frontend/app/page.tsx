import { getPapers } from "@/lib/papers";
import { PaperCard } from "@/components/PaperCard";

export const dynamic = "force-dynamic";

export default async function Home() {
  const papers = await getPapers();

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black">
      <main className="mx-auto w-full max-w-4xl px-6 py-12">
        <header className="mb-10">
          <h1 className="text-2xl font-semibold tracking-tight">Research Radar</h1>
          <p className="mt-1 text-sm text-neutral-500 dark:text-neutral-400">
            ASR · TTS · Speech LLMs · VLMs · Multimodal · AI Agents — genuinely new papers only.
          </p>
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
          <div className="flex flex-col gap-4">
            {papers.map((paper) => (
              <PaperCard key={paper.id} paper={paper} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
