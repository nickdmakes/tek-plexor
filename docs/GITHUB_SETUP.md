# GitHub setup and pipeline operations

Tracking: PR [#1](https://github.com/nickdmakes/tek-plexor/pull/1); merge protection backlog item OPS-001.

## Administrator actions

The submitting account can push and open PRs but cannot administer repository settings. An administrator must activate a branch ruleset for `main` in **Settings → Rules → Rulesets**. Require pull requests and review, block force pushes and deletion, and require these exact checks from the CI workflow:

- `Security`
- `Test (ubuntu-latest, Python 3.10)`
- `Test (ubuntu-latest, Python 3.11)`
- `Test (ubuntu-latest, Python 3.12)`
- `Test (macos-latest, Python 3.12)`
- `Test (windows-latest, Python 3.12)`
- `Package (ubuntu-latest)`
- `Package (macos-latest)`
- `Package (windows-latest)`

Require the branch to be up to date before merging. Choose administrator bypass policy explicitly.

Review and merge PR #1 once its latest checks pass. This puts the weekly scheduled checks and Dependabot configuration on the default branch. No new repository secrets are needed for this baseline.

Reference: [GitHub branch ruleset instructions](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository).

## Delivery and ongoing checks

PRs and main pushes run deterministic tests, coverage, security scans, and executable builds for Linux, macOS, and Windows. Download tested artifacts from the workflow run; these are unsigned validation builds. Public signed releases remain OPS-002 and need a separate approved release plan. Weekly runs audit dependencies and run deterministic tests; they intentionally omit packaging. Review Dependabot PRs and require the same passing checks.

## Live YouTube validation

Hosted CI has no live-download job or playlist input. Manual workflow dispatch runs the same offline checks. Live checks are permitted only when necessary, locally through an active VPN. The initial GitHub-hosted run rejected the supplied playlist with PyTubeFix `BotDetection` during metadata retrieval, although the local full playlist run passed all 35 tracks. Hosted IP reputation therefore prevents claiming a successful live GitHub download.

Only if live validation is necessary: activate and verify VPN routing, set `TEK_PLEXOR_TEST_URL` explicitly, then run locally:

```sh
python scripts/live_smoke.py --vpn-confirmed --playlist "$TEK_PLEXOR_TEST_URL"
```

A small reference candidate is [DEAF KEV — Invincible (NCS)](https://www.youtube.com/watch?v=J2X5mJ3HDYE), linked by the [official NCS track page](https://ncs.io/INVINCIBLE). This reference was located through web search only; it was not played, downloaded, or tested. It is not a default or executable fixture. Prefer a single track; any user-chosen playlist is limited to five tracks by default.

FFmpeg must be installed. The command uses temporary outputs and validates every file. Do not add personal cookies or authentication material to the repository to bypass provider restrictions.

## Known validation boundaries

Three expected-failure tests track deferred file-safety, destination, and mono-Opus defects. Executable smoke tests establish process survival, not a complete frozen-app download or visual resource check. See [validation](VALIDATION.md), [security review](SECURITY_REVIEW.md), and the prioritized [optimization backlog](OPTIMIZATION_BACKLOG.md) before approving further changes.
