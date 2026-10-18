# Templates as Code - Moving Templates to Git

## The Move

The first step of the approach is to move the templates out of the classic execution platform and into a new Git repository. The execution platform stops being the place templates are stored. It becomes a consumer of them: it deploys what is in the repo and nothing else.

| | Classic | Templates as code |
|---|---|---|
| Where templates live | Inside the execution platform, as its repository of templates | A Git repository |
| How a change is made | Edit the template in the platform, or create a new one | Branch, change, merge request, merge |
| History | None | Every change is a commit: who, when, why |
| Who approves | Nobody, or whoever has access | The code owner of that template |
| Which version is the standard | Unknown | The default branch (`master`) |

## Key Concept - Manage Templates as Code

Templates are treated the same way software teams treat source code. The repo is the single place a template exists, and a change to a template is a change to code.

- **One location** — A template exists once, in the repo. No copies in the execution platform, in scripts or on engineers' laptops.
- **Full history** — Version control records every change and gives the ability to compare any two versions or roll back.
- **Reviewed before it takes effect** — A change cannot reach the standard without being read by someone else.

## Change Workflow - Branch and Merge to Master

No change is made directly on `master`. The default branch is protected, so the only way to change a template is:

1. **Branch** — Create a branch from `master` for the change, for example `fix/dmz-storm-control`.
2. **Change** — Edit the template on the branch. This includes break-fix changes that were first made on a device.
3. **Merge request (MR)** — Open an MR to merge the branch into `master`. The MR shows exactly what changed, line by line.
4. **Review and approval** — The code owner of the changed template approves the MR.
5. **Merge** — After approval, the branch is merged into `master`. `master` is now the new standard.

A new template version no longer means a new copy of the template. The `nexus-9300-NEW.tmpl` and `dmz-NEW.tmpl` pattern from the [worked example](../examples/classic/README.md) has no place in this workflow: there is one `nexus-9300.tmpl`, and its history shows what changed.

## Code Owners - Approval Based on Ownership

Not everyone can approve a change to every template or parameter file. The repo uses a code owners file to map each file to the team that owns it. The MR can only be approved by the owner of the files it touches.

Example (illustrative team names, GitLab-style `CODEOWNERS`):

```text
[Baseline]
templates/baseline/          @network-platform-team

[Environment - Data Center]
templates/environment/datacenter.tmpl   @dc-network-team

[Environment - DMZ]
templates/environment/dmz.tmpl          @security-network-team

[NMS Parameters]
parameters/ntp.yml           @infrastructure-services-team
parameters/syslog.yml        @monitoring-team
parameters/snmp.yml          @monitoring-team
```

How this works in practice:

- **Baseline** — Owned by the team responsible for the hardware platform. A change here affects every environment, so it needs their approval.
- **Environment** — Each environment template is owned by the team accountable for that environment, such as Data Center or DMZ.
- **NMS parameters** — Each parameter file is owned by the team that runs that service, such as the monitoring team for syslog and SNMP.
- **A change touching several templates** — Needs approval from each owner involved.
- **The author cannot approve their own change** — Ownership decides who approves, and the approver is never the author.

This gives governance by construction. The question "who is allowed to change this?" is answered in a file under version control, and enforced by the platform on every MR.

## Network Management Parameters - Same Approach

The NMS parameters (NTP, SNMP, syslog) are handled the same way as templates. They are stored in the Git repo as data, in separate YAML files, and a change to them goes through the same branch, MR and merge workflow.

```text
parameters/
├── ntp.yml
├── syslog.yml
└── snmp.yml
```

```yaml
# parameters/ntp.yml
ntp_servers:
  - 10.0.0.10
  - 10.0.0.11
```

- **One location per parameter** — Each value is defined once, in one file. Templates reference the variable. A value is no longer copied into per-device values files, scripts or spreadsheets, and it is no longer hard-coded in a template.
- **Separate files by concern** — NTP, syslog and SNMP are changed for different reasons, by different owners. Separate files let each have its own owner and its own review.
- **Same governance** — A change to `ntp.yml` is a change to code. It needs a branch, an MR and the approval of the file's code owner.
- **Credentials are referenced, not stored** — Sensitive values such as the SNMP community or credentials are held as a reference to a secret store. The YAML file does not contain the secret itself.

## What This Solves

Mapped to the challenges in [the problem statement](01-the-problem.md):

- **Configuration drift** — The repo's default branch is the standard, so "which template is current" has one answer. A change made on a device during break-fix is promoted back by an MR, with review, instead of being lost.
- **Snowflakes** — Copy-and-modify is replaced by branch-and-merge. Variations are visible in history and in review, not hidden in separate files.
- **Governance** — Ownership of each template and each parameter file is explicit, and approval is enforced.
- **NMS parameters with no home** — Each parameter has one file in the repo and one owner. A change is reviewed, approved and recorded, and a value cannot be changed in one place and missed in another.

## What Is Still Open

Moving templates and parameters to Git manages the intent. The device is still only compared with that intent if someone checks it. The next content covers the drift check.
