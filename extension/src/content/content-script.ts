/**
 * Content script — detects checkout / send-like actions and surfaces the intervention.
 * For the hackathon we look for high-signal DOM patterns:
 *   - buttons whose text matches /buy|checkout|pay|place order|send|post/i
 *   - a known demo product page marker (data-dialecta="demo-product") for testing
 */
const TRIGGER_KEYWORDS = /\b(buy|checkout|pay|place order|confirm purchase|send|post|tweet|submit|sign)\b/i;

let intercepted = false;

function interceptAction(button: HTMLElement) {
  if (intercepted) return;
  intercepted = true;

  // Pull page context — this is what the orchestrator receives
  const pageContext = {
    page_title: document.title,
    item: readMeta("product:title") || readMeta("og:title") || button.innerText.trim(),
    amount: readMeta("product:price:amount") || detectAmountFromPage(),
    currency: readMeta("product:price:currency") || "INR",
    urgency_banner_age_days: detectUrgencyBannerAge(),
  };

  // Notify the service worker
  chrome.runtime.sendMessage(
    {
      type: "DIALECTA_INTERCEPT",
      payload: { type: "checkout", pageContext },
    },
    () => {
      // After a beat, allow the same button to be intercepted again (e.g. if user reopens)
      setTimeout(() => (intercepted = false), 4000);
    }
  );

  // Pause the action visually for the debate (5s per PRD user story)
  showInlineBadge(button);
}

function showInlineBadge(target: HTMLElement) {
  const badge = document.createElement("div");
  badge.className = "dialecta-inline-badge";
  badge.textContent = "DIALECTA is opening a debate…";
  badge.style.cssText = `
    position: fixed; bottom: 20px; right: 20px; z-index: 2147483647;
    background: #13141A; color: #F4F4F6; border: 1px solid #7C3AED;
    padding: 10px 14px; border-radius: 4px; font: 500 13px/1.4 'JetBrains Mono', monospace;
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
  `;
  document.body.appendChild(badge);
  setTimeout(() => badge.remove(), 5000);
}

function readMeta(name: string): string | null {
  const el = document.querySelector(`meta[name="${name}"], meta[property="${name}"]`);
  return el?.getAttribute("content") ?? null;
}

function detectAmountFromPage(): string | null {
  // Best-effort scan for a price-looking token
  const re = /(?:₹|rs\.?|inr|\$|€|£)\s?([0-9][0-9,]*)/i;
  const text = document.body.innerText.slice(0, 5000);
  const m = text.match(re);
  return m ? m[1].replace(/,/g, "") : null;
}

function detectUrgencyBannerAge(): number | undefined {
  // For the demo, treat a "limited time" banner as 6 days old if it exists
  const banner = Array.from(document.querySelectorAll("*")).find((el) =>
    /limited time|hurry|ending soon|only \d+ left/i.test(el.textContent ?? "")
  );
  return banner ? 6 : undefined;
}

document.addEventListener(
  "click",
  (e) => {
    const target = (e.target as HTMLElement)?.closest("button, a, input[type=submit]");
    if (!target) return;
    const text = (target.textContent || (target as HTMLInputElement).value || "").trim();
    if (TRIGGER_KEYWORDS.test(text)) {
      interceptAction(target as HTMLElement);
    }
  },
  true
);

// Demo marker — pages with data-dialecta="demo-product" always trigger on load
const demoProduct = document.querySelector('[data-dialecta="demo-product"]');
if (demoProduct) {
  const fakeButton = document.createElement("button");
  fakeButton.textContent = "Buy now";
  fakeButton.style.cssText = "position:fixed;bottom:80px;right:20px;z-index:9999;padding:12px 18px;background:#7C3AED;color:#fff;border:0;border-radius:6px;cursor:pointer;font:600 14px/1 sans-serif";
  fakeButton.addEventListener("click", (e) => {
    e.preventDefault();
    interceptAction(fakeButton);
  });
  document.body.appendChild(fakeButton);
}
