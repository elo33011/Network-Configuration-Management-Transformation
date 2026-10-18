# Review - What the Approach Fixed, and What It Does Not

## Where We Started

Classic network configuration management treats the CLI template as the design. Templates sit in an execution platform with no version control, engineers paste config by hand, and two challenges follow ([the problem](01-the-problem.md)):

1. **Configuration drift** — Device config can no longer be correlated with the design. This includes the shared NMS parameters (NTP, SNMP, syslog), which have no single home and no governance.
2. **Automation built on snowflakes** — Automation consumes the same unmanaged templates, or a private copy of them, so it automates an instance of the design rather than the design.

## What the Approach Built

| # | Content | What it put in place |
|---|---|---|
| 1 | [The problem](01-the-problem.md) | The two challenges and the lost source of truth. |
| 2 | [Worked example](../examples/classic/README.md) | Baseline + environment templates, and the challenges shown with real diffs. |
| 3 | [Framework](03-config-management-framework.md) | Design, template, execution platform, device config and drift check, and how they relate. |
| 4 | [Templates as code](04-templates-as-code.md) | Templates and NMS parameters in Git. Branch, merge request, code owner approval. |
| 5 | [Execution platform](05-execution-platform.md) | Ansible on a self-built platform. Pipeline with Dev, QA and Prod, a required playbook set, tested rollback, merge rules, release tag and change gate. |
| 6 | [Worked example](../examples/execution-platform/README.md) | The NTP use case running through the playbook set, the rollback and the gates. |
| 7 | [Drift check](07-drift-check.md) | Re-run the playbook in check mode to find drift, report it on a dashboard and remediate with the same playbook. |

## How Each Challenge Was Addressed

| Challenge | Addressed by |
|---|---|
| Template has no history or owner | Templates in Git, changed only by merge request, approved by the code owner (4) |
| NMS parameters have no home or governance | Parameters in YAML files in the same repo, with the same governance (4) |
| Automation reads private or legacy copies | The Ansible repo is linked to the template repo, so playbooks read the governed template (5) |
| Automation is a snapshot of the design | Playbooks are built from the source of truth, so a change to it reaches every use case through the pipeline (5) |
| Changes are untested and unsafe | Dev and QA testing, a required precheck, validate and postcheck, a tested rollback, and a change gate for production (5, 6) |
| Drift is invisible | A scheduled check-mode run, with results on a dashboard (7) |
| Drift cannot be fixed consistently | Remediation applies the same playbook again, through the same pipeline (7) |

## What Is Now Controlled

Following the chain from design to device, each hop now has a control, except the first:

| Hop | Control |
|---|---|
| Design → Template | **None.** A person reads the design and writes the template. |
| Template → Execution platform | The Ansible repo reads the governed template repo (4, 5) |
| Execution platform → Device | The pipeline, with Dev, QA, Prod and the change gate (5) |
| Device → Template | The drift check (7) |

## What This Approach Does Not Address: The Design

The first hop is still open. The design is still not modeled.

The design in this approach is what it was in the classic one: diagrams, spreadsheets and documents that describe intent but are not connected to what gets deployed. A person turns that design into templates by hand. Everything built in this series starts at the template and goes down, and it is correct as far as it goes. It cannot see upstream of it.

This leaves drift in a place the drift check cannot see:

- **The drift check compares the device with the template, never with the design.** If a template does not match the design, whether because it was written wrongly or because the design changed and nobody updated it, every device is deployed from it and every drift check says "in sync".
- **A design change has no automatic path to the templates.** Someone has to notice, translate it and update the right template or parameter file. Nothing tells them they missed one.
- **The same fact is written more than once.** An address, a VLAN or a role exists in the design document, and again in a template or a parameter file. Two copies can disagree.
- **The design cannot be validated.** A document cannot be checked for a missing value or a conflicting one before it reaches a template.

The approach moves the source of truth from the device to the template. The design, which should be the source of truth, is still outside it.

## Next Step: Model the Design

The next step is to rewrite the design using a model approach, and to present it as a data schema. This is the approach taken in the [Automation Native Campus Network Design](https://github.com/elo33011/Automation-Native-Campus-Network-Design) repository, which expresses a network design as structured data:

- **Schemas** define what a design must contain, and which values are valid.
- **Data models** hold the values, as version-controlled files that are validated against the schemas.
- **Everything else is generated from the model** — templates render from it, and diagrams and other design artifacts are produced from it.

The core flow in that repository is:

- schema + values = data model
- data model + template = rendered config
- playbook + rendered config = deployed config
- validation = data model vs deployed config

Applied to this approach, the design stops being a document and becomes the top of the chain, under the same Git, merge request and code owner governance as the rest. The NMS parameters become part of the model. A design change is a change to the model, and it reaches the templates, the playbooks and the devices through the pipeline that already exists. The drift check can then compare the device with the design itself, not only with a template derived from it.
