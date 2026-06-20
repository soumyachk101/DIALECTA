import "../popup/popup.css";

const AGENTS = [
  { name: "optimist", label: "Optimist", color: "#38BDF8" },
  { name: "skeptic",  label: "Skeptic",  color: "#F5A524" },
  { name: "analyst",  label: "Analyst",  color: "#34D399" },
  { name: "ethicist", label: "Ethicist", color: "#7C3AED" },
];

const accounts = document.querySelector<HTMLUListElement>("#accounts")!;
const sliders  = document.querySelector<HTMLDivElement>("#sliders")!;
const valuesEl = document.querySelector<HTMLTextAreaElement>("#values")!;

(async () => {
  const stored = await chrome.storage.local.get(["accounts", "tuning", "values"]);
  (stored.accounts ?? ["google_calendar", "gmail"]).forEach((p: string) => {
    const li = document.createElement("li");
    li.style.cssText = "display:flex;justify-content:space-between;padding:8px 10px;background:#13141A;border:1px solid #23252E;border-radius:4px;font:500 12px/1 'JetBrains Mono', monospace";
    li.innerHTML = `<span>${p}</span><a href="#" style="color:#8B8D98;text-decoration:none">Disconnect</a>`;
    accounts.appendChild(li);
  });

  AGENTS.forEach((a) => {
    const row = document.createElement("div");
    row.style.cssText = "display:flex;align-items:center;gap:10px;margin:6px 0";
    row.innerHTML = `
      <span style="width:80px;font:500 11px/1 'JetBrains Mono', monospace;letter-spacing:0.1em;color:${a.color}">${a.label}</span>
      <input type="range" min="0" max="100" value="50" data-agent="${a.name}" style="flex:1;accent-color:${a.color}">
      <span style="width:30px;text-align:right;font:500 10px/1 'JetBrains Mono', monospace;color:#8B8D98">50</span>
    `;
    row.querySelector("input")!.addEventListener("input", (e) => {
      const v = (e.target as HTMLInputElement).value;
      row.querySelector("span:last-child")!.textContent = v;
    });
    sliders.appendChild(row);
  });

  valuesEl.value = (stored.values ?? [
    "Saving for a trip in 8 weeks",
    "No impulse buys over ₹2000",
    "Be direct but kind in emails",
  ]).join("\n");
})();
