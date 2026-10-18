# Execution Platform - Worked Example (NTP Use Case)

A runnable example of the [execution platform](../../docs/05-execution-platform.md), using NTP as the use case. All devices and values are made up. Devices are simulated as config files under `sim/`, so the playbooks run for real with `ansible-core` and no network gear.

## What Is Where

```text
execution-platform/
├── template-repo/                     # the governed repo from "templates as code", linked in
│   ├── templates/baseline/ntp.j2      #   NTP template
│   ├── parameters/ntp.yml             #   NTP servers: one file, one owner
│   └── CODEOWNERS
├── ansible-repo/
│   ├── .gitlab-ci.yml                 # pipeline: structure -> dev -> qa -> prod (illustrative, not executed)
│   ├── ansible.cfg
│   ├── scripts/
│   │   ├── check_usecase.py           # fails the pipeline if the playbook set is incomplete
│   │   ├── run_usecase.sh             # runs the playbooks in the enforced order
│   │   ├── change_gate.py             # STUB for the firm's change management system (prod)
│   │   └── reset_sim.sh               # puts the simulated devices back to the starting state
│   └── usecases/ntp/                  # one use case = its playbooks, inventory and variables
│       ├── playbooks/                 #   the eight required playbooks
│       ├── inventory/{dev,qa,prod}/
│       └── vars/main.yml              #   points at the linked template-repo
└── sim/{dev,qa,prod}/                 # simulated devices (one config file each)
```

## The Use Case

The use case sets the NTP servers on every device to what is in `template-repo/parameters/ntp.yml`. The devices start with an old server (`10.0.0.9`). `vars/main.yml` points at the template repo:

```yaml
template_repo: "{{ playbook_dir }}/../../../../template-repo"
ntp_template: "{{ template_repo }}/templates/baseline/ntp.j2"
ntp_parameters_file: "{{ template_repo }}/parameters/ntp.yml"
```

The playbook has no copy of the template or the servers. Changing an NTP server is an MR on `parameters/ntp.yml`, approved by its code owner. The pipeline then rolls it out.

| Playbook | What it does in this use case |
|---|---|
| `deploy-precheck` | Asserts the device config exists and NTP servers are defined. Takes a backup so rollback has something to restore. |
| `deploy` | Renders the template and replaces the NTP lines on the device. |
| `deploy-validate` | Straight after the deploy, asserts the device's NTP lines equal the rendered template. |
| `deploy-postcheck` | Asserts nothing else changed: everything except NTP lines equals the backup. |
| `rollback-precheck` | Asserts the backup exists. |
| `rollback` | Restores the backup. |
| `rollback-validate` | Straight after the rollback, asserts the NTP lines are back to the original. |
| `rollback-postcheck` | Asserts the device config is byte-identical to the backup. |

## Run It

```bash
pip install ansible-core
cd ansible-repo
scripts/reset_sim.sh
scripts/run_usecase.sh ntp dev
```

In Dev and QA the script runs the deploy phase and then the rollback phase, as the pipeline enforces. Output from a real run, one recap per playbook (both devices `failed=0`):

```text
=== deploy-precheck (dev)    ok=5 changed=1 failed=0
=== deploy (dev)             ok=4 changed=2 failed=0
=== deploy-validate (dev)    ok=4 changed=0 failed=0
=== deploy-postcheck (dev)   ok=2 changed=0 failed=0
=== rollback-precheck (dev)  ok=2 changed=0 failed=0
=== rollback (dev)           ok=1 changed=1 failed=0
=== rollback-validate (dev)  ok=2 changed=0 failed=0
=== rollback-postcheck (dev) ok=1 changed=0 failed=0
```

After the deploy phase the device has the servers from the template repo. After the rollback phase it is back to `10.0.0.9`, so rollback is proven to work before anything reaches `master`.

Production runs the deploy phase only:

```bash
scripts/run_usecase.sh ntp prod
```

```text
hostname abc-prod-sw-01
feature ssh
! BEGIN NTP (managed by pipeline)
ntp server 10.0.0.10 use-vrf management
ntp server 10.0.0.11 use-vrf management
! END NTP (managed by pipeline)
logging server 10.0.0.20 use-vrf management
snmp-server community EXAMPLE-ONLY ro
```

## The Pipeline Enforces the Rules

`.gitlab-ci.yml` maps the stages onto branches and the tag. It was not executed here, because there is no GitLab runner in this example. It parses as valid YAML, and the scripts it calls were run directly.

| Stage | Trigger | What the job does |
|---|---|---|
| `structure` | Any branch or tag | `check_usecase.py` on every use case |
| `dev` | Branch `dev` | `run_usecase.sh <use case> dev`: deploy phase, then rollback phase |
| `qa` | Branch `qa` | Fetches inventory and credentials from firm systems (stubs), then deploy phase and rollback phase |
| `prod` | Release tag | `change_gate.py` first, then the deploy phase only |

**Incomplete playbook set fails the pipeline.** With `rollback.yml` removed:

```text
FAIL ntp: missing rollback
```

**Change gate blocks production.** The gate here is a stub that passes only when `CHANGE_APPROVED=true`:

```text
CHANGE GATE FAILED: change 'none' is not approved. Production run blocked.
CHANGE GATE PASSED: CHG0012345
```

**Validate catches a device that does not match the template repo.** Someone edits an NTP server on `abc-dev-sw-01` after the deploy, and `deploy-validate` fails on that device only:

```text
fatal: [abc-dev-sw-01]: FAILED! ... "NTP on abc-dev-sw-01 does not match the template repo"
```

## What Is Simulated

- **Devices** are config files. The playbooks edit them with `lineinfile` and `blockinfile`. Real devices would use the vendor's Ansible collection, with the same playbook structure.
- **Change gate, inventory data store and vault** are stubs.
- **The pipeline file** is illustrative and not run.
- **The link to the template repo** is a folder next to the Ansible repo here. In the pipeline it is a checkout of the template repo before any job runs.
