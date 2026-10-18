#!/usr/bin/env bash
# Drift check: re-run the use case's deploy playbook against the devices in check mode.
# Nothing is changed. A host that reports a change differs from the source of truth.
# Usage: drift_check.sh <usecase> <env> <run-id>   (appends to drift/runs/<run-id>.json)
set -euo pipefail
usecase=$1; env=$2; run_id=$3
root="$(cd "$(dirname "$0")/.." && pwd)"
raw="$(mktemp)"
export ANSIBLE_CONFIG="$root/ansible.cfg" ANSIBLE_CALLBACKS_ENABLED=drift_json DRIFT_RAW="$raw"
cd "$root/usecases/$usecase"
ansible-playbook -i "inventory/$env" playbooks/deploy.yml --check --diff >/dev/null
python3 "$root/scripts/drift_record.py" "$usecase" "$env" "$run_id" "$raw"
rm -f "$raw"
