import Link from "next/link";
import { notFound } from "next/navigation";
import { Sidebar } from "@/components/Sidebar";
import { DebateView } from "@/components/DebateView";
import { getDecision } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function DecisionDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  let decision;
  try {
    decision = await getDecision(id);
  } catch {
    notFound();
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-10 max-w-5xl">
        <Link href="/" className="font-mono text-[10px] tracking-[0.2em] text-text-muted hover:text-text-primary">
          ← BACK TO LOG
        </Link>
        <header className="mt-4 mb-8">
          <div className="font-mono text-[10px] tracking-[0.3em] text-text-muted mb-2 uppercase">
            {decision.session.trigger_type} · {new Date(decision.session.created_at).toLocaleString()}
          </div>
          <h1 className="text-[20px] font-semibold leading-tight">{decision.session.decision_summary}</h1>
          {decision.decision && (
            <div className="mt-3 font-mono text-[10px] tracking-[0.2em] text-text-muted">
              OUTCOME: <span className="text-text-primary">{decision.decision.outcome.toUpperCase()}</span>
            </div>
          )}
        </header>

        <DebateView decision={decision.session.decision_summary} turns={decision.turns} />

        <section className="mt-10">
          <h2 className="font-mono text-[10px] tracking-[0.3em] text-text-muted mb-3">FULL TRANSCRIPT</h2>
          <ol className="border-t border-border-subtle">
            {decision.turns.map((t) => (
              <li key={`${t.agent}-${t.turn_order}`} className="py-4 border-b border-border-subtle">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-mono text-[10px] tracking-[0.2em] text-text-muted">{t.agent.toUpperCase()}</span>
                  {t.no_context_found && (
                    <span className="font-mono text-[9px] tracking-[0.2em] text-accent-amber border border-accent-amber/40 px-1.5 py-0.5 rounded-sm">NO CONTEXT</span>
                  )}
                </div>
                <p className="text-sm leading-relaxed">{t.message}</p>
                {t.citations.length > 0 && (
                  <ul className="mt-2 space-y-1">
                    {t.citations.map((c, i) => (
                      <li key={i} className="font-mono text-[11px] text-text-muted">
                        <span className="text-accent-violet">{c.source}</span> · {c.detail}
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            ))}
          </ol>
        </section>
      </main>
    </div>
  );
}
