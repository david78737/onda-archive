# Curator Content Intake Protocol

First run: 2026-09-08, David acting as Curator, ingesting Matthew Castle's episode (via Gerette Buglion's "Living Cult Free" podcast) into ONDA Replay/Nile — the first time this has ever been done manually, end to end. This document exists because it's meant to be repeatable: this is what Robin Robeson does every time she takes an article from a contributor, and what Gerette would do herself if she becomes a Curator.

## Task inventory

| # | Task | Depends on | Owner today | Effort | Blocking? |
|---|------|-----------|-------------|--------|-----------|
| 1 | Get the raw file from the contributor (MP3, Drive link, etc.) | — | Curator | minutes | yes |
| 2 | Get the file onto a device running a **signed** Replay build (App Store or TestFlight — not an ad-hoc local build) | 1 | Curator | minutes | yes |
| 3 | Utilities → Import Recording | 2 | Curator (tap) | seconds | yes |
| 4 | Transcribe | 3 | App/Xano (Whisper) | minutes, scales with audio length | yes |
| 5 | Set sleeve (cover) + label in-app | 4 | Curator | **unconfirmed** — not actually exercised tonight, only discussed | no |
| 6 | Export the real `.onda` file as an actual saved file on disk (**not** Share Bundle's share link — that link expires and is the wrong thing to use here, see below) | 4 | Curator (tap) | seconds | yes |
| 7 | Draft the Nile tile metadata (title, synopsis, audience, tags, headings) | 4 (needs the transcript) | **Claude/agent** — done by hand tonight, see below | minutes | no, but currently manual |
| 8 | Submit the tile (`nile/tile/create`) — returns `id` **and** a `session_token`, which doubles as the proxy needed for step 9 | 7 | Curator relays a Xano AI prompt, or fills the web form | minutes | yes |
| 9 | Attach the real file: `nile/presenter/session/complete`, with `proxy` = the `session_token` from step 8 and the real file from step 6. **Must be run in Xano's own Run & Debug panel, not a chat-relayed prompt** — this needs a real file upload, which a text prompt can't carry. This replaces the empty placeholder `onda_file` and finalizes the permanent `onda_url`. | 6, 8 | Curator, in Xano's UI directly | minutes | yes |
| 10 | Publish it (`nile/tile/update`: `status: published`, `is_visible: true`) | 9 | Curator relays a Xano AI prompt | minutes | yes |
| 11 | Verify it's live (`nile/tile/detail` or the `chapter/` link) | 10 | Curator/Claude | minutes | no |
| 12 | Send the link to the contributor | 11 | Curator | seconds | no |

### Why not Share Bundle's link for step 6
Share Bundle produces a share-and-forget link (`last_share_url` / `share_url_expires_at`) — the same expiring-link mechanism already documented (in Claude memory, `project_proxy_recording_pipeline`) as having caused real, already-happened damage to older PCA/Elevate archive content when links expired with no backup. A permanent tile needs the real file attached via step 9, not a link that can silently die later.

### What "Send with a Message" actually looks like (real example, 2026-09-09)
Documented from a real Android run, episode "s4 taking a cult to court" (tags `lcf`, `gerette`, Music/audio-only toggle available in the same modal): tapping Share → Send with a Message opens a modal with an editable message body pre-filled with the session title, then Share hands it to the OS share sheet. The result lands wherever you sent it (tested via email) as a short proxy link: `https://bey.ondareplay.com/{code}`. This confirms the proxy-link format and that it's the `onda_share_links` path described above — casual/personal, not a tile.

### Automation opportunity this exposes
At the moment `onda_share/upload` receives a file, Xano already has the audio **and** the transcript (embedded in the .onda). Right now nothing reads that transcript until a Curator manually drafts tile metadata later (step 7). The real opportunity: have Xano consume the transcript at upload time and auto-draft a synopsis, closing step 7's gap the same way step 4 (transcription) already runs unattended.

**Resolved design (2026-09-09):** don't merge `onda_share_links` and `nile_presentations` into one table, and don't auto-fire on every share — that would flood the archive table with one-off personal sends that were never meant to be curated content. Instead: add a second toggle to the existing "Send with a Message" modal (alongside "Music/audio-only"), labeled **"+ Sessions"**, visible **only to Contributor and Curator roles** (not Listener — matches the existing rule that publish control belongs to the Curator/Presenter, per `project_publication_control_protocol`). Checked at send time: the share still goes out exactly as today, but Xano also creates the `nile_presentations` row right then — status `pending`, real file attached, synopsis drafted from the embedded transcript. Unchecked: behaves exactly as it does today, no LLM cost incurred. This makes the decision at the one moment the sender already knows their own intent, instead of a separate review queue or an always-on trigger.

Still open: exact modal layout (a second toggle may need the modal widened / padding reduced to avoid crowding) — a real implementation detail, not decided yet. And the status-enum check (is `pending` already a valid `nile_presentations.status` value, or does it need to be added) is still pending verification in Xano.

## Critical path

Steps 1→2→3→4→6→8→9→10→11→12 is the real chain — nothing downstream can start until the step before it finishes. Step 5 (sleeve/cover) and step 7 (metadata drafting) can happen in parallel with other steps, not in series.

**The actual bottleneck tonight wasn't any of these steps — it was discovering that ad-hoc local `flutter build macos --release` builds have a real, unresolved AppKit lifecycle bug that a properly signed build (TestFlight) doesn't have.** That cost the majority of tonight's time and has nothing to do with the protocol itself. Flagging this prominently so it isn't rediscovered: **always use a signed build (App Store or TestFlight) for real work, never an ad-hoc local desktop build.**

Secondary, smaller bottleneck: on an Android **emulator** specifically, a file dropped via drag-and-drop doesn't show up in the system file picker until Android's MediaStore indexes it — a real device doesn't have this lag. Emulator-only quirk, not a protocol problem.

## A real cost worth naming

Step 4 (transcription) draws on the **Curator's own** subscription tank, not the original contributor's. A Curator ingesting someone else's raw file is spending their own transcription minutes to do it. Worth knowing before this becomes routine — it's a real input cost to curating, not a free action.

## Where to automate — the actual opportunity

**The one thing that stays permanently human, on principle, not just for now: review.** Every session gets reviewed by a Curator before it goes live on Replay or Nile — that review is the actual job, the real value curation adds. No amount of automating the mechanics below changes that.

**Step 7's mechanics, on the other hand, are a today's-tooling limitation, not a permanent line.** Tonight it was done by Claude, live, in a Claude Code session, reading the pasted transcript and drafting the metadata by hand in the conversation. That proved the *content* is good — it did not prove a scalable *mechanism*. A Claude Code session is a general-purpose assistant sitting in front of one computer, not part of the actual product. The better long-term home is server-side, in Xano: step 4 already proves the pattern (transcription already works by Xano calling an external AI model directly, no human relay involved) — step 7 should work the same way, a Xano function triggered right after transcription that calls an LLM directly and writes the synopsis/who/tags/headings onto the record, running identically for every Curator without anyone needing a session open. Not built yet — this is the recommendation.

**Step 9 (attaching the real file) is manual today for a similar, non-permanent reason** — no chat-relayed AI prompt, Xano's or Claude's, can carry a binary file upload right now. That's a real constraint today, worth building real automation for once volume actually justifies it (per David, 2026-09-08) — not a philosophical line the way review is. Don't confuse the two: review must always be human; loading the file just currently has to be.

## Open, unconfirmed

Step 5 (sleeve + cover art, in-app) was discussed but never actually walked through tonight — don't assume it's simple until it's actually been done once.

## Related
- `HELP_FILES_STAGES.md`, `CRUD_SCOPE.md` (this folder) — the CRUD infrastructure this protocol runs on.
- `onda-replay/.claude/skills/onda-doc/SKILL.md` — the sibling protocol this one's `nile-intake` recommendation is modeled on.
- Claude memory: `project_content_lifecycle_access_model` — the Curator/Contributor/Listener model this protocol is the first real instance of.
