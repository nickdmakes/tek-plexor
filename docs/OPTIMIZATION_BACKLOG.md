# TekPlexor optimization backlog

Reviewed: 2026-10-02. Owner: maintainer. Scope: desktop Python/PyQt application, YouTube extraction, conversion, packaging, and repository protection.

## Review status

Tests, CI configuration, dependency updates, security scans, and one bounded shell-execution fix are implemented in the submission branch. The optimization items below are **awaiting approval**. A successful playlist run demonstrates the happy path; it does not resolve the file-safety and edge-case defects listed here.

Choose items by ID, for example: `Approve OPT-001 and OPT-002`. Track each item as `Awaiting approval → Approved → In progress → Verified → Done`. Record a PR/commit and verification result before marking Done. No item in the pending table has been implemented as part of this sweep.

## Implemented protection

| ID | Status | Change | Verification |
| --- | --- | --- | --- |
| BASE-001 | Implemented | Unit, real FFmpeg integration, and offline Qt end-to-end tests | 37 tests: 34 pass; three explicit expected failures below; 82% measured statement/branch coverage |
| BASE-002 | Implemented | CI tests on Linux Python 3.10/3.11/3.12, macOS 3.12, Windows 3.12; 80% coverage floor | Local suite passes; workflow passes actionlint; hosted matrix results must be confirmed on the PR |
| BASE-003 | Implemented | Gitleaks history/worktree scans, dependency vulnerability audit, Bandit medium/high gate, fatal Python lint checks | No scan-detected secrets; zero known vulnerability records among 53 resolved development/runtime packages on local Python 3.12; no medium/high Bandit findings |
| BASE-004 | Implemented | SHA-pinned Actions, read-only token, no stored checkout credentials, weekly Dependabot, gated build artifacts | Workflow lint passes; local macOS executable builds; startup check described in validation report |
| BASE-005 | Implemented | Legacy conversion helper invokes FFmpeg without a shell, checks failure before source deletion, and rejects existing output | Real filenames containing `&` convert correctly; failure preserves source; original high-severity Bandit finding removed |
| BASE-006 | Implemented | Opt-in live playlist checker with empty-destination and collision safeguards | Latest live playlist: 35 tracks converted, every saved title/artist tag verified, 100% progress, zero errors |

The baseline is submitted separately from the pending optimization work. See the pull request for hosted CI results. CI configuration cannot force merge protection without repository settings.

## Priority order

P1: prevent data loss and protect merges. P2: correct common failures and harden delivery. P3: maintenance and UX improvements. No remotely exploitable critical issue was demonstrated. Scores help sort within a phase; data-loss and security dependencies take precedence.

Score = `(impact + risk) × (6 − effort)`, each dimension 1–5. Effort is a rough relative estimate, not a delivery commitment: 1 is a small patch; 2 is roughly half a day; 3 is 1–2 days; 4 is several days; 5 requires broader design. Owner defaults to maintainer until assigned.

