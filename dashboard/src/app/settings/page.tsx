import { Sidebar } from "@/components/Sidebar";

const AGENTS = [
  { name: "optimist", label: "Optimist", color: "#38BDF8" },
  { name: "skeptic",  label: "Skeptic",  color: "#F5A524" },
  { name: "analyst",  label: "Analyst",  color: "#34D399" },
  { name: "ethicist", label: "Ethicist", color: "#7C3AED" },
];

const ACCOUNTS = [
  { provider: "google_calendar", connected: "2026-06-10" },
  { provider: "gmail",            connected: "2026-06-10" },
];

const DEFAULT_VALUES = [
  "Saving for a trip in 8 weeks",
  "No impulse buys over \u20B92000",
  "Be direct but kind in emails",
];

export default function SettingsPage() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-10 max-w-3xl">
        <header className="mb-10">
          <div className="font-mono text-[10px] tracking-[0.3em] text-text-muted mb-2">SETTINGS</div>
          <h1 className="text-[28px] font-semibold leading-tight">Tune your parliament.</h1>
        </header>

        <Section title="CONNECTED ACCOUNTS">
          <ul className="divide-y divide-border-subtle border-t border-b border-border-subtle">
            {ACCOUNTS.map((a) => (
              <li key={a.provider} className="py-4 flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">{a.provider}</div>
                  <div className="font-mono text-[10px] tracking-[0.2em] text-text-muted mt-1">
                    CONNECTED {a.connected}
                  </div>
                </div>
                <button className="font-mono text-[11px] tracking-[0.1em] text-text-muted hover:text-text-primary transition-colors">
                  Disconnect
                </button>
              </li>
            ))}
          </ul>
        </Section>

        <Section title="AGENT TUNING">
          <div className="border-t border-b border-border-subtle divide-y divide-border-subtle">
            {AGENTS.map((a) => (
              <div key={a.name} className="py-4 flex items-center gap-4">
                <span className="w-24 font-mono text-[11px] tracking-[0.1em]" style={{ color: a.color }}>{a.label}</span>
                <input type="range" min="0" max="100" defaultValue="50" className="flex-1" style={{ accentColor: a.color }} />
                <span className="w-10 text-right font-mono text-[10px] text-text-muted">50</span>
              </div>
            ))}
          </div>
        </Section>

        <Section title="STATED VALUES">
          <textarea
            defaultValue={DEFAULT_VALUES.join("\n")}
            rows={5}
            className="w-full bg-bg-elevated border border-border-subtle rounded-sm p-3 text-sm font-sans resize-y focus:border-text-muted focus:outline-none transition-colors"
          />
          <p className="mt-2 text-[12px] text-text-muted">One statement per line. The Ethicist checks every decision against these.</p>
        </Section>
      </main>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-10">
      <h2 className="font-mono text-[10px] tracking-[0.3em] text-text-muted mb-3">{title}</h2>
      {children}
    </section>
  );
}
