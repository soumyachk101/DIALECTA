import Link from "next/link";
import { Sidebar } from "@/components/Sidebar";
import { listDecisions, type DecisionLogItem } from "@/lib/api";

export const dynamic = "force-dynamic";

const OUTCOME_META: Record<string, { label: string; color: string }> = {
  accepted:  { label: "ACCEPTED",  color: "text-accent-emerald" },
  overridden:{ label: "OVERRIDDEN",color: "text-accent-amber" },
  ignored:   { label: "IGNORED",   color: "text-text-muted" },
};

export default async function HomePage() {
  let decisions: DecisionLogItem[] = [];
  let error: string | null = null;
  try {
    decisions = await listDecisions();
  } catch (e) {
    error = (e as Error).message;
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-10 max-w-5xl">
        <header className="mb-10">
          <div className="font-mono text-[10px] tracking-[0.3em] text-text-muted mb-2">DECISION LOG</div>
          <h1 className="text-[28px] font-semibold leading-tight">Every debate that ran before you acted.</h1>
          <p className="text-sm text-text-muted mt-2 max-w-2xl">Outcomes update as you accept, override, or ignore interventions. Open any row to read the full transcript.</p>
        </header>

        {error && (
          <div className="mb-6 p-4 border border-accent-amber/40 rounded-sm bg-bg-elevated text-sm text-accent-amber font-mono">
            Could not reach backend: {error}
          </div>
        )}

        {decisions.length === 0 && !error ? (
          <EmptyState />
        ) : (
          <ul className="divide-y divide-border-subtle border-t border-b border-border-subtle">
            {decisions.map((d) => {
              const outcome = d.outcome ? OUTCOME_META[d.outcome] : null;
              return (
                <li key={d.session_id}>
                  <Link href={`/decisions/${d.session_id}`} className="block py-5 px-1 hover:bg-bg-elevated/50 transition-colors">
                    <div className="flex items-baseline justify-between gap-6">
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium truncate">{d.decision_summary}</div>
                        <div className="mt-1 font-mono text-[10px] tracking-[0.18em] text-text-muted uppercase">
                          {d.trigger_type} · {new Date(d.created_at).toLocaleString()}
                        </div>
                      </div>
                      <div className={`font-mono text-[10px] tracking-[0.2em] ${outcome?.color ?? "text-text-muted/50"}`}>
                        {outcome?.label ?? "PENDING"}
                      </div>
                    </div>
                  </Link>
                </li>
              );
            })}
          </ul>
        )}
      </main>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="border border-dashed border-border-subtle rounded-sm p-12 text-center">
      <div className="font-mono text-[10px] tracking-[0.3em] text-text-muted mb-3">NO DEBATES YET</div>
      <p className="text-sm text-text-muted max-w-sm mx-auto">
        Install the extension and trigger an intervention (or hit “Trigger demo intercept” in the popup).
        The first debate will land here.
      </p>
    </div>
  );
}
