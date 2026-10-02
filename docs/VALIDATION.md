# Testing and validation

Date: 2026-10-02. The local baseline is macOS/arm64, Python 3.12.14, PyQt6 6.9.1, PyTubeFix 11.2.0, and external FFmpeg 9.0.2.

## Results

| Check | Result | Limit |
| --- | --- | --- |
| Complete deterministic suite | 37 tests: 34 pass, three expected failures | Expected failures document deferred defects; they are not passing behavior |
| Application coverage | 82% combined statement/branch measurement; CI floor 80% | Generated UI files excluded; native Qt worker thread tracing is incomplete; behavior is also asserted through real signal-driven E2E tests |
| Offline E2E | Playlist lookup → metadata dialog edit → download workers → real FFmpeg → actual title/artist tags; single video with/without conversion/source retention | Only external YouTube provider objects are replaced with deterministic fixture providers |
| Real codec integration | Stereo input to M4A, MP4, MP3, Ogg; valid duration and correct tags | Mono Ogg at 320 kbps is a reproduced pending defect |
| Live YouTube E2E | Latest shared playlist had 35 tracks; all 35 converted to M4A; every saved title/artist checked; progress 100%, zero errors | Network/advisory/platform evidence is dated; external YouTube changes can still break extraction |
| Dependency audit | 53 resolved runtime/dev packages; zero known vulnerability records | Local platform resolution only; external system FFmpeg and undisclosed vulnerabilities are outside pip-audit |
| Secrets | No findings in 51 reachable commits or nonignored worktree snapshot | No proof of absence; ignored data/environments are excluded, no external user files were scanned |
| Bandit | Zero medium/high; 11 low findings in subprocess-based maintenance scripts | Low calls are reviewed argument-list process launches with no shell; not suppressed |
| Fatal lint | E9/F821/F823 checks pass | Full style/cleanup findings remain OPT-013 |
| Workflow validation | actionlint 1.7.12 passes | Check the submission PR for hosted execution results; runner-specific failures remain possible |
| PyInstaller executable | Local macOS build succeeds, offscreen executable remains running 10 seconds outside repo cwd | A process-survival check is not proof of usable GUI readiness, icons, live frozen downloads, or FFmpeg availability; OPT-009 tracks these |
| Wheel build | **Fails**: `No file/folder found for package tek-plexor` | Explicitly deferred as OPT-010; source execution and standalone executable build pass |
| Remote merge protection | Rulesets `[]`, protection endpoint 404, current account not admin | Administrator must inspect and configure required checks; OPS-001 |

## Commands

Install the development tooling inside the application environment:

```sh
python -m pip install -r requirements-dev.txt
ffmpeg -version
python scripts/run_tests.py
python -m coverage report
python -m coverage xml
python -m ruff check --isolated --select E9,F821,F823 main.py tp_engine tp_conversion tp_interface utils scripts tests
python -m bandit -r main.py tp_engine tp_conversion tp_interface utils scripts -ll
python -m pip_audit -r requirements-dev.txt --progress-spinner off
python scripts/check_secrets.py
```

`check_secrets.py` also requires the Gitleaks executable. `run_tests.py` bounds the test process tree to 180 seconds. Run from the repository root. Tests use temporary synthesized 440 Hz audio and do not need credentials or remote media. Real ffmpeg integration tests skip if ffmpeg is missing locally; CI explicitly installs/verifies ffmpeg, so skipping is not the intended CI configuration.

The direct developer command remains available, but has no outer process-tree timeout:

```sh
python -m unittest discover -s tests -v
```

## Live smoke test

```sh
python scripts/live_smoke.py --playlist 'https://youtube.com/playlist?list=YOUR_PUBLIC_PLAYLIST_ID'
```

This downloads **all tracks**, up to 50 by default, to a temporary directory and checks saved audio duration, file count, tags, progress, and worker error counts. It does not authenticate or use cookies. To retain validation output, add `--destination data/live-check`; the folder must be empty. The checker refuses case-insensitive filename collisions while OPT-002 is pending. A parent process enforces a deadline and terminates the test process tree on expiry.

The normal PR gate uses fixture-backed E2E tests. For a live hosted test, run the `CI` workflow manually and supply the optional public `live_playlist` input. Live YouTube failures block that manual run; the weekly deterministic/security run does not download playlists automatically.

## Expected failures and remediation

| Test | Why it fails now | Remove marker after |
| --- | --- | --- |
| `test_source_survives_tag_failure_pending_opt_001` | Source is deleted before tag-save failure | OPT-001 |
| `test_regular_file_is_rejected_pending_opt_007` | An existing regular file passes destination validation | OPT-007 |
| `test_mono_ogg_at_default_bitrate_pending_opt_008` | Opus rejects mono at the default 320 kbps | OPT-008 |

These use `unittest.expectedFailure`, are named in test output, and link directly to the backlog. If a fix unexpectedly makes a test pass, unittest reports unexpected success and fails the suite until the marker is removed. Do not mark new failures as expected without documenting a reviewed backlog item.

## CI and delivery

[CI workflow](../.github/workflows/ci.yml) runs on PRs, main pushes, manual requests, and a weekly schedule. Tests cover Linux Python 3.10/3.11/3.12, macOS 3.12, and Windows 3.12. Security audits runtime and development dependency resolution, medium/high static findings, and redacted repository secrets. Syntax/undefined-name lint and the 80% application coverage floor provide small, maintainable gates.

Linux/macOS/Windows standalone builds run only after tests and security pass. Each build receives a process-survival smoke check, and CI saves the executable as a short-lived artifact. This is artifact delivery, **not a signed public release or auto-deployment**. FFmpeg remains an external prerequisite. Weekly runs omit artifact builds.

Dependabot proposes weekly updates for Python packages and Actions. Actions are pinned to verified commit SHAs; standalone scanner downloads have verified SHA-256 values. Workflows have read-only repository permission and do not store checkout credentials or use repository secrets.

The initial audit was local; the submission follow-up commits and pushes this baseline for PR review. Check the PR for hosted matrix results. No repository-setting change is included. An administrator should require passing checks before merging. Signed releases, locked transitive dependencies, installed-wheel delivery, packaged-resource lookup, and full packaged live E2E remain approval-backlog work.

## Test plan and remaining coverage

| Area | Protected behavior | Next coverage tied to approved work |
| --- | --- | --- |
| Engine | Ordered playlist metadata, single-core pool, title parsing, missing details, empty playlist/errors, bounded HTTP retries, filename containment | URL host/query variants, unreachable/private items, network deadlines; OPT-004/012 |
| Conversion | Four codecs, tags, source retention/deletion, existing final file protection, invalid audio, literal legacy paths | Transaction commit/rollback, collisions, tag failures, same container, mono/bitrate matrix; OPT-001/002/006/008 |
| GUI/workers | Real URL signals and metadata editor, both conversion settings, source preference, finished/error signal contracts, stale-result rejection, progress completion | Immutable queued jobs, existing editor during download, stage summaries, cancellation; OPT-003/005/012 |
| Destination | Missing path and unsupported settings; file-as-directory documented defect | Writable/disappearing destinations and filesystem error reporting; OPT-007 |
| Distribution | Executable build and bounded process survival | Ready-window handshake, icons from alternate cwd, frozen live extraction, installation/signing; OPT-009/010, OPS-002 |

Measure coverage as a regression indicator, not proof of correctness. Prefer an acceptance test that catches a destructive or wrong-stage behavior over tests for trivial getters or generated UI text.
