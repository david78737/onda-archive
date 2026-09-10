# Replay Subscriptions — future identity protocol (not built yet)

Direction only, worked out 2026-09-10 while designing the "+ Sessions" feature. Nothing here is built — this is a note for whenever it's picked up.

## The problem it solves

"+ Sessions" needs to know which station/Curator a submission belongs to. The app has no persistent answer to that today — it only knows a coarse "are you Contributor or Curator" flag (which gates whether the toggle shows at all), not "which specific station, which specific role." Getting that richer answer already has a mechanism — it's just wired to forget the answer the instant it's used.

## What already exists and can be reused

The "Replay for Business" screen (`an_utilities_screen.dart`, `_showBusinessPortalDialog`) already does the real work: phone number → one-time code → verify → `nile/auth/resolve`, which returns *every* station and role that phone number is authorized for (this is the same data that produces the "ONDA Nile" web dashboard's list of stations). Today, the result is used once to open a browser link (`_showContextSheet` → `_launchContext`) and then thrown away — nothing is cached locally.

## The direction

1. **Rename** "Replay for Business" → "Replay Subscriptions."
2. **Persist the chosen identity.** After a successful resolve + role pick, save the station/role locally (not just launch a browser link and forget) so the app remembers "you are currently acting as Curator of ONDA Replay" across launches — until the person deliberately re-runs this flow to change it.
3. **Turn the dead end into an invitation.** Today, a phone number that resolves to zero stations shows "No roles found for your number. Contact your ONDA administrator." — a dead end. Someone curious enough to try this with no existing role should instead be invited to subscribe as a Contributor or Curator, not turned away.
4. **"+ Sessions" becomes the natural trigger for setup.** If someone taps "+ Sessions" and no station identity has been established yet (step 2 never completed), it should redirect into the Replay Subscriptions flow first, rather than silently failing to submit for lack of a station to submit to. Once identity is set up, "+ Sessions" behaves normally from then on.

## Why this matters

Without step 2 (persisting identity), a "+ Sessions" submission has no real way to know which Curator's Station Dashboard it should land on — it would have to guess from a meaningless device install ID. This protocol gives it a real, already-partially-built answer instead.

## Related
- `CURATOR_INTAKE_PROTOCOL.md`, this folder — the sibling protocol this feeds into once a submission has somewhere real to land.
- Claude memory `project_gerette_pipeline_status` — the session this design conversation happened during.
