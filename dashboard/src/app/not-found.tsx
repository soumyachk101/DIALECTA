import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen grid place-items-center">
      <div className="text-center">
        <div className="font-mono text-[10px] tracking-[0.3em] text-text-muted mb-3">404</div>
        <h1 className="text-[20px] font-semibold mb-3">No debate found at that address.</h1>
        <Link href="/" className="font-mono text-[11px] tracking-[0.1em] text-accent-cyan hover:underline">
          ← back to the decision log
        </Link>
      </div>
    </div>
  );
}
