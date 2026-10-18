#!/usr/bin/env bash
# Run one use case in one environment, in the order the pipeline enforces.
# Usage: run_usecase.sh <usecase> <dev|qa|prod> [deploy-only]
# Dev and QA: deploy phase, then rollback phase (rollback is tested). Prod: deploy phase only.
# deploy-only: deploy phase only in any environment (used for remediation).
set -euo pipefail
usecase=$1; env=$2
export ANSIBLE_CONFIG="$(cd "$(dirname "$0")/.." && pwd)/ansible.cfg"
cd "$(dirname "$0")/../usecases/$usecase"
run() { echo "=== $1 ($env)"; ansible-playbook -i "inventory/$env" "playbooks/$1.yml" | grep -E "^(PLAY RECAP|abc-)" ; }

for p in deploy-precheck deploy deploy-validate deploy-postcheck; do run "$p"; done
if [ "$env" != "prod" ] && [ "${3:-}" != "deploy-only" ]; then
  for p in rollback-precheck rollback rollback-validate rollback-postcheck; do run "$p"; done
fi
