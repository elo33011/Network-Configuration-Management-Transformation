"""Records, per host, whether a run changed (or would change, in check mode) anything, and the diff.
Enable with ANSIBLE_CALLBACKS_ENABLED=drift_json and set DRIFT_RAW to the output file.
"""
import difflib
import json
import os

from ansible.plugins.callback import CallbackBase

DOCUMENTATION = """
    name: drift_json
    type: aggregate
    short_description: write per-host change and diff data as JSON
    description:
      - Used by the drift check. A check-mode run that reports a change means the device differs from the source of truth.
"""


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "aggregate"
    CALLBACK_NAME = "drift_json"
    CALLBACK_NEEDS_ENABLED = True

    def __init__(self):
        super().__init__()
        self.hosts = {}

    def _host(self, result):
        return self.hosts.setdefault(result._host.get_name(), {"changed": False, "failed": False, "diff": []})

    def v2_runner_on_ok(self, result):
        host, res = self._host(result), result._result
        host["changed"] = host["changed"] or bool(res.get("changed"))
        for d in res.get("diff") or []:
            if isinstance(d, dict) and "before" in d and "after" in d:
                for line in difflib.unified_diff(d["before"].splitlines(), d["after"].splitlines(), lineterm="", n=0):
                    if not line.startswith(("---", "+++", "@@")):
                        host["diff"].append(line)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self._host(result)["failed"] = True

    def v2_runner_on_unreachable(self, result):
        self._host(result)["failed"] = True

    def v2_playbook_on_stats(self, stats):
        with open(os.environ["DRIFT_RAW"], "w") as f:
            json.dump(self.hosts, f, indent=2)
