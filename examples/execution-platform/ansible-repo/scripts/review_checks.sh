#!/usr/bin/env bash
# Mechanical checks a reviewer runs before reading the code. Exit non-zero if any fail.
# Usage: review_checks.sh <usecase>
set -uo pipefail
usecase=$1
root="$(cd "$(dirname "$0")/.." && pwd)"
export ANSIBLE_CONFIG="$root/ansible.cfg"
fail=0
ok()  { echo "PASS  $*"; }
bad() { echo "FAIL  $*"; fail=1; }

# 1. full playbook set, inventory and vars present
python3 "$root/scripts/check_usecase.py" "$root/usecases/$usecase" >/dev/null && ok "full playbook set present" || bad "playbook set incomplete"

# 2. no hard-coded IP addresses in playbooks: NMS values must come from the template repo
if grep -nE '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' "$root/usecases/$usecase"/playbooks/*.yml >/dev/null; then
  bad "hard-coded IP address in a playbook:"; grep -nE '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' "$root/usecases/$usecase"/playbooks/*.yml
else ok "no hard-coded IP addresses in playbooks"; fi

# 3. idempotent: a second deploy against an already-deployed device changes nothing
"$root/scripts/reset_sim.sh"
cd "$root/usecases/$usecase"
for p in deploy-precheck deploy; do ansible-playbook -i inventory/dev "playbooks/$p.yml" >/dev/null 2>&1; done
second=$(ansible-playbook -i inventory/dev playbooks/deploy.yml 2>&1 | grep -E '^abc-' | grep -vc 'changed=0')
[ "$second" = "0" ] && ok "deploy is idempotent (second run changed=0)" || bad "deploy is not idempotent"

# 4. the full dev cycle passes: deploy phase then rollback phase
"$root/scripts/reset_sim.sh"
"$root/scripts/run_usecase.sh" "$usecase" dev >/dev/null 2>&1 && ok "dev cycle passes (deploy then rollback)" || bad "dev cycle fails"
"$root/scripts/reset_sim.sh"
exit $fail
