# Drift Check - Re-running the Playbook Against the Device

## The Idea

Every playbook in the execution platform is built from the source of truth: the templates and NMS parameters in Git. That has a useful side effect. A playbook already knows what the device should look like. To find out whether a device still matches, run the use case against it again.

No separate comparison tool is needed. The playbook that deployed the change is the same playbook that detects drift.

## How the Drift Check Works

1. **Run the use case against the device** — The pipeline runs the use case's playbooks against the existing devices without changing them, in check mode.
2. **The playbook compares intent with reality** — It renders the intended config from the template and parameters in Git, and compares it with what is on the device.
3. **A difference is drift** — If the playbook would change something, or the validation fails, the device no longer matches the source of truth.
4. **The result is recorded** — The pipeline records the outcome per device and per use case, and sends it to the dashboard.

The check can be run on demand, or on a schedule so that drift is found without anyone looking for it.

## What a Drift Record Contains

Each result is stored as data, not as a log line someone has to read. For each device and use case:

| Field | Example |
|---|---|
| Device | `abc-dmz-sw-01` |
| Use case | `ntp` |
| Result | In sync / Drifted |
| Difference | The lines the playbook would add or remove |
| Source of truth version | The commit or release tag of the templates and parameters used |
| Pipeline run and time | Which run found it, and when |

Recording the version matters. It says what the device was compared against, so a drift result can always be explained.

## Reporting - The Dashboard

The drift data is reported to a dashboard. It turns drift from something found by accident into something that is measured.

- **Current state** — How many devices are in sync and how many have drifted, by use case, by environment and by device.
- **What drifted** — The difference for each drifted device, taken from the record.
- **Trend** — Whether drift is growing or shrinking over time, and which use cases drift most.
- **Age** — How long a device has been drifted since the drift was first seen.

The classic approach had no answer to "how much of the network matches the design?" The dashboard gives one.

## Remediation - Apply the Same Playbook Again

Remediation uses the same playbook that detected the drift. Running the use case normally, not in check mode, puts the device back to the source of truth.

- **Same content, same pipeline** — There is no separate remediation tooling. The playbook goes through the same stages and the same prechecks, validation and postchecks as a deployment. Production still sits behind the change gate.
- **Rollback is available** — The rollback playbooks cover a remediation like any other deployment.
- **The device is not always the one that is wrong** — Drift means the device and the source of truth disagree. If a break-fix change on the device was correct, reapplying the playbook would undo it. In that case the change goes into the templates or parameters first, through a branch and an MR with the code owner's approval. Then the playbook is applied, and the device and the source of truth agree again.

| Drift found | Which side is right | Action |
|---|---|---|
| Device was changed by hand | Source of truth | Run the playbook again to remediate |
| Device was changed by hand, and the change was needed | Device | Update the template or parameters through an MR, then run the playbook |
| Device was missed by an earlier rollout | Source of truth | Run the playbook again to remediate |

## What This Closes

Mapped to the challenges in [the problem statement](01-the-problem.md):

- **Configuration drift** — Drift is found by a scheduled run, measured on a dashboard and fixed by the same playbook. The break-fix loop is closed: the change is detected, and then either reverted or promoted into the source of truth.
- **NMS parameters** — A device pointing at an old NTP or syslog server shows up as drift against `parameters/`, without anyone having to check.
- **Source of truth** — The question "what should this device look like?" has an answer, and "does it?" has an answer too.

## Worked Example

The [NTP worked example](../examples/execution-platform/README.md#drift-check-dashboard-and-remediation) runs this end to end: it drifts three devices, finds them with a check-mode run, shows them on a dashboard, remediates them with the same playbook and checks again.
