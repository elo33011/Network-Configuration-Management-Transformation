# Network Configuration Management Transformation

My journey from CLI templates and copy-paste to a version-controlled
source of truth for network configuration.

## Executive Summary

Classic network configuration management treats the CLI template as the design. Templates sit in an execution platform with no version control, and engineers paste config onto devices by hand. This causes two problems, and the inconsistency they create causes network outages and impact:

- **Configuration drift** — Device config can no longer be correlated with the design, including shared NMS parameters (NTP, SNMP, syslog) that have no single home and no governance.
- **Automation built on snowflakes** — Automation consumes the same unmanaged templates, so it automates an instance of the design, not the design.

The approach put in place:

- **Framework** — Design, template, execution platform, device config and drift check, with one direction of authority.
- **Templates as code** — Templates and NMS parameters in Git. Every change is a merge request approved by the code owner.
- **Execution platform** — Self-built Ansible platform with a pipeline: Dev, QA and Prod stages, a required deploy and rollback playbook set, a tested rollback, and a change gate for production.
- **Drift check** — Re-run the playbook in check mode, report drift on a dashboard, and remediate by applying the same playbook again.

An add-on shows how to build new use cases with three agents (architect, developer and code reviewer) under the same governance.

What it does not address: the design itself. It is still not modeled, so drift between the design and the templates remains. The next step is to rewrite the design as a data model with schemas, as in the Automation Native Campus Network Design repo.

## Contents

1. [The Problem: When the Template Is Not the Truth](docs/01-the-problem.md)
2. [Worked example: baseline + environment templates](examples/classic/README.md)
3. [The Approach: A Configuration Management Framework](docs/03-config-management-framework.md)
4. [Templates as Code: Moving Templates to Git](docs/04-templates-as-code.md)
5. [The Execution Platform: Ansible, Built In-House](docs/05-execution-platform.md)
6. [Worked example: NTP use case on the execution platform](examples/execution-platform/README.md)
7. [Drift Check: Re-running the Playbook Against the Device](docs/07-drift-check.md)
8. [Review: What the Approach Fixed, and What It Does Not](docs/08-review-and-next-step.md)
9. [Add-on: Building Use Cases with Agentic Coding](docs/09-agentic-use-case-development.md)

## Who this is for

Network engineers and architects who have felt configuration drift
and want a practical path out of it.
