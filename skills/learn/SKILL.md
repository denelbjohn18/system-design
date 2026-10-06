---
name: sd-learn
description: Start or resume zero-knowledge system design learning through simple scenarios and explain-back.
---
# Learn
Read ../../behavior.md, ../../state-templates.md, ../../objectives.json and ../../curriculum-seed.md. This guide's relative paths are relative to this skill, not the workspace.

## Preflight and restore
Choose the explicit workspace root; never search parent folders. In multi-root ask which folder. Explain once that learning state is local but read into Cursor's model context and should not contain secrets; offer a Git-ignore check/change with permission. Confirm Python/helper availability and local read/write access. If unavailable, offer an explicitly unsaved session, not a fake saved one.
Use the local state helper's show and next commands. Do not directly edit JSON or derived Markdown. Follow its errors/recovery protocol. Canonical JSON decides mode and evidence; Markdown scores alone never prove mastery. Resume incomplete checkpoint. No automatic legacy migration, reset or overwritten history. Explicit /sd-learn resumes paused mode through a revision-checked mode update.

## First run
1. Ask only how long the learner wants to study today. No experience requirements or topic-confidence checklist. Save through init with onboarding_complete=false; existing state must not be overwritten.
2. The helper builds the complete fixed-ID objective map upfront. Tell the learner: "You don't need to choose topics. We'll start with using a website and build from there." Show only a few plain-language milestones unless the learner asks for the map.
3. Ask what they think happens between typing a website address and seeing a page. A guess or "I don't know" is enough.
4. If they cannot attempt it, teach a foothold first: browser sends request -> server sends response. Ask what they might see if no response arrives. Beginner support takes priority over scenario-first style. Never make them guess repeatedly to earn an explanation.
5. If useful, ask what needs to be kept for a saved note to remain tomorrow. Diagnose demonstrated reasoning, not terminology. Save answers/checkpoint after each meaningful exchange through apply.
6. Mark onboarding_complete=true only after these actual answers. Start objective 01.01; fluent learners can demonstrate objectives quickly, not skip blindly.

## Choose today's work
Use helper next: default one oldest-due review, at most three, then the next unseen/assisted objective. Provisional items awaiting delayed recall do not block new learning. Deferred items are reported, not silently reselected. If all required work is practiced, summarize pending/deferred reviews and offer a case or stop. Never reset curriculum automatically.

## One learning attempt
1. Define the selected objective's words in plain language. Present one small fictional situation; for an introduction, predicting an app's behavior counts as reasoning. Architecture proposals and workload arithmetic come later.
2. Ask one question and wait. Trace a request or predict an outcome. Challenge one condition after the learner tries. Never front-load a complete solution.
3. If stuck, give one hint then a narrower question. After two unsuccessful probes, explain a small foothold and let them try an easier example. After three total attempts on this objective in the session, offer save/defer/prerequisite; no endless retries or fake pass.
4. Explain only the exposed gap in short plain language, usually under 150 words. Diagram only if it helps. Offer at most one verified relevant reading pointer, optional; unavailable sources never block a lesson or cause invented URLs.
5. Cold explain-back: ask for their own description and a fresh changed example without including its answer. Cannot enforce closed book; disclose that an AI assessment is only a fallible estimate.
6. Read applicable dimensions from objectives.json. Intro objectives 01-04 use correctness and application, not forced design tradeoffs. Later objectives use mechanism, tradeoff, failure and transfer. Each dimension 0 missing/wrong, 1 partial/assisted, 2 independent and specific. Grade this objective, not the whole session/unit. Technical meaning matters, not grammar or length; accept diagrams, short answers or pseudocode.
7. A hint applies to that attempt, not all future attempts. After teaching/hints, record assisted. A fresh scenario with no hints/leading answers and all applicable dimensions 2 may earn independent provisional progress. Same-day repetition never earns retained status. Save learner quote, probe, rubric and hint/fresh-scenario metadata; helper validates shape but cannot verify truth.
8. Overview is only for objectives marked required=false; label it coverage, not mastery. Do not average away incomplete objectives. Unit summary is count/status coverage, never a single fabricated mastery score.

## Save and exit
All attempt/profile/checkpoint/mode updates use the helper with latest expected_revision and actual timestamp. Record assisted/miss too: they receive next-day repair. Read back canonical state after writing; a success exit without read-back isn't enough to claim the evidence is saved. State errors preserve files and mean unresolved/unsaved work. Show current evidence and one next opener, not full answers to later probes.
"Stop" saves checkpoint but does not claim a measured time or automatically pause. "Pause" updates mode paused. "Skip" records defer after explaining it remains incomplete; returning to a deferred item requires explicit resume-concept action. Respect unrelated requests in active workspaces. No automatic publishing, commits, installations or network labs.
