"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
  { href: "/", label: "Log", icon: "≡" },
  { href: "/settings", label: "Settings", icon: "✦" },
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="w-14 border-r border-border-subtle flex flex-col items-center py-6 gap-6 bg-bg-base">
      <div className="w-7 h-7 rounded-sm bg-accent-violet grid place-items-center font-mono text-[10px] font-bold text-bg-base">D</div>
      <nav className="flex flex-col gap-4 mt-4">
        {NAV.map((n) => (
          <Link
            key={n.href}
            href={n.href}
            className={`group relative w-9 h-9 grid place-items-center rounded-sm text-text-muted hover:text-text-primary transition-colors ${
              pathname === n.href ? "text-text-primary bg-bg-elevated" : ""
            }`}
            aria-label={n.label}
          >
            <span className="text-lg leading-none">{n.icon}</span>
            <span className="absolute left-full ml-2 px-2 py-1 rounded-sm bg-bg-elevated text-[10px] font-mono uppercase tracking-widest opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap border border-border-subtle">
              {n.label}
            </span>
          </Link>
        ))}
      </nav>
    </aside>
  );
}
