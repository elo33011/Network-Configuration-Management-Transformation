# NTP use case - design

> Example of the architect agent's output (`usecase-architect`). It describes the NTP use case in this example and shows the shape of a design: specific enough for the developer agent to build from, short enough to review in a few minutes.

## Requirement

Every device uses the NTP servers defined in the template repo. When the servers change, a merge request to the parameter file is enough: the use case rolls it out and keeps it correct. Out of scope: NTP authentication, and devices outside the `dev`, `qa` and `prod` inventories.

## Inputs

| Input | Path in the template repo | Exists |
|---|---|---|
| NTP template | `templates/baseline/ntp.j2` | Yes |
| NTP servers | `parameters/ntp.yml` (owner: infrastructure services team) | Yes |

No new template or parameter is needed.

## Playbook design

| Playbook | What it does | Fails when |
|---|---|---|
| `deploy-precheck` | Confirms the device config exists and NTP servers are defined. Takes a backup. | Config is missing, or `ntp_servers` is empty |
| `deploy` | Renders the template and rewrites the device's NTP lines inside a managed block. | Never changes anything if the device already matches |
| `deploy-validate` | Compares the device's NTP lines with the rendered template. | Any difference |
| `deploy-postcheck` | Compares everything except NTP lines with the backup. | Anything other than NTP changed |
| `rollback-precheck` | Confirms the backup exists. | Backup is missing |
| `rollback` | Restores the backup. | - |
| `rollback-validate` | Compares the device's NTP lines with the backup's. | Any difference |
| `rollback-postcheck` | Compares the whole device config with the backup. | Any difference |

## Idempotency and drift

`deploy` builds the new config as a list of lines and writes it only if it differs from the device. A second run reports no change. Run with `--check --diff` it reports what it would change, which is the drift check.

## Rollback

`deploy-precheck` copies the device config to a backup before any change. `rollback` restores that copy.

## Test plan

- **Dev** - Deploy phase, then rollback phase, on the dev devices. Deliberately edit an NTP server on one device and confirm `deploy-validate` fails.
- **QA** - The same, with inventory from the network inventory data store.

## Production considerations

Low risk, but it touches every device. Release in one run only after QA passes. The change gate should show the old and new server lists from the parameter file's merge request.
