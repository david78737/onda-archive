# Nile Tile CRUD + Permissions — Scope

Written 2026-09-07. This is a planning document, not a finished spec — expect it to change once real work starts, same as the `onda-doc` skill protocol it supports.

## The problem, in one line

Today the tile system (Presentation/Help File/General Info/Article, `nile-tile-create` → Station Dashboard) can only **Create**. There's no way to view a single tile's full record, fix a mistake, replace a screenshot, or delete a tile — and it's not yet confirmed that "who can see/change what" is checked correctly everywhere it needs to be.

## What already exists (verified in the code)

- **Create** — `POST {api:onda-nile}/nile/tile/create`, via `nile-tile-create/index.html`, writes to the `nile_presentations` table. Works, and as of tonight (2026-09-07) is actually complete: a real bug was found and fixed live in Xano — `synopsis`, `who`, `brief`, `takeaways`, `deck_url`, `youtube`, `event_code` were valid columns on the table that this endpoint simply never wrote to (not declared as inputs at all), so every tile created before tonight is missing that content. Also, `headings` didn't exist as a column anywhere — added tonight (json, same shape as `takeaways`). Both are now declared inputs and wired into the insert step. One already-created tile (id 142, "Creating a Help file") was patched by hand via a one-off Xano maintenance function; anything created before that fix and not manually patched is still missing this content.
- **List** — `GET {api:onda-nile}/nile/station/tiles?station_id=...&phone=...&magic_auth_token=...`, via `nile-admin/dashboard.html`. **The `station_id` vs `org_l1/l2/l3` question is resolved, not a real conflict.** Reading Create's actual function stack: it takes `org_l1/l2/l3` as input, then looks up *both* an `org_id` (step 4) and a `station_id` (step 4b, via an "identity" lookup row) and stores both on the record. So `org_l1/l2/l3` is just the human/URL-facing address; `station_id` is the resolved internal id already sitting on every tile. Update/Delete should follow the same resolution pattern, or simply operate on a tile's own `id` and check its stored `station_id` against the caller's resolved identity.
- **A new field worth knowing about before building Update: `is_visible` (boolean).** Confirmed via direct Xano inspection — every tile has this, separate from `visibility` (which is audience: public/station/private). Every tile so far has `is_visible: false`. No endpoint anywhere sets it to `true`. This is almost certainly the real "is this actually published" switch that the earlier "no publish control found anywhere" gap (below, and in the `onda-doc` skill) was pointing at. Fold this into Update rather than building a separate publish endpoint.
- **A server-side auth check appears to exist for List** — the dashboard's fetch explicitly handles a "Not authorized for this station" error from the server. This is good news (it suggests Xano already does *some* check, not zero), but from the static files alone I can't see what that check actually verifies (association only? a specific role? just that the token is valid at all?). This needs verifying directly in Xano, which is outside what I can inspect from this repo.
- **`nile/presenter/my-stations`** — an existing endpoint (referenced in the `onda-doc` skill's lessons-learned) that returns a presenter's real, established station relationships. Likely the right building block for "what am I actually allowed to touch," rather than inventing a new mechanism.
- **Dashboard is view/filter only** — no edit or delete affordance on any tile card.
- **No content-type page (`nile-tile-create`) has an edit mode** — no `id`/`tile_id` param handling, no pre-fill, no PATCH call.
- Two other editors exist in this repo but are **not** this system: `nile-update` (a presenter's own session card, older/different data model) and `nile-presentation` (the separate, paused `api:presentations` system). Neither should be extended for this — confirmed while investigating this exact question this week.

## What needs to be built

### 1. Read (single record) — DONE, 2026-09-07
`GET {api:onda-nile}/nile/tile/detail?id=...` (query param, not path param — renamed from an original `{id}` path version after a persistent, never-fully-explained Xano publish conflict; the working one was kept and renamed rather than the mystery chased further). Verified live against a real record.

### 2. Update — DONE, 2026-09-07
`POST {api:onda-nile}/nile/tile/update`, matching the codebase's existing convention (`nile/card/update`, `nile/station/profile` are both POST-with-an-id, not PATCH). Accepts the same fields as Create, plus `is_visible` and `status` — solving "publish" as part of Update rather than a separate endpoint, as planned. Only fields actually included in the request get changed; everything else is left alone. `org_l1/l2/l3` cannot be changed via this endpoint. Verified live.
**Still to build:** the UI side — give `nile-tile-create` an edit mode (`?tile_id=...`, pre-fill every field, "Save Changes" instead of "Submit," call update instead of create). Reuses ~90% of the existing form.

### 3. Delete — DONE, 2026-09-07
`POST {api:onda-nile}/nile/tile/delete`. Soft delete, per your call: sets `status` to `archived` rather than removing the row — recoverable, and matches the "Archived" filter the Dashboard already has. Verified live.
**Still to build:** a Delete action on each Dashboard card, with a confirm step before it fires.

### A real security gap found and fixed along the way
Building Read surfaced two genuine bugs in the authorization logic shared by all of these (and by the pre-existing `/nile/station/tiles`): the token check was being **skipped entirely** whenever no presenter record matched the given phone (letting a coordinator-table entry bypass token verification altogether), and a `null` token expiry was being treated as "never expires." Both fixed at the source, so List, Read, Update, and Delete all inherit the fix. Verified live: an authorized call now round-trips correctly, and a token must have a real, unexpired `magic_auth_token_expiry` to pass. (Not yet verified: that an *actually* expired token gets rejected end-to-end — the positive path is proven, the negative path wasn't chased down given how much time the debug tooling itself cost tonight.)

### 4. Wiring the Dashboard to Read/Update/Delete
Each tile card on `dashboard.html` gets an "Edit" link (→ `nile-tile-create?tile_id=...` in edit mode) and a "Delete" action, alongside the existing "Open →". Currently "Open →" only appears when the tile has a linked `.onda` file — Edit/Delete should appear regardless.

### 5. Permissions — the part that needs your call, not just building
Two separate questions, easy to conflate:

- **Association** — is this person legitimately connected to this station at all? Likely already partially solved via `my-stations` / the server's existing "Not authorized" check on List. Update and Delete need the *same* check applied — right now there's no evidence they'd get it automatically just because List has it, since they don't exist yet.
- **Role within a station** — is "associated with the station" the only tier that matters, or do different people at the same station need different rights (e.g., anyone can propose a tile, but only a Curator can edit or delete someone else's)? **This is a product decision, not a technical one — I'm not picking it for you.** See Open Questions.

## Suggested build order

1. ~~Read + Update + Delete endpoints~~ — **done, 2026-09-07.** All three live and verified, plus a real auth bug (token check skippable, null expiry treated as valid) found and fixed at the source. Remaining: the edit-mode UI on `nile-tile-create`, and Edit/Delete buttons on the Dashboard — see items 2–3 above.
2. Once real usage shows whether "associated or not" is actually enough, add role granularity only if it's actually needed — don't build a permissions system for a problem that hasn't shown up yet. (Turns out there already IS a real role check — curator/coordinator via `nile_org_coordinators` — not just bare association, so this may already be settled; see Open Question 2.)
3. ~~Reconcile `station_id` vs `org_l1/l2/l3` before step 1~~ — **done, see above.** Not a real conflict; `org_l1/l2/l3` resolves to `station_id` server-side already.

## Open questions for you, not decided here

1. **Delete: hard delete, or soft (archive)?** Soft is safer (recoverable, matches the "Archived" status the dashboard filter already has a slot for) and is my instinct, but it's your call.
2. **Roles: binary association, or graduated (e.g. Curator vs Contributor) within one station?** Affects how much of this is worth building now vs. later.
3. **Who can delete a tile someone else submitted?** Only them, any curator of that station, or only you?
4. ~~Xano-side work: live together, or drafted for you to paste in?~~ — **settled:** live, via a Xano AI Agent prompt relay (David runs it in Xano's own AI, pastes results back). Already working well tonight for the Create fix — same pattern for Update/Delete.

## Related
- `.claude/skills/onda-doc/SKILL.md` (onda-replay) — the create-side protocol this CRUD work completes.
- `HELP_FILES_STAGES.md` (this folder) — the full staged roadmap this scope doc is one part of.
- Claude memory: `project_onda_doc_workflow` — logs the three-system landscape (in-app help / paused presentations migration / this tile system) this all lives in.
