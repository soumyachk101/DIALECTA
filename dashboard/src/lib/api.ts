/**
 * Tiny client for the FastAPI backend. Uses the Next.js rewrite to /v1/* in dev.
 */
const API = ""; // same-origin — Next.js rewrite proxies /v1/* to the FastAPI service

export type DecisionLogItem = {
  session_id: string;
  decision_summary: string;
  outcome: string | null;
  trigger_type: string;
  created_at: string;
  moderator_summary: string | null;
};

export type DebateTurn = {
  agent: "optimist" | "skeptic" | "analyst" | "ethicist" | "moderator";
  message: string;
  citations: { source: string; detail: string }[];
  confidence: number | null;
  no_context_found: boolean;
  turn_order: number;
};

export type DecisionDetail = {
  session: { id: string; decision_summary: string; trigger_type: string; created_at: string };
  turns: DebateTurn[];
  decision: { outcome: string; moderator_summary: string | null; resolved_at: string } | null;
};

export async function listDecisions(): Promise<DecisionLogItem[]> {
  const res = await fetch(`${API}/v1/decisions`, { cache: "no-store" });
  if (!res.ok) throw new Error(`listDecisions ${res.status}`);
  return res.json();
}

export async function getDecision(id: string): Promise<DecisionDetail> {
  const res = await fetch(`${API}/v1/decisions/${id}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`getDecision ${res.status}`);
  return res.json();
}

export async function createSession(payload: { user_id: string; trigger_type: string; decision_summary: string; page_context?: Record<string, unknown> }) {
  const res = await fetch(`${API}/v1/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`createSession ${res.status}`);
  return res.json() as Promise<{ id: string }>;
}
