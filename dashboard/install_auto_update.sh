#!/usr/bin/env bash
set -euo pipefail

if [[ ${EUID:-$(id -u)} -ne 0 ]]; then
  echo 'Run this installer as root' >&2
  exit 2
fi
repo=$(git -C "$(dirname "$0")/.." rev-parse --show-toplevel)
if [[ "$repo" == *'"'* || "$repo" == *$'\n'* ]]; then
  echo 'Repository path contains unsupported characters' >&2
  exit 2
fi
if [[ ! -f "$repo/dashboard/.env" ]]; then
  echo 'Create dashboard/.env before enabling automatic updates' >&2
  exit 2
fi
if [[ $(git -C "$repo" symbolic-ref --quiet --short HEAD || true) != main ]]; then
  echo 'Server checkout must be on main' >&2
  exit 2
fi

install -m 0755 "$repo/dashboard/auto_update.sh" /usr/local/sbin/ans-dashboard-auto-update
cat > /etc/systemd/system/ans-dashboard-auto-update.service <<EOF
[Unit]
Description=Update ANS Dashboard from GitLab main
Wants=network-online.target
After=network-online.target docker.service
Requires=docker.service

[Service]
Type=oneshot
User=root
TimeoutStartSec=20min
Environment="ANS_SKILL_REPO=$repo"
ExecStart=/usr/local/sbin/ans-dashboard-auto-update
EOF
cat > /etc/systemd/system/ans-dashboard-auto-update.timer <<'EOF'
[Unit]
Description=Check GitLab for ANS Dashboard updates every five minutes

[Timer]
OnBootSec=3min
OnUnitActiveSec=5min
RandomizedDelaySec=30s
Unit=ans-dashboard-auto-update.service

[Install]
WantedBy=timers.target
EOF
systemctl daemon-reload
systemctl enable --now ans-dashboard-auto-update.timer
echo "Auto-update installed for $repo; run systemctl start ans-dashboard-auto-update.service to check now"