| Order | ID | Priority | Optimization | Impact / risk / effort | Score | Status | Depends on |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | OPT-001 | P1 | Transactional conversion and source retention | 5 / 5 / 3 | 30 | Awaiting approval | — |
| 2 | OPT-002 | P1 | Collision-safe download and final filenames | 5 / 5 / 3 | 30 | Awaiting approval | OPT-001 |
| 3 | OPS-001 | P1 | Enforce required checks and reviewed merges | 5 / 4 / 1 | 45 | Awaiting approval | BASE-002 pushed; admin access |
| 4 | OPT-003 | P2 | Immutable per-job metadata and batch state | 4 / 4 / 2 | 32 | Awaiting approval | — |
| 5 | OPT-004 | P2 | Validate/debounce URLs and bound retrieval work | 4 / 4 / 3 | 24 | Awaiting approval | — |
| 6 | OPT-005 | P2 | Accurate stage errors and completion summaries | 4 / 3 / 2 | 28 | Awaiting approval | OPT-001, OPT-003 |
| 7 | OPT-006 | P2 | Same-container conversion and quality policy | 4 / 3 / 2 | 28 | Awaiting approval | OPT-001 |
| 8 | OPT-007 | P2 | Validate destination directory and write failures | 3 / 3 / 1 | 30 | Awaiting approval | — |
| 9 | OPT-008 | P2 | Channel-aware Opus bitrate handling | 3 / 3 / 1 | 30 | Awaiting approval | OPT-006 |
| 10 | OPT-009 | P2 | Packaged resources and runtime preflight | 4 / 3 / 3 | 21 | Awaiting approval | — |
| 11 | OPT-010 | P2 | Reproducible dependency resolution and wheel install | 3 / 3 / 3 | 18 | Awaiting approval | — |
| 12 | OPT-011 | P3 | Literal, safe debug-console messages | 2 / 2 / 1 | 20 | Awaiting approval | — |
| 13 | OPT-012 | P3 | Cancellation, partial playlist results, and retry UI | 3 / 2 / 4 | 10 | Awaiting approval | OPT-003, OPT-004, OPT-005 |
| 14 | OPT-013 | P3 | Remove duplicate/dead code and tighten lint | 2 / 2 / 2 | 16 | Awaiting approval | — |
| 15 | OPS-002 | P3 | Signed release distribution | 3 / 2 / 4 | 10 | Awaiting approval | OPT-009, OPT-010 |

## Acceptance criteria and evidence

### OPT-001 — Commit complete converted files before deleting originals

Evidence: `tp_conversion/converter.py:80–109` encodes directly to the final filename, passes overwrite mode to FFmpeg, deletes the original, then adds tags. The unused `convert_to_m4a` helper has the same destructive ordering at lines 113–140. A tag failure deletes the original. An encoder failure can leave a partial final output that prevents retry.

Proposed change: encode and tag an owned temporary sibling, commit the complete result without overwriting existing files, then delete the original only after success. Remove only this job's temporary files on failure. Preserve the original on every encoding/tagging/commit error.

Acceptance: injected tag and encoder failures retain identical source bytes; no partial final output is published; retry succeeds after a failed attempt; concurrent commits never overwrite another result. Remove the expected-failure marker from `test_source_survives_tag_failure_pending_opt_001` after the production fix.

### OPT-002 — Reserve distinct destinations for colliding tracks

Evidence: `yt_download_controller.py:174` derives names only from sanitized title/artist; `yt_api.py:122–124` delegates to PyTubeFix with `skip_existing=True`. Inspection of installed PyTubeFix shows that this flag only skips a matching-size original; otherwise the destination can be opened for writing. Different videos, repeated URLs, and sanitizer/case collisions may share a path. FFmpeg's separate existence check and overwrite mode also race.

Proposed change: unique per-job temporary source paths, stable collision policy using video identity or track number, and exclusive final-file reservation. Decide whether repeated URLs should be deduplicated or retained as separately named tracks.

Acceptance: two simultaneous videos with identical metadata or sanitized names both produce the intended files; existing originals and outputs retain their bytes regardless of size; no overwrite on case-insensitive platforms. Test with concurrent workers and preexisting files.

### OPS-001 — Activate merge protection

Evidence: origin is public `nickdmakes/tek-plexor`. Repository rulesets API returned an empty list. Branch-protection API returned 404; current account has push permission but no admin permission. This supports a configuration gap but is not proof that every possible organization-level control is absent.

Proposed action: after these workflows are merged, an administrator should require every matrix test and Security check, disallow direct/force pushes to main, require review, and protect workflow changes. Select actual check names after the first hosted run. Decide how maintainer bypasses should work.

Acceptance: a PR with failing tests/security cannot merge and direct pushes cannot bypass the chosen policy. Record settings verification and required check names here.

### OPT-003 — Snapshot metadata and protect an active batch

Evidence: `yt_download_controller.py:146–152` disables URL and metadata-open button but leaves title/artist editable. `MetadataPayload.getPayload()` returns a shared dictionary (`utils/Utils.py:108–109`). An already-open nonmodal metadata editor can also mutate queued jobs.

