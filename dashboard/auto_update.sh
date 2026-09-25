#!/usr/bin/env bash
set -euo pipefail
export GIT_TERMINAL_PROMPT=0

repo=${ANS_SKILL_REPO:?Set ANS_SKILL_REPO to the absolute Git checkout path}
if [[ "$repo" != /* || $(git -C "$repo" rev-parse --is-inside-work-tree 2>/dev/null || true) != true ]]; then
  echo 'ANS_SKILL_REPO must be an absolute Git checkout path' >&2
  exit 2
fi
if [[ ! -f "$repo/dashboard/.env" ]]; then
  echo 'dashboard/.env is missing; refusing to deploy' >&2
  exit 2
fi

lock_file=${ANS_UPDATE_LOCK:-/run/lock/ans-dashboard-auto-update.lock}
mkdir -p "$(dirname "$lock_file")"
exec 9>"$lock_file"
if ! flock -n 9; then
  echo 'Another Dashboard update is running'
  exit 0
fi

branch=$(git -C "$repo" symbolic-ref --quiet --short HEAD || true)
if [[ "$branch" != main ]]; then
  echo "Expected a main checkout, got: ${branch:-detached HEAD}" >&2
  exit 2
fi
if [[ -n $(git -C "$repo" status --porcelain --untracked-files=normal) ]]; then
  echo 'Git checkout has local changes; refusing automatic update' >&2
  exit 2
fi

current=$(git -C "$repo" rev-parse HEAD)
git -C "$repo" fetch --quiet --no-tags origin main
target=$(git -C "$repo" rev-parse FETCH_HEAD)
if [[ "$current" == "$target" ]]; then
  echo "Dashboard already at $current"
  exit 0
fi
if ! git -C "$repo" merge-base --is-ancestor "$current" "$target"; then
  echo 'origin/main did not fast-forward from the deployed commit; refusing update' >&2
  exit 2
fi

echo "Updating Dashboard $current -> $target"
git -C "$repo" merge --ff-only "$target"
cd "$repo/dashboard"
if docker compose up --build --wait --wait-timeout 120 dashboard; then
  echo "Dashboard healthy at $target"
  exit 0
fi

echo 'New Dashboard failed health check; restoring previous commit' >&2
if [[ -n $(git -C "$repo" status --porcelain --untracked-files=normal) ]]; then
  echo 'Checkout changed during deployment; automatic rollback refused' >&2
  exit 1
fi
git -C "$repo" reset --hard "$current"
if docker compose up --build --wait --wait-timeout 120 dashboard; then
  echo "Previous Dashboard restored at $current" >&2
else
  echo 'Rollback also failed; inspect the container and state volume' >&2
fi
exit 1
