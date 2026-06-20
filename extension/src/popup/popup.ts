import "./popup.css";

const DEMO_USER_ID = "00000000-0000-0000-0000-000000000001";
const BACKEND = "http://localhost:8000";

const $ = <T extends HTMLElement = HTMLElement>(sel: string) => document.querySelector(sel) as T;

const statusEl = $<HTMLSpanElement>("#status");

async function triggerDemo() {
  statusEl.textContent = "intercepting…";
  const tab = await chrome.tabs.query({ active: true, currentWindow: true });
  const [res] = await chrome.tabs.sendMessage(tab[0]!.id!, { type: "DIALECTA_FORCE_DEMO" }).catch(() => [null]);
  if (res?.ok) {
    statusEl.textContent = "opened debate tab";
  } else {
    // Fallback: directly create a session and open the debate view
    const session = await fetch(`${BACKEND}/v1/sessions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: DEMO_USER_ID,
        trigger_type: "manual",
        decision_summary: "Demo decision: should I buy this ₹4,999 ergonomic chair right now?",
        page_context: { page_title: "Demo Product", item: "Ergonomic chair", amount: "4999", currency: "INR", urgency_banner_age_days: 6 },
      }),
    }).then((r) => r.json());
    const stream = `${BACKEND}/v1/sessions/${session.id}/stream`;
    const url = chrome.runtime.getURL("src/popup/debate.html") + `?session=${session.id}&stream=${encodeURIComponent(stream)}`;
    await chrome.tabs.create({ url });
    statusEl.textContent = "opened debate tab";
  }
}

$("#trigger-demo").addEventListener("click", triggerDemo);
$("#open-dashboard").setAttribute("href", "http://localhost:3000");
