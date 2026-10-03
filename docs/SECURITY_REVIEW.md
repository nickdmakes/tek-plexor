# TekPlexor security review

Date: 2026-10-02. Scope: working-tree application code, maintenance scripts, repository workflow configuration, reachable Git history, nonignored repository files, and dependency resolution on local macOS/Python 3.12.

## Result

No secrets were detected in the 51-commit Git-history scan or the nonignored working-tree scan. The local runtime/development dependency audit resolved 53 packages and found zero known vulnerability records. These checks do not prove that every secret or vulnerability is absent. Offline scanner coverage excludes ignored local environments/downloads and external system tools such as FFmpeg; hosted Linux/Windows resolution still needs to run.

One high-severity static finding was confirmed and fixed: the unused legacy conversion helper interpolated untrusted filenames into a shell command. Current Bandit reports zero medium/high findings and 11 low findings associated with subprocess execution and temporary-path use in test/maintenance code. No scanner suppressions or vulnerability ignore lists were added.

Outstanding data-integrity and rendering issues remain pending review in [the backlog](OPTIMIZATION_BACKLOG.md). Desktop risk differs from a network server: no service listener, account login, persisted credentials, or application authentication flow was found. Framework-specific Python web guidance does not apply to this PyQt app.

## Findings

| ID | Severity | State | Evidence | Impact / action |
| --- | --- | --- | --- | --- |
| SEC-001 | High, latent | Fixed locally | Original `converter.py:147` used `os.system` with interpolated input/output paths; no active production call site found | Shell metacharacters could execute commands if the helper was reused; failed encoding could delete source. Current lines 144–156 pass literal arguments to FFmpeg, check failure before deletion, and reject existing output. Real FFmpeg regression tests cover metacharacter paths and source preservation. |
| SEC-002 | High data integrity | Awaiting approval | `converter.py:80–109`; `yt_download_controller.py:174`; `yt_api.py:122–124` | Source deletion before tagging, partial final outputs, and concurrent filename collisions can destroy user audio. See OPT-001/002. This is not evidence of remote code execution. |
| SEC-003 | Low rendering integrity | Awaiting approval | `debug_logger.py:10–23` | Provider-controlled/title/error strings are interpolated into rich text. Escape before display; see OPT-011. Web XSS/JavaScript execution was not demonstrated. |
| SEC-004 | Repository control gap | Awaiting admin action | Rulesets API returned `[]`; main protection returned 404; current identity is not admin | Workflows alone do not prevent bypassing failing checks. Require checks and reviewed merges after activation; see OPS-001. |

## New protection

CI uses SHA-pinned GitHub Actions, a read-only token, disabled checkout credential persistence, no repository secrets, and no `pull_request_target` execution. Security checks fail on known dependency vulnerabilities, medium/high Bandit issues, or Gitleaks findings. Scans redact matched secrets. Downloaded Gitleaks and actionlint binaries are version-pinned and checksum-verified. Dependabot proposes reviewed weekly dependency/Actions updates. Published release deployment is not configured.

## Recheck

```sh
python -m pip_audit -r requirements-dev.txt --progress-spinner off
python -m bandit -r main.py tp_engine tp_conversion tp_interface utils scripts -ll
python scripts/check_secrets.py
```

The final command requires Gitleaks. It scans reachable Git history plus tracked/nonignored working-tree files, rejects symlinks rather than following them, and never prints matched values without redaction. Scanner tools and advisory sources can still miss custom secret formats or undisclosed vulnerabilities.

## References

- [GitHub Actions secure use](https://docs.github.com/en/actions/reference/security/secure-use): immutable action pins, least privilege, and untrusted PR handling.
- [pip-audit](https://pypi.org/project/pip-audit/): known Python dependency advisory scanning, rather than a proof that dependencies are vulnerability-free.
- [Gitleaks](https://github.com/gitleaks/gitleaks): repository/history secret scanning.
