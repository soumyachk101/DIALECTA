# DIALECTA — App Flow

## 1. Onboarding Flow

```mermaid
flowchart LR
    A[Install extension] --> B[Sign up / sign in]
    B --> C[Connect calendar + email - read-only OAuth]
    C --> D[Set stated values & goals - feeds the Ethicist]
    D --> E[Guided demo intervention - shows the concept once]
    E --> F[Ready state]
```

Goals captured at onboarding (e.g. "saving for a trip," "no impulse buys over ₹2000," "be direct but kind in emails") are stored as `user_values` and are what the Ethicist agent checks decisions against (see `BACKEND_SCHEMA.md` §2).

## 2. Core Flow: Browser Checkout Intercept

```mermaid
flowchart TD
    A[User reaches checkout on a tracked page] --> B{Extension detects checkout DOM pattern}
    B -->|Yes| C[Create session + send page context to backend]
    B -->|No| Z[No action]
    C --> D[Backend fetches context: purchase history, calendar, stated goals]
    D --> E[4 agents debate in parallel, streamed to overlay]
    E --> F[Moderator gives closing recommendation]
    F --> G{User choice}
    G -->|Proceed anyway| H[Log as overridden]
    G -->|Cancel purchase| I[Log as accepted]
    G -->|Dismiss without reading| J[Log as ignored]
```

## 3. Core Flow: Voice Query Debate

```mermaid
flowchart TD
    A[User asks a question out loud] --> B[Whisper transcribes in real time]
    B --> C[Create session with transcribed query as the decision]
    C --> D[Backend fetches relevant context - e.g. sent folder, calendar]
    D --> E[4 agents debate, streamed as voice + text]
    E --> F[Moderator gives closing recommendation]
    F --> G[User acts / ignores]
    G --> H[Logged to Decision Log]
```

## 4. Core Flow: Decision Log Review

```mermaid
flowchart LR
    A[Open dashboard] --> B[Decision Log - chronological list]
    B --> C[Select a past decision]
    C --> D[Full debate transcript + citations + final outcome]
    D --> E[Optional: mark real-world outcome later - e.g. 'I regretted this anyway']
```

The optional outcome-tagging step is what eventually lets DIALECTA calibrate which agent's read was most often right for a given user — a natural post-hackathon feature, not required for MVP.

## 5. Settings Flow

- **Connected accounts** — view/revoke calendar & email connections.
- **Agent tuning** — adjust how aggressive the Skeptic is, how cautious the Ethicist is (slider, stored per-user).
- **Stated goals/values** — edit the text the Ethicist checks decisions against.

## 6. Error / Edge Case Flows

| Case | Behavior |
|---|---|
| LLM call times out mid-debate | Show "this agent is taking longer than expected" inline, don't block the other 3 agents' output |
| MCP returns no relevant context | Agents explicitly state "no relevant history found" rather than inventing one |
| User dismisses without reading | Logged as `ignored` — still valuable signal, not treated as an error |
| User has not connected calendar/email | Agents proceed on general reasoning only, with a visible "limited context" badge on the overlay |
