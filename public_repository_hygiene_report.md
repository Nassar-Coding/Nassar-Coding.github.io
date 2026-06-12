# Public Repository Hygiene Report

## 1. Branch started from
`claude/new-session-56q4pt` (final state: commit `2d1c6d3`, suite 37/0/0,
clean tree). This branch is preserved untouched as the complete internal
record.

## 2. Cleanup branch
`cleanup/professional-repo` — branched from the above; holds the
sanitization work, the explicit `private_archive/` of removed internal
materials, and this report. Internal-use only.

## 3. Final public branch
`public-release` — a fresh **orphan branch** with a **single clean
commit** (`2f0d51a34d4baae77c56fab963eeba4b1f65b5a3`, 1 commit in
history). It inherits no prior history, so no internal commit messages,
session trailers, or construction-process artifacts exist anywhere in its
history. The project tree sits at the repository root (no `dream-paper/`
nesting). Note: one residual reviewer-reference docstring was found after
the branch's initial creation; because the branch was seconds old with no
consumers, its single commit was amended and force-pushed rather than
patched on top — no pre-existing history was rewritten, and the term now
appears nowhere in the branch's history.

## 4. Files removed from the public branch
- `docs/findings/` (3 internal review documents)
- `docs/04_decision_log.md`, `docs/05_venue_strategy.md`,
  `docs/06_redesign_specification.md`, `docs/07_review_gates.md`
- `paper_redesign_implementation_report.md`
- `prof1_prof2_revision_response_report.md`
- `artifacts/` (stale pre-redesign outputs + manifest)
- repository-root site file (`Push`) and internal CI workflows
  (`acquire-nyc-export.yml`, `dream-paper-tests.yml` — replaced by
  sanitized `tests.yml` and a dispatch-only `acquire-311-data.yml`)
- LaTeX build byproducts (`*.aux/*.log/*.bbl/...`), `__pycache__`,
  `.pytest_cache`

## 5. Files moved to private archive
All items above are preserved twice: (a) in full on
`claude/new-session-56q4pt`, and (b) explicitly under
`private_archive/` on `cleanup/professional-repo` (41 paths: findings/,
the four internal docs, the two internal reports, stale_artifacts/).
Nothing was destroyed.

## 6. Files rewritten for the public branch
- `README.md` — full rewrite to the 12-point public specification.
- `docs/01_problem_definition.md` — supersession notice made
  self-contained (references to removed internal protocol documents and
  internal amendment/commit identifiers replaced with
  `configs/decision.yml` and the freeze date).
- `docs/02_novelty_and_literature_audit.md` — search-coverage sentence
  neutralized.
- `reproducibility/command_log.md` — reviewer/mirror references removed;
  path-sanitization of logs disclosed.
- `reproducibility/checklists.md` — venue line removed; internal
  decision-log pointers neutralized.
- `outputs/logs/*` and `reproducibility/execution_evidence/*` — absolute
  environment paths replaced with `<REPO_ROOT>` / `<PYTHON_ENV>`
  placeholders; log content otherwise verbatim.
- `tests/test_guards.py` — three docstrings carrying reviewer shorthand
  neutralized (guard logic unchanged; suite re-verified).
- `.github/workflows/` — sanitized `tests.yml` (public-release/main
  triggers) and dispatch-only `acquire-311-data.yml`.

## 7. Filename scan results
Full `find` over the public tree for claude/chatgpt/prompt/agent/prof/
venue/closure patterns: **zero hits**.

## 8. Text scan results
Full `git grep -i` over the committed public tree for the complete
internal-language list (Claude, ChatGPT, OpenAI, Anthropic, prompt,
implementation agent, Prof 1/2, closure review, re-closure, Google
Drive, Drive mirror, pasted, old/deleted repo, Harvard, admissions,
venue strategy, not defensible, major/minor revision, READY AFTER/FOR,
review gate, internal-process labels, conversation): **zero hits** after
sanitization. Security scan (API_KEY, TOKEN, SECRET, PASSWORD, /Users/,
C:\Users, localhost, /home/, /root/): no credentials or private paths
remain.