Proposed change: copy download/metadata settings per worker; freeze or close editors during a batch; provide explicit state transitions rather than sharing mutable GUI data.

Acceptance: editing title, artist, destination, or a previously opened metadata window after submission cannot change queued filenames or tags; subsequent batches use the new edits. Workers do not update Qt widgets directly.

### OPT-004 — Bound metadata retrieval and parse URLs explicitly

Evidence: every text change schedules a lookup (`yt_download_controller.py:242–260`) in the same pool used for downloads. Stale-result IDs prevent replacement of current metadata but do not cancel obsolete network work. Engine detection uses a `"playlist"` substring (`yt_api.py:37`), rather than a parsed YouTube host/path/query.

Proposed change: validate supported YouTube hosts and identifiers before network access, accept intentional playlist URLs including watch URLs with `list`, debounce edits, separate retrieval/download scheduling, and enforce deadlines without using unsafe thread termination.

Acceptance: malformed/non-YouTube inputs cause no request; supported share/video/playlist variants resolve correctly; rapid edits produce one current lookup; slow obsolete requests cannot block current work indefinitely. Empty, inaccessible, private, and partially unavailable playlists have useful outcomes.

### OPT-005 — Report the failing stage accurately

Evidence: generic exceptions in `yt_download_worker.py:58–61` count as failed downloads through `yt_download_controller.py:237–239`, including tagging failures or a missing FFmpeg executable after download success. The summary can call conversion-disabled tracks converted; status always says finished even when errors exist.

Proposed change: typed per-track stage/result state; wrap filesystem/metadata errors at the correct boundary; summaries distinguish successful/skipped/failed downloads and conversions.

Acceptance: missing FFmpeg and tag failures count as conversion failures after successful downloads; conversion-disabled batches report conversion skipped; mixed failures still complete with an accurate error count and retry guidance.

### OPT-006 — Support input and output sharing a container

Evidence: `convert` derives output by replacing the suffix and then checks existence (`converter.py:81–84`). An MP4 source with MP4 selected is mistaken for an existing converted output. Current bitrate settings can also transcode already-lossy audio without improving the source quality.

Proposed change: define a safe same-container path using a separate temporary output; decide when remux/tagging or keeping original audio is preferable to transcoding. Avoid promises that 320 kbps creates source detail that was not present.

Acceptance: MP4-source/MP4-output works while preserving source on failure; all supported formats retain intended tags; source-quality policy is visible and testable. Do not introduce new file-safety exceptions.

### OPT-007 — Reject invalid destinations before starting jobs

Evidence: `utils/Utils.py:45–63` checks path existence, not whether it is a directory. An existing file passes validation. Filesystem permission errors are discovered after work starts.

Proposed change: reject non-directories, report write/create failures clearly, and validate actual writes rather than relying only on permission bits that can race.

Acceptance: regular file, missing directory, unwritable directory, and disappearing destination yield actionable errors without overwriting user files. Remove the marker from `test_regular_file_is_rejected_pending_opt_007`.

### OPT-008 — Respect Opus constraints for mono input

Evidence: a real 48 kHz mono fixture fails conversion to Ogg/Opus at the default 320 kbps; stereo fixtures pass. The converter applies one bitrate to every codec/channel configuration (`converter.py:86–100`).

Proposed change: select a valid codec/channel bitrate, explicitly resample/upmix only if that is the chosen product behavior, and explain any adjustment.

Acceptance: mono and stereo sources convert at each offered bitrate to supported containers; metadata survives; no silent unsupported setting. Remove the marker from `test_mono_ogg_at_default_bitrate_pending_opt_008`.

### OPT-009 — Validate packaged downloads and resolve bundled resources

Evidence: icon paths are relative to the working directory (`yt_download_controller.py:82–83` and status handlers). CI now bundles icons, but packaging them does not fix runtime lookup. Startup smoke tests prove imports/window initialization only. FFmpeg remains an external prerequisite, and PyTubeFix's JavaScript/Node assets need actual frozen-download testing.

