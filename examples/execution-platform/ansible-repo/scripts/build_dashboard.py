"""Build the drift dashboard (one self-contained HTML file) from the drift run files.
Usage: build_dashboard.py <output.html> [--through <run-id>]
Reads drift/runs/*.json. The latest run shown is the last one at or before --through.
"""
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
out = Path(sys.argv[1])
through = sys.argv[sys.argv.index("--through") + 1] if "--through" in sys.argv else None

runs = [json.loads(p.read_text()) for p in sorted((root / "drift" / "runs").glob("*.json"))]
if through:
    runs = [r for r in runs if r["run_id"] <= through]
template = (Path(__file__).parent / "dashboard_template.html").read_text()
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(template.replace("__RUNS__", json.dumps(runs)))
print(f"wrote {out} ({len(runs)} run(s), latest {runs[-1]['run_id']})")
