# Ansible repository - conventions for Claude

This repo is the execution platform's automation content. Every automation is a **use case** under `usecases/<name>/`: its playbooks, inventory and variables.

## Rules every use case follows

- **Required playbook set**, run in this order by the pipeline:
  `deploy-precheck` -> `deploy` -> `deploy-validate` -> `deploy-postcheck`, and
  `rollback-precheck` -> `rollback` -> `rollback-validate` -> `rollback-postcheck`.
  `scripts/check_usecase.py` fails the pipeline if any is missing.
- **Templates and NMS parameters come from the linked template repo** (`../template-repo`), never from a copy and never hard-coded in a playbook. Do not edit the template repo from here: a template or parameter change is a merge request to that repo, approved by its code owner.
- **`deploy` is idempotent.** Run with `--check --diff` it changes nothing and reports what it would change. That is the drift check, so a deploy that always reports a change is a bug.
- **Rollback is tested, not assumed.** In Dev and QA the pipeline runs the rollback phase after the deploy phase.
- **No credentials in the repo.** Credentials come from the vault in QA and Prod.
- Use cases are independent: do not edit another use case's directory.
- The reference implementation is `usecases/ntp/`. Read it before designing or building a new use case.

## Commands

- `scripts/check_usecase.py usecases/<name>` - structure check
- `scripts/run_usecase.sh <name> dev` - deploy phase then rollback phase against the simulated dev devices
- `scripts/review_checks.sh <name>` - structure, no hard-coded values, idempotency, dev cycle
- `scripts/reset_sim.sh` - reset the simulated devices

## Workflow

Work happens on a branch from `dev`. Nothing is merged without a merge request and the pipeline passing. Agents follow this workflow like everyone else: the three project agents in `.claude/agents/` (architect, developer, reviewer) never merge, tag a release or touch `master`.
