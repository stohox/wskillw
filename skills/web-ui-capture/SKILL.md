---
name: web-ui-capture
description: Use when recording an existing website or web application for reference, including capturing page states and producing an offline interactive HTML prototype with mock data.
---

# Web UI Capture

Capture observable website pages and their states as evidence, then create an offline interactive HTML prototype with mock data. Respect the requested scope, fidelity, and output location. Default to a browsable prototype plus screenshots and concise page notes.

## Capture

1. Identify the target URL or existing browser tab, accessible session, requested pages, and output location from context. If the target cannot be identified or reached, request the missing information. Use the existing authenticated browser session where supported; never request or record passwords or session tokens.
2. Prefer available browser/computer-use tools; use Playwright when appropriate and available. Follow the relevant tool's instructions. Inspect navigation and capture representative pages at a consistent viewport. For each page capture its initial state and relevant observable states such as expanded filters, dropdowns, dialogs, drawers, validation and empty results. Scroll within page and nested regions when needed. Record viewport and page URL without sensitive query parameters.
3. Observe navigation, labels, fields, tables, controls, layout, visual tokens, and interaction outcomes. Note permission-limited, inaccessible or unobserved states explicitly. Do not assert that inferred behavior was observed. Limit exploration to the authorized scope; avoid submitting real changes or destructive operations. Use read-only inspection and safe UI states; ask for a safe test environment if a required state cannot be observed without modifying real data.
4. Save a page index, screenshots, and concise notes mapping pages and states to evidence. Avoid retaining real personal or business data, secrets, cookies, tokens, or network payloads; use synthetic values in notes and prototype. Check screenshots for sensitive content and redact or omit it when needed. If a safe capture is impossible, describe the limitation.

## Prototype

- Implement observed pages as a self-contained local HTML prototype with local CSS/JS and synthetic data, without external services or production requests. Prefer an `index.html` that opens directly via `file://`; embed mock data or use local scripts rather than `fetch()` of local JSON. If a server is necessary, explain how to start it.
- Reproduce the observed layout, navigation, labels, controls, and states to the requested fidelity. Provide working navigation and relevant local interactions such as filtering, pagination, dialogs, form validation and mock CRUD where observed or requested. Keep mock changes local; label prototype and simulated actions clearly. Implement reasonable responsive behavior and keyboard-accessible controls.
- Distinguish observed behavior from inferred or simulated behavior in the notes. Do not invent unobserved business rules or imply that mock behavior is connected to the real backend. If scope is large, deliver the requested pages first and document coverage and gaps.
- Organize outputs clearly, for example `index.html`, `screenshots/`, and `docs/page-index.md`; adapt to the user's requested format. Include setup/opening instructions and a page/state coverage list.

## Verify

Open the generated prototype in a browser where available. Check navigation, representative filters, dialogs and mock edits, and verify that it works offline without calls to the original system. Compare representative views with captured evidence, including a narrow viewport when relevant. Report what was captured, what was simulated or inaccessible, and any verification that could not be performed.
