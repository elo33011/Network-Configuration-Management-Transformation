#!/usr/bin/env bash
# Build the starting state for the drift example:
#   1. every device is deployed from the source of truth (in sync),
#   2. then three things happen that the source of truth does not know about.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
export ANSIBLE_CONFIG="$root/ansible.cfg"
"$root/scripts/reset_sim.sh"
cd "$root/usecases/ntp"
for env in dev qa prod; do
  limit=all; [ "$env" = prod ] && limit=abc-prod-sw-02          # prod-sw-01 is missed by the rollout
  for p in deploy-precheck deploy; do ansible-playbook -i "inventory/$env" "playbooks/$p.yml" --limit "$limit" >/dev/null; done
done
sim="$root/../sim"
sed -i 's/^ntp server 10.0.0.11 /ntp server 10.0.0.99 /' "$sim/dev/abc-dev-sw-02.cfg"            # hand-edited server
sed -i 's/^! END NTP.*/ntp server 10.0.0.50 use-vrf management\n&/' "$sim/qa/abc-qa-sw-02.cfg"  # extra server added in a break-fix
rm -f "$sim"/*/*.pre-ntp-change
echo "drift simulated: dev-sw-02 (edited), qa-sw-02 (extra server), prod-sw-01 (missed rollout)"
