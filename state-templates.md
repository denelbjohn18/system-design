# State protocol, schema 1

State exists only at the explicitly selected workspace root/.system-design. Never search parents. Multi-root requires selecting one root. Legacy Markdown-only state is not automatically accepted or migrated. Keep legacy files untouched, ask whether to use a new study folder or explicitly review evidence for a future migration. No scores carry over by guessing.

## Canonical and readable files
- state.json: authoritative, schema_version 1, curriculum_version 2026-10-06.1, workspace_root, revision, learner_id, mode, profile, checkpoint, concepts.
- profile.md, curriculum.md, progress.md: derived readable views, never edited for authoritative scores.
- backups/revision-N.json: previous canonical revision before each write.
- .write-lock/owner.json: current writer. An existing lock blocks another writer. Never delete a lock automatically or steal a stale lock.

Use scripts/state.py, Python standard library only. It refuses unsafe roots/symlinked state, validates schema/objective coverage and rejects stale revisions. Atomic replacement protects the canonical JSON. Multiple readable files cannot be updated atomically together; a crash can leave stale views, repaired from canonical JSON. No claim that a network/cloud-synced filesystem provides local-disk locking guarantees. Use one active chat per study workspace.

## Calls
Determine the helper's absolute path from this plugin, not the workspace. Quote paths. Run only this local helper with explicit workspace root. Send JSON through quoted stdin, never interpolated prose in shell arguments.

```sh
python3 /absolute/plugin/scripts/state.py init --root /absolute/study/root <<'JSON'
{"available_minutes":60,"onboarding_complete":false}
JSON
python3 /absolute/plugin/scripts/state.py show --root /absolute/study/root
python3 /absolute/plugin/scripts/state.py next --root /absolute/study/root
```

For updates, use apply with a JSON request on stdin. Read the latest revision first; do not reuse a revision after any successful write.

- profile: expected_revision, action="profile", value object with observed onboarding answers.
- checkpoint: expected_revision, action="checkpoint", value object with stage, concept_id, next_opener and unresolved question.
- mode: expected_revision, action="mode", value="active" or "paused".
- attempt: expected_revision, action="attempt", concept_id, result, at (actual ISO timestamp with offset), evidence.

Attempt result is assisted, miss, independent, overview or defer. Evidence needs learner_quote and probe. Independent additionally needs hint_used=false, fresh_scenario=true and rubric exactly matching applicable dimensions in objectives.json, all 2. The helper verifies the shape, not the truth of the teacher's assessment.

Never fabricate timestamps. Obtain current system time with timezone. Early independent practice before the due instant, or under 24 hours, neither advances the review interval nor postpones due recall. Initial independent pass: provisional, review in 24 hours. Later independent recall at/after its scheduled due instant and at least 24 hours after the previous independent anchor: retained, then intervals 3, 7, 14, 30 days, saturated at 30. Miss/assisted: assisted, streak cleared, repair due in 24 hours. Overview only for optional objectives; no mastery claim. Defer excludes an item from automatic selection until the learner explicitly returns to it.

Selection: due items oldest due timestamp first, assisted first only on a due-time tie, then stable ID. Maximum three due items per session; default one, offer to use the remaining budget. Next new item is first unseen or assisted in fixed order. Provisional/retained/overview/deferred items do not block progression. Assisted items get repair, not an endless gate; defer if today's bounded attempts are exhausted.

## Error and recovery
Nonzero exit or stderr error means not confirmed saved. Report that, preserve current files, and give an unsaved summary. Revision conflict: reread latest, reconcile evidence and ask before losing either session's changes. Do not repeatedly retry or overwrite.

repair-views uses canonical state to regenerate missing/stale readable views with a normal locked revision. It refuses symlinked/non-file targets. Offer this only after explaining what changed; it never replaces malformed canonical JSON. Keep malformed JSON and backups intact; user review is required to restore a particular backup. Legacy schema/mismatched root errors stop writes, not learning: use an explicitly chosen fresh workspace if the learner wishes.

Bound canonical state at 2 MB. Readable progress shows recent 20 attempts; older evidence remains in JSON/backups. Do not load all history by default. The helper currently stops writes at the bound; no automatic deletion/archive. Backups grow with writes and need a reviewed retention/archive policy. No secrets or private company examples in state; Cursor reads this state into model context. Offer to keep .system-design out of Git with permission.

resume-concept action takes expected_revision and concept_id; use only when the learner explicitly returns to a deferred item. It restores unseen/assisted scheduling without granting a score.
