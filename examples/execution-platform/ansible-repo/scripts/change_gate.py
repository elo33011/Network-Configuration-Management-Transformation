"""STUB for the firm's change management system. Prod only.
A real implementation would call the change management system's API with CHANGE_ID and the release tag.
Here: the gate passes only if CHANGE_APPROVED=true.
"""
import os, sys

change_id = os.environ.get("CHANGE_ID", "")
if not change_id or os.environ.get("CHANGE_APPROVED") != "true":
    print(f"CHANGE GATE FAILED: change '{change_id or 'none'}' is not approved. Production run blocked.")
    sys.exit(1)
print(f"CHANGE GATE PASSED: {change_id}")
