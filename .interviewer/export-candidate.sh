#!/usr/bin/env bash
set -euo pipefail

CANDIDATE_SHA="6d49822a441e69b14afdff2babe1290781fb638a"

if [[ $# -ne 1 ]]; then
  echo "usage: $0 /absolute/path/to/new-candidate-copy" >&2
  exit 2
fi

destination="$1"
if [[ "$destination" != /* ]]; then
  echo "destination must be an absolute path" >&2
  exit 2
fi
if [[ -e "$destination" ]]; then
  echo "destination already exists: $destination" >&2
  exit 2
fi

mkdir -p "$destination"
git archive "$CANDIDATE_SHA" | tar -x -C "$destination"

git -C "$destination" init --initial-branch=main
git -C "$destination" add .
git -C "$destination" commit -m "Candidate interview exercise starter"

if [[ -e "$destination/.interviewer" ]]; then
  echo "confidential interviewer directory leaked" >&2
  exit 1
fi
if [[ "$(git -C "$destination" rev-list --all --count)" != "1" ]]; then
  echo "candidate copy does not have exactly one commit" >&2
  exit 1
fi
if [[ "$(git -C "$destination" rev-list --max-parents=0 --all --count)" != "1" ]]; then
  echo "candidate copy does not have exactly one root" >&2
  exit 1
fi
if [[ "$(git -C "$destination" for-each-ref --format='%(refname)' refs/heads refs/remotes)" != "refs/heads/main" ]]; then
  echo "candidate copy has unexpected branches or remotes" >&2
  exit 1
fi
if git -C "$destination" cat-file -e "${CANDIDATE_SHA}^{commit}" 2>/dev/null; then
  echo "source history is reachable from candidate copy" >&2
  exit 1
fi
if [[ -n "$(git -C "$destination" fsck --no-reflogs --unreachable 2>/dev/null)" ]]; then
  echo "candidate copy contains unreachable Git objects" >&2
  exit 1
fi

echo "candidate copy verified: $destination"
echo "root commit: $(git -C "$destination" rev-parse HEAD)"
