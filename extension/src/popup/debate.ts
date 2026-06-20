import "./debate.css";

const params = new URLSearchParams(location.search);
const sessionId = params.get("session")!;
const streamUrl = params.get("stream")!;
const BACKEND = streamUrl.split("/v1/")[0];

const $ = <T extends HTMLElement = HTMLElement>(sel: string) => document.querySelector(sel) as T;

const decisionText = $<HTMLDivElement>("#decision-text");
const decisionEl = $<HTMLDivElement>("#decision");
const connDot = $<HTMLSpanElement>("#conn-dot");
const connText = $<HTMLSpanElement>("#conn-text");
const footer = $<HTMLElement>("#footer");
const moderatorMsg = $<HTMLDivElement>("#moderator-msg");

const seatText: Record<string, HTMLElement | null> = {};
document.querySelectorAll(".seat").forEach((el) => {
  const agent = (el as HTMLElement).dataset.agent!;
  seatText[agent] = el.querySelector("[data-msg]") as HTMLElement;
});

function setActive(agent: string) {
  document.querySelectorAll(".seat").forEach((el) => {
    el.classList.toggle("active", (el as HTMLElement).dataset.agent === agent);
  });
}

function appendToSeat(agent: string, delta: string) {
  const el = seatText[agent];
  if (el) el.textContent = (el.textContent ?? "") + delta;
}

function setDecision(text: string) {
  decisionText.textContent = text;
}

async function resolve(outcome: "accepted" | "overridden" | "ignored") {
  const res = await fetch(`${BACKEND}/v1/sessions/${sessionId}/resolve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ outcome }),
  });
  if (res.ok) {
    document.body.innerHTML = `<div style="display:grid;place-items:center;height:100vh;font-family:'JetBrains Mono',monospace;color:#8B8D98">logged · ${outcome}</div>`;
  }
}

document.querySelectorAll<HTMLButtonElement>("[data-outcome]").forEach((btn) => {
  btn.addEventListener("click", () => resolve(btn.dataset.outcome as "accepted" | "overridden" | "ignored"));
});

async function bootstrap() {
  const meta = await fetch(`${BACKEND}/v1/sessions/${sessionId}`).then((r) => r.json());
  setDecision(meta.decision_summary);

  const ws = new WebSocket(streamUrl.replace(/^http/, "ws"));
  ws.onopen = () => {
    connDot.classList.add("live");
    connText.textContent = "debating";
  };
  ws.onclose = () => {
    connDot.classList.remove("live");
    connText.textContent = "closed";
  };
  ws.onerror = () => {
    connText.textContent = "error — using fallback";
  };
  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    if (msg.type === "context_loaded") {
      connText.textContent = "debating";
    } else if (msg.type === "token") {
      setActive(msg.agent);
      appendToSeat(msg.agent, msg.delta);
    } else if (msg.type === "agent_done") {
      setActive(msg.agent);
      // Final turn is already in the seat text from the token stream
    } else if (msg.type === "moderator_token") {
      setActive("ethicist");
      moderatorMsg.textContent = (moderatorMsg.textContent ?? "") + msg.delta;
    } else if (msg.type === "moderator_done") {
      footer.hidden = false;
      decisionEl.classList.add("hidden");
    } else if (msg.type === "error") {
      connText.textContent = `error: ${msg.detail}`;
    } else if (msg.type === "done") {
      connText.textContent = "done";
    }
  };
}

bootstrap();
