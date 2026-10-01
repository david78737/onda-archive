# Help Files — Where We Are, What's Next

Living document. Update the status lines as stages move — this is meant to be read at the start of a work session to answer "what do I do right now," not a historical log.

## Architecture decision, 2026-09-30 — read this before producing anything

**Help content gets its own station.** Not a tile type mixed into the general `onda-replay` station — a dedicated **Replay Help Station**, same pattern as any other curated archive (Pat Stone Memorium, Gerette's Living Cult Free). Created 2026-10-01 ("ondareplay · austin · help").

**`ctx` now actually pre-filters, as of 2026-10-01.** `chapter.html` seeds its existing tag-filter state (the same one the Tags drawer writes to) from `?ctx=` on load — pre-scoped on arrival, full drawer still one tap away for everything else. This was a real, confirmed gap: the app's help buttons had sent `ctx=` for weeks with nothing reading it, so every tap landed on the full, unfiltered station. Fixed in `chapter/index.html`.

**Real follow-on requirement, not yet consistently done:** this only actually filters anything if each Help File is tagged with the lowercase screen name that matches its `ctx` value (e.g. a Sleeve-editor Help File needs the tag `sleeve`, since `ctx=Sleeve` lowercases to that). Tag discipline when producing each Help File, not a code problem.

**Two content tiers, not one — match the ingredient to the appetite:**
1. **The session card itself (Activity pathway)** — screenshot + control labels + what each one does in the common case. A *reminder*, not an explanation. Often enough on its own for someone who's used the screen before.
2. **The full Storyboard (Orientation)** — the real, narrated, goal-first deep dive, for when the reminder isn't enough.

**The tag/heading vocabulary rule — this is the actual authoring discipline, not a new feature:** Section Headings already let a listener jump straight to a moment in a Storyboard — that mechanism is built and working. The rule going forward: **tags on the session card and section headings in the deep-dive must use the exact same words.** Tag says "pausing," heading says "pausing" — tap the tag, land exactly there. No new code needed, just deliberate shared vocabulary between whoever writes the tags and whoever writes the headings (usually the same person, but easy to drift if not done on purpose).

**For ONDA's own help content specifically**, this is first-party, fully-hosted content (real fields on the tile, not a pointer) — there's no external site to point to, ONDA is the only source. A pointer-style tile (like the existing `Article` type: title + tags + a link to where the real thing lives elsewhere) is the right shape for a *different* case — an enterprise Curator whose real help content lives on their own site — not needed for this station.

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
