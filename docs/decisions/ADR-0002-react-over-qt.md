# ADR-0002: Prefer React over Qt for the final GUI

- Status: Superseded by ADR-0007
- Date: 2026-07-10
- Superseded: 2026-08-12

## Context

Both can satisfy graphical visualization. A key additional objective is teaching APIs and
event-driven client/server communication.

## Decision

The original decision selected React + TypeScript after the FastAPI contract existed and retained Qt
as a fallback if schedule or packaging constraints materially changed.

## Why it was superseded

The implemented API evolved into a deliberately synchronous request/response boundary before events.
The first real browser consumer therefore does not need React, TypeScript, Vite, a separate frontend
dev server, or CORS. ADR-0007 replaces this React-first choice with native HTML, CSS, JavaScript,
`fetch()` and browser-native SVG until measured UI complexity justifies a framework.

## Alternatives considered

- PySide/Qt: fewer languages and easier direct Python integration, but an HTTP boundary would be
  more artificial.
- Terminal-only: mandatory-compatible but misses the desired final GUI/API learning outcome.

## Historical consequence

React remained a useful target design while the API/event architecture was hypothetical. Once the
synchronous API became real, keeping the framework choice without a demonstrated need would have
added toolchain work that obscures the simpler REST learning path.
