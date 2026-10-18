#!/usr/bin/env bash
# Remediation: apply the same use case again (deploy phase), through the same prechecks, validation and postchecks.
# Usage: remediate.sh <usecase> <env>
exec "$(dirname "$0")/run_usecase.sh" "$1" "$2" deploy-only
