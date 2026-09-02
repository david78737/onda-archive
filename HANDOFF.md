# ONDA Nile / onda-archive — Agent Handoff Document

**Last updated:** 2026-09-02
**Repo:** https://github.com/david78737/onda-archive
**Live site:** https://david78737.github.io/onda-archive/

This document is the single source of truth for any agent (Mac Claude, PC Claude,
iOS Claude, or a future instance) working on this repo. Read it before touching
anything. Update it when you make a significant change.

**Note on this rewrite:** the previous version of this file was a byte-for-byte
copy of `pca-archive/HANDOFF.md` — it described a different, sibling repo and
never mentioned anything built in `onda-archive` itself (ONDA Nile, the curator
tools, or any of the `docs/` pages). It was likely used as a starting template
when this repo was created and never customized. This version replaces it with
what's actually in this repo as of 2026-08-02.

---

## Repo Relationship Map — read this first

There are **three separate repos** in play. Mixing them up is the single easiest
mistake to make here:

| Repo | What it is | Live site |
|------|-----------|-----------|
| `onda-replay` | The Flutter iOS/Android app | (TestFlight / Play Console, not a website) |
| `pca-archive` | Standalone ProductCamp Austin session archive — PCA28–PCA34, SQLite+FTS5 search | https://david78737.github.io/pca-archive/ |
| `onda-archive` (this repo) | Started as the Elevate Summit 2026 archive, has grown into **ONDA Nile** — a multi-organization curator/discovery platform. Also hosts legacy static copies of the PCA28–34 pages. | https://david78737.github.io/onda-archive/ |

**`onda-archive` depends on `pca-archive` being cloned as a sibling directory.**
`build_ondanile.js` reads `../pca-archive/sessions.json` by relative path to merge
PCA sessions into the unified ONDA Nile dataset. If you only clone `onda-archive`,
that build script will fail. Clone both, side by side:

```
~/Developer/onda-replay
~/Developer/onda-archive
~/Developer/pca-archive
```

---

## What This Repo Is

A static GitHub Pages site with two layers:

