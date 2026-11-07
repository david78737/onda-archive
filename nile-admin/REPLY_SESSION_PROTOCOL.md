# Reply / New-Story Session Protocol (proposed — not yet built)

Status: design agreed with David 2026-11-07. Nothing in this doc is live yet.

## The problem with today's flow

When someone taps "Record it in ONDA Replay" (reply to a tile, or add a
new story) from the chapter page, here's what actually happens, verified
in code:

1. Chapter page posts `{phone, link, presenter}` to
   `api:nile/reply/invite` (Xano). `link` is a **web URL** with query
   params (`newstory=1`, org identity, phone, name) — not a native deep
   link.
2. Xano texts that link to the phone number. No OTP is generated. No
   session row is created.
3. User taps the link → lands back on the web page → the page's
   `maybeAutoRespond()` / `maybeAutoNewStory()` shows a "Continue"
   banner (iOS Safari blocks an auto-fired custom-scheme redirect that
   isn't a direct tap) → tapping it fires
   `ondareplay://newstory?org_l1=...&org_l2=...&org_l3=...&name=...&phone=...`
   (or `ondareplay://reply?tile=...&phone=...`).
4. The native app (`AppDelegate.swift` / `MainActivity.kt`) parses that
   into a pipe/colon string, hands it to Flutter, which opens
   `AnRecordSessionScreen` with those org/phone params passed in as
   **loose metadata** — not a session identity.
5. User records. On upload, `an_capture_controller.dart` tags the
   bundle with `nile_story_org_l1` (etc.) so it lands in the right
   archive location.

So the destination-tagging genuinely works today. What's missing:

- **No OTP.** The phone number is never verified. Anyone who gets the
  link can use it.
- **No pre-existing session.** Every tap of the link starts a brand-new
  blank recording. If the app crashes mid-recording, there is nothing
  to return to — the user starts over.
- **No resume.** The link always means "start fresh," never "continue
  where I left off."
- SMS wording bug (separate, flagged but not yet scoped): the invite
  text says "Reply to X's tribute" even for a plain new-story send,
  because both flows share the same Xano template.

## The agreed design

When a phone number is submitted (reply OR new-story — same mechanism,
different session content type):

1. **Xano generates the OTP and creates the session row in the same
   step.** Not two separate actions — one invite-send operation that
   produces both an auth credential and a destination to land in.
2. The session is created **empty** — org identity, presenter/tile
   link, content type (plain recording vs. Storyboard) all set, audio
   content not yet recorded.
3. The SMS link embeds (or resolves server-side to) both: the OTP and
   a reference to that specific session.
4. Tapping the link:
   - Verifies the OTP → unlocks whatever that phone number is
     authorized to interact with (same credential class as
     `login.html`/the publish gate — OTP phone already does this job
     elsewhere in the system).
   - Opens **that exact session**, not a new blank one.
5. The user records into it — either a normal recording or a
   Storyboard, same session mechanism either way.
6. **Continuous saving.** Progress persists against the session as it
   goes, so a crash mid-recording means returning to the same link and
   resuming, not losing the take and starting over.

The core shift: today the link carries *identity metadata for a new
recording*. The design calls for the link to carry *identity +
a resumable session reference* — the OTP and the session are minted
together, not identity-now/session-later.

## What this touches, if built

- **Xano (`api:nile/reply/invite` or a new endpoint)** — generate OTP +
  create session row atomically; can't be built from either local repo,
  needs Xano access.
- **SMS template** — fix the "Reply to..." wording bug for new-story
  sends while this is being touched anyway.
- **Chapter page (`onda-archive/chapter/index.html`)** — the invite
  POST and the deep-link URL construction (`openNewStoryDeepLink()`,
  `openNewStoryInviteModal()`) need to carry a session reference instead
  of (or alongside) raw org params.
- **Native deep-link parsing (`AppDelegate.swift`, `MainActivity.kt`)** —
  currently builds `newstory:<query>` / `reply:<tileId>|phone:<phone>`
  strings; would need a session-id field added to that payload.
- **Flutter app (`onda_echo_screen.dart`, `an_record_session_screen.dart`,
  `an_capture_controller.dart`)** — `AnRecordSessionScreen` currently
  always starts a fresh local session; needs a "resume session \<id\>"
  path that fetches/continues an existing server-side session instead
  of creating a new local one, plus continuous (not just on-stop) saving
  against that session.

None of this is scoped into tasks or estimated yet — this doc is the
shared understanding to build a plan from, not the plan itself.
