# Construction dry-run record

Date: 2026-09-12

## Frozen candidate starter

Source commit: `6d49822a441e69b14afdff2babe1290781fb638a`

Commands and results:

- `make verify-env` — passed with locked dependencies.
- `make baseline` — passed: Ruff format/lint, strict mypy, 14 pytest tests.
- `python .interviewer/evaluator.py --expect unsafe` executed with the starter on `PYTHONPATH` — passed: direct IPv4, direct IPv6, link-local, and redirected protected destinations all reached the tracking transport; a public redirect chain still worked.
- credential-shaped value scan — no matches in tracked candidate files.
- candidate-facing leakage scan — no interviewer directory or named answer-key terms in the frozen tree.

The construction host's managed Python 3.12 installation was broken independently of this repository. Local proof used system Python 3.13 with `UV_PYTHON=/usr/bin/python3.13`; the pinned Python 3.12 devcontainer was separately built and verified during the PR review.

## Worked reference solution

Commands and results:

- `make verify-env` — passed with locked dependencies.
- `make baseline` — passed: Ruff format/lint, strict mypy, 23 pytest tests.
- `python .interviewer/evaluator.py --expect safe` — passed: all four modeled protected paths were denied before the protected outbound hop and the public redirect chain still worked.
- all DNS and HTTP outcomes in tests/evaluator used `StaticResolver` and `TrackingTransport`/`ScriptedTransport`; no test contacted DNS, external HTTP, cloud services, or credentials.

## History-free export proof

`./.interviewer/export-candidate.sh <new-temp-path>/candidate` produced:

- exactly one commit and one root commit;
- exactly one ref: `refs/heads/main`;
- no `.interviewer` path;
- no source commit reachable by object ID;
- no unreachable Git objects; and
- the complete 14-test candidate baseline passing in the exported repository.

## Timing calibration

The starter contains five short product modules and two candidate-visible test modules. The worked change adds one policy module, one call at each outbound hop, and focused tests; this is qualitatively scoped for the 35-minute coding phase when setup is complete. No independent engineer has yet completed a timed pilot, so timing remains a calibration requirement before relying on the exercise across the full pipeline.
