---
name: flyin-ui-implementation
description: Build the Fly-In React visualization incrementally
version: 1.0.0
metadata:
  hermes:
    category: web-development
    tags: [fly-in, react, typescript, visualization]
    requires_toolsets: [terminal]
---

# Fly-In UI implementation

## When to use

Use in the UI milestone for React/TypeScript, graph SVG, playback, API/SSE consumption,
accessibility, or frontend tests.

## Preconditions

Read `frontend/AGENTS.md` and `docs/project/07_UI_PLAN.md`. Verify a tested backend response
contract exists. If absent, work on a deliberately hard-coded projection spike only with explicit
approval and delete/replace it when integrating.

## Procedure

1. Choose one visible user behavior.
2. Define server state, projection state, and local UI state separately.
3. Check native SVG/CSS/HTML and installed dependencies before adding one.
4. Add the smallest strict TypeScript component/transformation.
5. Test the pure reducer/transform or critical interaction.
6. Verify loading, error, keyboard/text alternative, contrast/reduced-motion implications.
7. Confirm no authoritative routing/scheduling logic moved into React.
8. Review diff with Ponytail and update progress/teaching notes.

## Slice order

Hard-coded response -> REST completed result -> input/errors -> graph -> turn playback -> capacity
details -> controls -> SSE/reconnect -> polish.

## Reject by default

Global state library, UI kit, graph algorithm library, WebSocket, complex animation dependency,
frontend route calculation, broad snapshots, and speculative responsive component systems.

## Verification

Compare one rendered turn/projection with the backend schedule/events. Critical controls work by
keyboard and errors preserve useful backend details.