1. **The original layer** — `sessions.json` (top-level) holds **Elevate Summit 2026**
   session data only (17 sessions as of this writing), built into `archive.db` via
   `build_node20.js`, browsable at `/elevate2026/`. The `pca28`–`pca34` directories
   are legacy static per-event pages, kept for direct links (not the live PCA
   archive — that's the separate `pca-archive` repo).

2. **ONDA Nile** — a multi-org curator/discovery layer built on top, at `/ondanile/`.
   Organizations ("curators") claim a station, manage their own session catalog,
   and their content is browsable/searchable in one unified place alongside other
   orgs' content. This is the actively developed part of the repo — see commit
   history, nearly all recent commits are Nile features.

---

## Repository Structure

```
onda-archive/
├── index.html              ← Hub landing page, links to Elevate Summit + Nile tools
├── sessions.json            ← Elevate Summit 2026 session data ONLY (not PCA)
├── archive.db                ← Generated from sessions.json via build_node20.js
├── build.js                  ← Original build script (Node 24+, node:sqlite, FTS5) — likely a leftover copy from pca-archive, verify before relying on it
├── build_node20.js           ← Actual build script used here (sql.js, no FTS5 — search is client-side)
├── build_ondanile.js         ← Merges THIS repo's sessions.json + ../pca-archive/sessions.json → ondanile/sessions.json
├── patch_levels.js           ← (purpose not yet documented — check before use)
├── elevate2026/               ← Elevate Summit 2026 static archive page
├── pca28/ … pca34/            ← Legacy static PCA pages (copies, not the canonical PCA archive)
├── chapter/                   ← Generic chapter/org archive template (ONDA Archive branding)
├── ondanile/                  ← ONDA Nile browse page — the unified cross-org discovery UI
│   └── sessions.json          ← Generated output of build_ondanile.js — do not hand-edit
├── nile-admin/                ← ONDA Nile's live admin/curator/presenter tool suite — see table below, this is where nearly all current work happens
├── nile-brand/                ← "Your Archive Identity" — org branding/logo/identity form
├── nile-claim/                ← Claim Your Session — presenter claims a session slot
├── nile-profile-edit/         ← Edit Profile
├── nile-schedule/              ← Upcoming event submission form (generates a QR code on success)
├── nile-session/               ← Session tile editor (photo picker, Save / Save & Close)
├── nile-session-update/       ← Presenter-facing "update your session" form
├── nile-tile-create/           ← Propose a Presentation — a presenter submits a talk (writes to `/nile/tile/create`; suspected still writing to the legacy `nile_tiles` table — see Known Gaps)
├── nile-update/                ← Presenter profile edit (magic-link identity flow)
├── docs/                       ← Marketing/spec/handoff HTML pages (see below)
├── img/, img_summit/, assets/  ← Images — img_summit is Elevate Summit speaker headshots
├── .nojekyll                   ← Disables Jekyll processing on GitHub Pages
└── HANDOFF.md                  ← This file
```

### `nile-admin/` page purposes (as of 2026-09-02)

This folder is the actual live control surface for ONDA Nile — event admins, curators,
and contributors all operate through these pages. There is no single entry point;
each page is reached by whoever built/tested it linking directly to it. This is the
biggest documentation gap in the repo and the reason this table exists.

| File | Title | Purpose |
|------|-------|---------|
| `login.html` | ONDA Nile — Sign In | **The single entry point (built 2026-09-02).** Phone OTP once → merges `/nile/coordinator/orgs` (curator/coordinator) + `/nile/presenter/my-stations` (contributor) into one list, one card per org, all applicable action buttons on each. Hub-and-spoke: sign in once here, then every other page below is a pure spoke reached with `?phone=&token=` already in the URL. |
| `index.html` | Event Admin — ONDA Nile | Older, separate "Create Session Slots" page — has its own standalone OTP with no token-passthrough, not yet folded into the hub. **Known gap**, not fixed 2026-09-02. |
| `event.html` | Create Event — ONDA Nile | Curator creates a new event/session slot. Spoke — redirects to `login.html` if visited without `?phone=&token=`. |
| `apply.html` | Apply to Present — ONDA Nile | **Self-service, no sign-in.** A brand-new candidate (no existing record) applies to present: phone OTP + name/LinkedIn/bio/talk info in one flow. Built 2026-08-31/09-01 to close the "catch-22" where only a curator could add a new person. |
| `cards.html` | Card Review — ONDA Nile | Curator reviews pending applications/cards — Admit/Reject + the older Approve/Return publish-review flow. Spoke — redirects to `login.html` if visited cold. |
| `register.html` | ONDA Nile Admin | Org-creation wizard ("Register a New Station"). Own OTP retired 2026-09-02 — now redirects to `login.html` if visited without `?phone=&token=`; the hub links here with `&action=new` to jump straight to the create-org screen. |
| `signin.html` | (redirect stub) | **Retired 2026-09-02** — its contributor picker was fully absorbed into `login.html`. Now just a redirect, kept so old bookmarks/links don't break. |
| `chapter.html` | ONDA Archive · Admin | Older admin page; auth resolves via `POST /nile/me` — a separate identity/org lookup, still its own standalone sign-in. **Known gap**, not folded into the hub 2026-09-02. |
| `station.html` | Station Profile — ONDA Nile | Edit a station/org's public profile. Own OTP had a real bug (sent `{phone,token}` instead of `{contact,code}` — fixed 2026-09-02) and now redirects to `login.html` if visited cold. Also had hardcoded ProductCamp/Arturo placeholder values, replaced with generic examples same day. |
| `enroll.html` | Contributor Enrollment | Curator/coordinator manually enrolls a new contributor. Had no token-passthrough at all until 2026-09-02 — added, now a proper spoke. |
| `bulk-upload.html` | Bulk Upload — ONDA Nile | Bulk session/file upload tool. Spoke — redirects to `login.html` if visited cold. |

**Sprawl resolved 2026-09-02:** three separate pages (`register.html`, `signin.html`,
`chapter.html`) used to each independently re-implement "look up which org(s)/role(s)
this phone belongs to." `login.html` is now the one canonical picker, merging curator
and contributor roles into a single list. `register.html` and `signin.html` are pure
spokes/redirects now. `chapter.html` and `index.html` were **not** folded in — both
still have their own standalone OTP with no token-passthrough support. Confirmed
separately: `nile_roles` (a table clearly meant for exactly this — org+role per
person) is dormant/unused by any endpoint; `login.html` reads the same two live
tables (`nile_org_coordinators`, `nile_presenter_orgs`) the old pages did.

### `docs/` page purposes

| File | Title / Purpose |
|------|------------------|
| `whats-new.html` | "What's New — ONDA Replay" — Aug 2026 tester update summary (tiers, features, ONDA Nile) |
| `curator-stories.html` | "Three Ways to Use ONDA Nile as a Curator" |
| `membership-tiers.html` | "ONDA Replay — Membership Tiers" |
| `channel-partner-it.html` | "The IT Channel Partner Model" |
| `onda-doc.html` / `onda-doc-demo.html` | "ONDA Doc — Living Help Documentation" concept + demo |
| `prakash-brief.html` | "Users Deserve Better Than This" |
| `working-documents.html` | "ONDA Working Documents" index |
| `xano-eli5-script.html` | "Xano + Codex — Plain Language Script" |

---

## Build System

Three build scripts exist; they are **not interchangeable**:

- **`build_node20.js`** — the one actually used for this repo's own `sessions.json`
  (Elevate Summit) → `archive.db`. Uses `sql.js` (pure JS, no native deps). No FTS5 —
  search is handled client-side in `index.html`/`elevate2026/index.html`.
  ```bash
  node build_node20.js
  ```
- **`build.js`** — Node 24+ / built-in `node:sqlite` / FTS5 version. This matches
  `pca-archive`'s build script exactly and was likely copied over at the same time
  as the old HANDOFF.md. Verify which one `index.html` actually expects before
  assuming this is live/current here. (This Mac has Node 24.14.1, so it *would* run.)
- **`build_ondanile.js`** — merges `sessions.json` (this repo, Elevate) +
  `../pca-archive/sessions.json` (sibling repo, PCA) into `ondanile/sessions.json`,
  the dataset the ONDA Nile browse page reads. Requires `pca-archive` cloned as a
  sibling directory. Re-run this any time either source `sessions.json` changes.
  ```bash
  node build_ondanile.js
  ```

Always commit the regenerated output (`archive.db` and/or `ondanile/sessions.json`)
after running a build script — the browser fetches these directly, nothing is
built server-side.

---

## Xano Backend

Workspace `xrxm-29on-xlyt` (same workspace referenced elsewhere in `onda-replay`'s
memory/docs — this is David's personal/template Xano workspace).

**Known inconsistency, unresolved as of 2026-08-02:** the API base URL is not
consistent across pages. Some reference `api:onda-nile`, at least one references
`api:nile` (per commit `8f97381 Fix API base URL: onda-nile → nile`, which
apparently wasn't applied everywhere):

```
https://xrxm-29on-xlyt.n7e.xano.io/api:onda-nile      (most pages)
https://xrxm-29on-xlyt.n7e.xano.io/api:nile           (at least one page)
```

If you hit a mysterious 404 on a Nile form, check which `NILE_API` / `NILE_API2`
constant that specific page uses before assuming the backend is down.

Auth pattern across the nile-* forms: phone number → OTP → `magic_auth_token`.
Several early commits show this token-extraction logic being debugged repeatedly
(profile_url query param parsing, Bearer header vs. body placement) — if a form's
auth breaks again, check `magic_auth_token` handling first, it's been fragile.

---

## Known Gaps / Open Items

- **Sign-in/org-picker sprawl** — see `nile-admin/` table above. Three pages, three
  endpoints, one concept. Needs consolidation before adding anything new that
  touches "which org/role am I."
- `build.js` vs `build_node20.js` — unclear which is authoritative for this repo's
  own `sessions.json`; `build.js` looks like a leftover copy from `pca-archive`.
- Xano API base URL inconsistency (`onda-nile` vs `nile`) — not yet fully fixed.
- `patch_levels.js` — purpose undocumented, check contents before use.
- No `CNAME` file — site serves at the default `david78737.github.io/onda-archive/`
  path, not a custom domain.
- See [[project_onda_visual_bundle_idea]] and [[project_youtube_upside_down_model_critique]]
  in `onda-replay`'s Claude memory for active product-direction threads that will
  likely touch this repo (embedded visuals in `.onda` bundles; ONDA Nile as a
  YouTube-alternative consumption format for talking-head/instructional content).

---

## Agent Coordination Notes

This repo is worked on by multiple Claude instances across different machines:

| Agent | Machine | Role |
|-------|---------|------|
| PC Claude | Windows / VS Code | Primary driver of ONDA Nile feature work (nearly all recent commits) |
| Mac Claude | miniMac | iOS TestFlight builds (`onda-replay`), archive/capture pipeline work, now also this repo |

**As of 2026-08-02: David's PC is going in for hardware repair.** Mac Claude
(miniMac, via VS Code + Claude Code extension) is the primary interface for the
duration. When PC Claude comes back online, it should `git pull` on all three
repos (`onda-replay`, `onda-archive`, `pca-archive`) and read this file before
resuming work — anything Mac Claude does in the meantime will be here or in commit
history, not in PC Claude's own memory (Claude's memory is local per-machine, not
synced — see `onda-replay`'s CLAUDE.md and memory notes for why).

**Before making changes:** `git pull` on whichever repo(s) you're touching —
multiple agents push to these.

**After making changes:** commit immediately. Do not hold uncommitted work across
sessions — this pattern has caused lost work before (the miniMac has crashed with
in-memory work lost).

**Commit-first protocol (from PC Claude, 2026-06-08, originally written for
`pca-archive` but applies here too):** any list, mapping, or dataset that required
effort to compile must be committed the moment it exists — YouTube URL lists,
session-to-filename mappings, intermediate data files.

---

## Session Count Reference (this repo's own data, not PCA)

Elevate Summit 2026: 17 sessions (grew from 13 at initial commit — check
`sessions.json` for current count, this will keep changing).
