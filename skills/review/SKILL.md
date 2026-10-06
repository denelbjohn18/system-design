---
name: sd-review
description: Test due system design concepts through bounded cold recall and changed examples.
---
# Review
Read ../../behavior.md, ../../state-templates.md, ../../objectives.json and ../learn/SKILL.md. Use the same selected-root helper, never direct Markdown edits.
1. No state: explain no saved review exists; offer sd-learn. Corrupt/legacy state: follow recovery, do not invent a queue. A paused workspace stays paused; this explicit command permits this review without changing the saved mode. New chats remain paused afterward.
2. Use next for due_count and ordered review_ids. Default one due item, maximum three. Ask budget only if not already known. Empty queue: offer a voluntary early practice or stop. Early practice under 24 hours is not a retention promotion and cannot postpone existing recall.
3. Ask one objective-specific cold question without notes/answer. Then a fresh changed example. Use its applicable rubric, not a universal interview gate. Hints make that attempt assisted; a different later attempt can be independent if genuinely unprompted.
4. Miss/assisted attempts receive repair in 24 hours, clear retention streak and keep exact weak evidence. Independent delayed attempts use the helper's 24-hour and 1/3/7/14/30-day saturated schedule. Never calculate dates by memory or directly rewrite dates.
5. Two failed probes: explain briefly. Three total attempts on one objective today: offer defer/save/prerequisite. Do not force a huge backlog into one session or certify weak work to finish.
6. Save through apply with current revision, actual timezone timestamp, quote, probe, hint/fresh-scenario and rubric fields. Read back. Errors mean not saved; preserve history and give recovery summary.
7. Show retained vs provisional vs assisted evidence and upcoming dates. Due UTC instants can be presented in learner-local time with correct conversion. No notification service or measured session timer exists.
