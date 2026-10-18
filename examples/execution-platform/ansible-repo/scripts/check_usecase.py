"""Pipeline structure gate: a use case must provide the full playbook set.
Usage: check_usecase.py <usecase-dir>
"""
import sys
from pathlib import Path

REQUIRED = [
    "deploy-precheck", "deploy", "deploy-validate", "deploy-postcheck",
    "rollback-precheck", "rollback", "rollback-validate", "rollback-postcheck",
]
usecase = Path(sys.argv[1])
missing = [n for n in REQUIRED if not (usecase / "playbooks" / f"{n}.yml").exists()]
for need in ("inventory", "vars"):
    if not (usecase / need).is_dir():
        missing.append(f"{need}/")
if missing:
    print(f"FAIL {usecase.name}: missing {', '.join(missing)}")
    sys.exit(1)
print(f"OK   {usecase.name}: full playbook set present")
