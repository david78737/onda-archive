# Recording Recovery Protocol

Written 2026-09-09, the night a debug install wiped a Samsung's local recordings (see `feedback_never_direct_install` in Claude memory for how that happened). This documents how real files were actually recovered afterward — worth knowing because a locally-wiped phone is not always a total loss.

## Why this works at all

"Send with a Message" and "Share Bundle" both upload a real `.onda` file to Xano, into a table called `onda_share_links` — completely separate from the phone's own local database. If a recording was ever shared this way, even once, a second copy exists in Xano independent of whatever happens to the phone. That's what made recovery possible here.

## Step-by-step

1. **Do not use the existing `RescueTools/full_audit` endpoint for this.** It's hardcoded to return only 5 sample rows per table, no matter what's asked of it — this cost real time before it was understood as a hard limit, not a bug to fix.
2. Ask Xano AI (relayed by hand, same pattern as every other Xano change this session) to write a **brand-new, one-off function** with no row limit — e.g. `get_onda_share_links_no_limit.xs` — that queries `onda_share_links`, sorted by `created_at` descending, returning every row. Ask for a `total_returned` count in the response so you can confirm nothing was silently capped.
3. Fields needed per row: `id`, `uuid`, `filename`, `file.url`, `file.size`, `expires_at`, `created_at`, `sleeve_id`, `install_id`.
4. Scan the results by filename/date to find real candidates. Expect noise: "Storyboard" entries aren't spoken recordings, and this workspace also has an old, unrelated bulk-imported block of ProductCamp/product-management conference talk titles with blank `install_id` — exclude both from consideration.
5. For each real candidate, two actions matter:
   - **Listen first, before deciding anything** — reuse the existing static web player: `<player-host>/index.html?src=<url-encoded file.url>`. This is the same mechanism behind every "Send with a Message" link ever generated.
   - **Download** — the direct `file.url` itself. These files are stored with `access: public`, so no signed URL is needed; a plain link works.
6. Build a simple review page listing every candidate with a Listen button, a Download button, and a Keep/Discard toggle, so nothing has to be re-decided twice across a session. (Built as a Claude Artifact this time — "Recovery Queue.")
7. **To actually restore a file:** download it on the *same device* you want it restored to (or transfer it there some other way), then in Replay: Utilities → Import Recording → pick the downloaded file from that device's Downloads.

## Known limits — don't oversell this as a full safety net

- Only recordings that were actually shared at least once via Send with a Message / Share Bundle have a Xano-side copy. Anything never shared this way is genuinely gone if the device is wiped.
- Share links expire (currently 60 days) and get cleaned up by a scheduled task, which deletes the database row. Whether the underlying file in storage survives orphaned after that point was never conclusively confirmed this session — an approach to check this directly (querying Xano's internal `_file` table via `maintenance/list_onda_files.xs`) was attempted but abandoned after repeated syntax disagreements from Xano's own AI about how to query that table correctly. Worth revisiting if a future recovery needs a file whose link has already expired.
- This is not a substitute for the general-purpose backup feature already in the app (Utilities → Backup, `AnBackupService.backupAll()`) — that one is complete and immediate but has no bulk restore counterpart yet; this protocol is what to do when a backup was never taken.

## Related
- Claude memory `feedback_never_direct_install` — why this was needed the first time.
- `CURATOR_INTAKE_PROTOCOL.md` (this folder) — the sibling protocol for getting a recording *into* Nile; this one is about getting a recording *back*.