Proposed change: resolve package resources independently of cwd; add actionable ffmpeg/runtime preflight; test the packaged app's real extraction/download/conversion. Decide whether to bundle FFmpeg separately with its licensing/distribution requirements.

Acceptance: packaged app launched from a different directory shows icons and completes a live video/playlist; offline fixtures also pass; missing dependencies have readable errors; Linux/macOS/Windows artifacts are tested on their own platforms.

### OPT-010 — Consolidate dependency declarations and test wheel installation

Evidence: runtime pins in `requirements.txt` differ in policy from caret ranges in `pyproject.toml`; transitive packages are resolved on each install. Poetry package layout/entry point is not explicit, and a real `uv build --wheel` attempt failed with `No file/folder found for package tek-plexor`.

Proposed change: one authoritative dependency workflow with reproducible resolutions/hashes for supported platforms, explicit package declarations and console entry point if pip/wheel installation is intended, compatible runtime/build/dev dependency separation.

Acceptance: clean install and wheel build succeed on supported Python versions; installed app imports/runs outside its checkout; dependency declarations stay in sync; audited locks update through reviewed PRs.

### OPT-011 — Escape untrusted log text

Evidence: `tp_interface/debug_logger.py:10–23` interpolates filenames, provider strings, and errors into rich text. Markup can alter displayed messages and conceal or imitate status text. No browser JavaScript execution or remote code execution was demonstrated; this is a desktop rendering issue, not a proven web XSS vulnerability.

Proposed change: render literal escaped text with explicit formatting for severity.

Acceptance: `<b>`, links, ampersands, and image-looking strings display literally; messages cannot spoof formatting or insert rich-text resource references.

### OPT-012 — Recover gracefully from partial batches

Evidence: the playlist metadata future loop raises on a failed item; no cancellation control or per-track retry UI exists. Worker deadlines alone do not create a usable cancellation/recovery path.

Proposed change: expose unavailable tracks, retain successful metadata, support cancellation between safe boundaries, and retry failed tracks without redownloading successful outputs.

Acceptance: one unavailable video does not discard every accessible track; cancellation preserves files; retry does not duplicate or overwrite completed outputs. Confirm acceptable partial-playlist behavior before implementation.

### OPT-013 — Reduce duplicate code and expand lint safely

Evidence: duplicate metadata UI modules, unused `tp_interface/output.py`, duplicated payload constructors, unused imports, broad catches, and datetime-based duration formatting appear in the static sweep. The new lint gate catches fatal syntax/undefined-name errors, not all style findings.

Proposed change: remove demonstrated dead code, unify controllers/payload construction, use a monotonic duration, format hand-written modules, and progressively enable full lint checks while keeping generated UI files separate.

Acceptance: healthy behavior stays covered by E2E tests; generated UI regeneration is documented; full lint has no unexplained suppressions; no unrelated redesign bundled into safety fixes.

### OPS-002 — Release artifacts deliberately

Evidence: CI builds downloadable artifacts only. There is no signing/notarization, update mechanism, or published release process. FFmpeg is still external.

Proposed action: decide supported OS/architecture targets, sign/notarize where required, attach checksums and an SBOM, document installation and release approval, and retain release provenance. Keep publishing behind explicit release approval.

Acceptance: users can install/run supported artifacts with documented trust checks; release artifacts come only from passing tests/security and an approved immutable version.

## Review checklist

- [ ] Approve OPT-001 and OPT-002 to address the highest data-loss risks.
- [ ] Assign an administrator for OPS-001 after the first hosted workflow run.
- [ ] Select the next P2 batch and decide source-quality/same-container policy.
- [ ] Confirm distribution targets before packaging and signing work.
- [ ] For every approved item, replace any expected-failure marker with a passing regression before Done.

## Implementation record

| ID | Approval date | Assignee | PR/commit | Verification | Completion date |
| --- | --- | --- | --- | --- | --- |
| Pending | — | — | — | — | — |