## 9. Remaining allowed hits, with justification
| Pattern | Location | Justification |
|---|---|---|
| "MIT" | `LICENSE`, README license section | the software license's name |
| author email (gmail) | README contact, `CITATION.cff`, paper author block, acquisition User-Agent strings, data manifests | author/contact information, explicitly permitted; standard polite-scraping identification in User-Agent |
| "agent" substring | `User-Agent`/`USER_AGENT` in `src/acquisition/*` and raw manifests | standard HTTP header name |
| "internal" | feature-set name `internal` throughout code/tables/paper | the internal-history feature set — a scientific term, not process language |
| "closure" substring | `conclusion.tex` ("closure data" = case-closure timestamps), code comments ("no gap-closure normalization exists" = the banned metric's absence), Chicago native category "Renters and Foreclosure Complaint" | scientific term / negated banned metric / raw data value |
| "TOKEN" substring | `FORBIDDEN_*_TOKENS` variable names in the guard suite | terminology-guard token lists, not secrets |
| `claude/new-session-56q4pt` string | this report and `private_archive/` docs on the **cleanup branch only** | required by this report; absent from `public-release` |

## 10. README cleanup summary
New README contains exactly: title, one-paragraph summary, research
question, data-source table, repository structure, installation
(pip-freeze authoritative), reproduction commands, expected outputs,
tests (G1–G16, 37), citation instructions, license, author contact. No
process, tooling, reviewer, venue, or admissions language.

## 11. Reproducibility-log sanitation summary
All 10 run logs and the pytest log ship on the public branch (plus
mirror-safe `.log.txt` copies in `reproducibility/execution_evidence/`);
the only edit was replacing absolute build-environment paths with
placeholders, disclosed in `command_log.md`.

## 12. Manuscript and supplement scan result
`paper/` and `supplement/` sources: clean against the full term list
(also enforced permanently by guard G8). Compiled `main.pdf`,
`main_anon.pdf`, `supplement.pdf` contain only the author's name/email
(permitted) — no internal terms; both PDFs are the final reviewed
builds, byte-identical to the internal branch's.

## 13. Tests run
`python3 -m pytest tests -q` executed inside the public export with
regenerable intermediates supplied: **37 passed / 0 failed / 0 skipped**.
The targeted G14 guard was re-run after the docstring fix: passed.
(On a fresh clone, artifact guards needing `data/interim`/`processed`
skip until `make all` regenerates them — documented behavior.)

## 14. Final public repository structure
```
README.md  LICENSE  CITATION.cff  Makefile  pyproject.toml  requirements.txt
configs/  src/  scripts/  tests/  docs/ (01–03, sanitized)
data/raw/ (+ manifests)  outputs/ (metrics, tables incl. provenance,
figures, sanitized logs)  paper/ (sources + main.pdf + main_anon.pdf)
supplement/ (sources + supplement.pdf)  reproducibility/ (pip-freeze,
checklists, command log, execution evidence, pytest log)
.github/workflows/ (sanitized tests + dispatch-only acquisition)
```
156 files; single commit.

## 15. Final git status
Clean on all three branches at hand-off (`git status --porcelain` empty).

## 16. Final commit SHAs
- `public-release`: `2f0d51a34d4baae77c56fab963eeba4b1f65b5a3` (pushed)
- `cleanup/professional-repo`: see the commit carrying this report (pushed)
- `claude/new-session-56q4pt`: `2d1c6d3` (untouched)
- note: the remote `cleanup/professional-repo` previously held unrelated
  stale content from an older project (tip `b460dd0`, 2026-05-30,
  "CrowdOps" demo); per the create-or-update instruction it was updated
  to the current cleanup state. The old tip SHA is recorded here and
  remains recoverable from the remote object store until garbage
  collection; nothing from the CURRENT project was overwritten.

## 17. Confirmation — no scientific result changed
No experiment was rerun; no metric, table value, figure, or paper claim
changed. The compiled PDFs on `public-release` are byte-identical to the
final reviewed builds. The only code file touched was `test_guards.py`
docstrings (logic unchanged; suite green).

## 18. Confirmation — no venue selection performed
None. The venue-strategy draft was moved to the private archive,
explicitly marked not-started.

## 19. Recommendation on the internal branches
**Important:** `claude/new-session-56q4pt` and its full history (commit
messages carrying session trailers, internal reports, review verdicts,
the pre-redesign artifacts) are already pushed to this public GitHub
repository. Deleting files in new commits does NOT remove them from that
branch's history, and the branch name itself is internal-flavored.
Recommended, in order of preference:
1. **Create a new, dedicated public repository** (e.g.,
   `nyc-311-benchmark` or similar) initialized from the `public-release`
   export — cleanest separation, since this repository is your personal
   site and its other branches remain visible; then make this repo's
   internal branches private by making the whole repo private, or
2. after privately archiving (clone or bundle the full repo locally),
   **delete the remote `claude/new-session-56q4pt` and
   `cleanup/professional-repo` branches** so only `public-release`
   (and optionally `main` fast-forwarded to it) remains visible; note
   that GitHub may retain orphaned commits temporarily via direct SHA
   links until garbage collection, or
3. history-cleaning tools (filter-repo) on the existing branches — only
   with your explicit approval, and unnecessary if option 1 or 2 is taken.
Do not present this repository publicly until one of these is done.
