import { promises as fs } from "fs";
import path from "path";

export type Novelty = "HIGH" | "MEDIUM" | "LOW" | "UNKNOWN";

export interface NoveltyAnalysis {
  problem: string;
  new_contribution: string;
  architecture_innovation: string;
  results: string;
  code_available: boolean;
  novelty: Novelty;
  why_interesting: string;
  relevance_score: number;
  error: string | null;
}

export interface PaperAlert {
  id: string;
  title: string;
  url: string;
  published: string;
  topics: string[];
  score: number;
  novelty: NoveltyAnalysis;
}

// data/papers.json is written by the Python pipeline and lives one level up
// from this Next.js app (repo root's data/ directory).
const PAPERS_FILE = path.join(process.cwd(), "..", "data", "papers.json");

export async function getPapers(): Promise<PaperAlert[]> {
  try {
    const raw = await fs.readFile(PAPERS_FILE, "utf-8");
    return JSON.parse(raw) as PaperAlert[];
  } catch {
    return [];
  }
}
