import type { DebateTurn } from "./api";

export const AGENT_META: Record<DebateTurn["agent"], { color: string; glyph: string; label: string; accentVar: string }> = {
  optimist: { color: "#38BDF8", glyph: "▲", label: "OPTIMIST", accentVar: "--accent-cyan" },
  skeptic:  { color: "#F5A524", glyph: "?", label: "SKEPTIC",  accentVar: "--accent-amber" },
  analyst:  { color: "#34D399", glyph: "#", label: "ANALYST",  accentVar: "--accent-emerald" },
  ethicist: { color: "#7C3AED", glyph: "◉", label: "ETHICIST", accentVar: "--accent-violet" },
  moderator:{ color: "#7C3AED", glyph: "◆", label: "MODERATOR",accentVar: "--accent-violet" },
};
