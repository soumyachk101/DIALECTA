/**
 * Background service worker.
 * - Receives intercepted actions from the content script
 * - Creates a debate session with the backend
 * - Opens the debate overlay in a new tab (or returns a stream URL for the popup)
 */
const BACKEND_URL = "http://localhost:8000";
const DEMO_USER_ID = "00000000-0000-0000-0000-000000000001";

interface InterceptedAction {
  type: "checkout" | "send" | "post";
  pageContext: {
    page_title: string;
    item?: string;
    amount?: string;
    currency?: string;
    urgency_banner_age_days?: number;
  };
}

async function createSession(action: InterceptedAction) {
  const decisionSummary = action.page_context?.item
    ? `About to buy: ${action.page_context.item} for ${action.page_context.amount ?? "unknown"} ${action.page_context.currency ?? ""}`.trim()
    : `Intercepted ${action.type} action on ${action.pageContext.page_title}`;

  const res = await fetch(`${BACKEND_URL}/v1/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: DEMO_USER_ID,
      trigger_type: action.type === "checkout" ? "checkout" : "manual",
      decision_summary: decisionSummary,
      page_context: action.pageContext,
    }),
  });
  if (!res.ok) throw new Error(`create session failed: ${res.status}`);
  return (await res.json()) as { id: string; decision_summary: string };
}

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  (async () => {
    try {
      if (msg.type === "DIALECTA_INTERCEPT") {
        const session = await createSession(msg.payload);
        const streamUrl = `${BACKEND_URL}/v1/sessions/${session.id}/stream`;
        const tabUrl = chrome.runtime.getURL("src/popup/debate.html") + `?session=${session.id}&stream=${encodeURIComponent(streamUrl)}`;
        await chrome.tabs.create({ url: tabUrl });
        sendResponse({ ok: true, sessionId: session.id });
      } else if (msg.type === "DIALECTA_RESOLVE") {
        const res = await fetch(`${BACKEND_URL}/v1/sessions/${msg.sessionId}/resolve`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ outcome: msg.outcome }),
        });
        sendResponse({ ok: res.ok });
      } else {
        sendResponse({ ok: false, error: "unknown message" });
      }
    } catch (e) {
      sendResponse({ ok: false, error: (e as Error).message });
    }
  })();
  return true; // keep channel open for async response
});
