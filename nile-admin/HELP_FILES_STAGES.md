# Help Files — Where We Are, What's Next

Living document. Update the status lines as stages move — this is meant to be read at the start of a work session to answer "what do I do right now," not a historical log.

## Stage 1 — Create one Help File (content)
**Status: built and refined.** Protocol lives in `onda-replay/.claude/skills/onda-doc/SKILL.md` — screenshot, numbered callouts verified against real source code, orientation-vs-activity-pathway content choice, headings worded as answers to "where."
**Next, if anything:** none required to keep working — this stage is usable today.

## Stage 2 — Submit it to the Nile archive
**Status: built, and a real bug was just fixed tonight (2026-09-07).** The "Add a Help File" form (`nile-tile-create`) → `POST /nile/tile/create`.
- Fixed tonight: `synopsis`, `who`, `brief`, `takeaways`, `deck_url`, `youtube`, `event_code` were being silently dropped — columns existed, the endpoint just never wrote to them. Now wired up.
- Added tonight: a `headings` column didn't exist at all before tonight — now added to `nile_presentations` and wired into Create.
- Also fixed tonight: the "Best for" field couldn't be resized (now a textarea); the Photo field now relabels to "Screenshot URL" with the right hint when "Help File" is selected as content type.
**Next:** confirm the fix is actually published live (Review → Publish in Xano, if not already done), then submit one fresh real test tile to prove the fix works end to end, not just via the one-off patch already run on record id 142.

## Stage 3 — View / manage submitted tiles
**Status: server-side done, 2026-09-07; UI wiring still open.** Station Dashboard (`nile-admin/dashboard.html`) lists tiles with status/visibility filters and now shows Created/Updated dates. Read, Update, and Delete (soft, via `status: archived`) all built, published, and verified live tonight — see `CRUD_SCOPE.md` for full detail, including a real authorization bug (token check skippable, null expiry accepted) found and fixed at the source while building this.
**Next:** wire the UI — an edit mode on `nile-tile-create` (pre-fill from `nile/tile/detail`, save via `nile/tile/update`), and Edit/Delete buttons on each Dashboard card (Delete behind a confirm step).

## Stage 4 — Actually publish a tile
**Status: resolved as part of Stage 3.** The `is_visible` boolean is real and confirmed to be the actual "is this live" switch, separate from `visibility` (audience: public/station/private). It's now a settable field on the Update endpoint built in Stage 3 — no separate publish endpoint was needed.
**Next:** once the edit-mode UI exists, add a way to toggle `is_visible` there — that's the actual "Publish" action.

## Stage 5 — Permissions / who can do what
**Status: scoped, not built.** Full detail in `CRUD_SCOPE.md`. Short version: List already seems to have *some* server-side "are you authorized for this station" check; Update/Delete need the same, and there's an open question on whether "associated with the station" is enough or whether real roles (Curator vs. Contributor) are needed.
**Next:** build Stage 3's CRUD first using whatever check List already has — don't design new roles for a problem that hasn't shown up in practice yet.

## Stage 6 — The permissionless / screen-only growth engine (Ray Deck reframe, separate track)
**Status: idea captured, not started.** This is a *different tool* from Stage 1's skill — one that looks only at a live product's screen (no code access at all) to draft a first Help File as an unsolicited pitch. Full detail in Claude memory (`project_onda_doc_permissionless_gtm`). Suno was floated as a test case. Tied loosely to the Sept 19 PCA35 date but not required for it.
**Next:** not started — explicitly deferred pending whether it's worth building before or after PCA35.

## Not a Help Files stage, but competing for the same time
The App Store subscribe-button fix (sandbox purchase test → TestFlight upload) is a separate, higher-urgency thread — real revenue is blocked every day it's not done, unlike anything above. Tracked in conversation, not in this doc.

## Related files
- `onda-replay/.claude/skills/onda-doc/SKILL.md` — Stage 1 protocol
- `CRUD_SCOPE.md` (this folder) — Stages 3–5 detail
- Claude memory: `project_onda_doc`, `project_onda_doc_workflow`, `project_onda_doc_nile_distribution`, `project_onda_doc_permissionless_gtm`
