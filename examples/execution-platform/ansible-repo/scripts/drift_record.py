"""Turn raw check-mode results into drift records and append them to the run file.
Usage: drift_record.py <usecase> <env> <run-id> <raw.json>
"""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

usecase, env, run_id, raw = sys.argv[1:5]
root = Path(__file__).resolve().parents[2]
tr = root / "template-repo"
# Version of the source of truth the devices were compared against: a content hash of the files
# the use case reads. (In the real platform: the commit or release tag of the template repo.)
digest = hashlib.sha256()
for f in ("templates/baseline/ntp.j2", "parameters/ntp.yml"):
    digest.update((tr / f).read_bytes())
sot_version = digest.hexdigest()[:8]

run_file = root / "drift" / "runs" / f"{run_id}.json"
run_file.parent.mkdir(parents=True, exist_ok=True)
run = json.loads(run_file.read_text()) if run_file.exists() else {
    "run_id": run_id,
    "time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    "source_of_truth_version": sot_version,
    "records": [],
}
for device, res in sorted(json.load(open(raw)).items()):
    status = "error" if res["failed"] else "drifted" if res["changed"] else "in sync"
    run["records"].append({
        "device": device, "environment": env, "use_case": usecase,
        "result": status, "difference": res["diff"],
    })
run_file.write_text(json.dumps(run, indent=2) + "\n")
print(f"{run_id} {env}: " + ", ".join(f"{r['device']}={r['result']}" for r in run["records"] if r["environment"] == env))
