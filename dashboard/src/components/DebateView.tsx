import type { DebateTurn } from "@/lib/api";
import { AGENT_META } from "@/lib/agent-style";

const ORDER: DebateTurn["agent"][] = ["optimist", "skeptic", "analyst", "ethicist"];

export function DebateView({ decision, turns }: { decision: string; turns: DebateTurn[] }) {
  const turnByAgent = Object.fromEntries(turns.map((t) => [t.agent, t])) as Record<string, DebateTurn | undefined>;
  const moderator = turnByAgent["moderator"];

  return (
    <div className="relative w-full h-[520px] grid place-items-center">
      {/* radial seats */}
      <div className="absolute top-[6%] left-1/2 -translate-x-1/2 w-72">
        <SeatCard agent="optimist" turn={turnByAgent["optimist"]} />
      </div>
      <div className="absolute left-[4%] top-1/2 -translate-y-1/2 w-72">
        <SeatCard agent="skeptic" turn={turnByAgent["skeptic"]} />
      </div>
      <div className="absolute right-[4%] top-1/2 -translate-y-1/2 w-72">
        <SeatCard agent="analyst" turn={turnByAgent["analyst"]} />
      </div>
      <div className="absolute bottom-[6%] left-1/2 -translate-x-1/2 w-72">
        <SeatCard agent="ethicist" turn={turnByAgent["ethicist"]} />
      </div>

      {/* decision at center */}
      <div className={`relative w-72 p-6 rounded-sm border border-dashed border-border-subtle bg-bg-elevated text-center z-10 transition-opacity ${moderator ? "opacity-20" : "opacity-100"}`}>
        <div className="font-mono text-[10px] tracking-[0.2em] text-text-muted mb-2">DECISION</div>
        <div className="text-sm font-medium leading-snug">{decision}</div>
      </div>

      {moderator && (
        <div className="absolute bottom-3 left-1/2 -translate-x-1/2 w-[640px] max-w-[92vw] p-4 rounded-sm border border-accent-violet bg-bg-elevated z-20">
          <div className="font-mono text-[10px] tracking-[0.2em] text-accent-violet mb-1">MODERATOR</div>
          <div className="text-sm font-medium leading-snug">{moderator.message}</div>
        </div>
      )}
    </div>
  );
}

function SeatCard({ agent, turn }: { agent: DebateTurn["agent"]; turn?: DebateTurn }) {
  const meta = AGENT_META[agent];
  const active = !!turn;
  return (
    <div
      className={`p-4 rounded-sm border border-border-subtle bg-bg-elevated/85 backdrop-blur transition-all ${
        active ? "opacity-100" : "opacity-40"
      }`}
      style={{ borderLeftWidth: 2, borderLeftColor: meta.color }}
    >
      <div className="flex items-center gap-2 mb-2">
        <span
          className="inline-grid place-items-center w-[18px] h-[18px] rounded-sm text-[11px] font-mono font-semibold"
          style={{ background: meta.color, color: "#0A0A0C" }}
        >
          {meta.glyph}
        </span>
        <span className="font-mono text-[10px] tracking-[0.2em] text-text-muted">{meta.label}</span>
      </div>
      <div className="text-[13px] leading-[1.45] min-h-[3.4em]">
        {turn ? turn.message : <span className="text-text-muted/60">…</span>}
      </div>
    </div>
  );
}
