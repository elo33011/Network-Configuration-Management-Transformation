# Classic Approach - Worked Example

A small, runnable example of the classic workflow and the two challenges described in [the problem statement](../../docs/01-the-problem.md).

## Files

| Path | What it is |
|---|---|
| `templates/access-switch.tmpl` | The original parameterized CLI template (Jinja2 syntax). |
| `templates/access-switch-NEW.tmpl` | A copy, modified after a design change. The original was never retired. |
| `values/*.yml` | Per-device variable values filled in by the engineer. |
| `automation/render_and_push.py` | The "automation": renders a template with a values file and pushes it. |
| `devices/f01-acc-01.intended.cfg` | What the template says device f01 should look like. |
| `devices/f01-acc-01.running.cfg` | What f01 actually looks like after a break-fix. |
| `devices/f02-acc-01.deployed.cfg` | Same role as f01, deployed from the NEW template. |

## Reproduce

```bash
pip install jinja2 pyyaml
python3 automation/render_and_push.py templates/access-switch.tmpl values/hq-f01-acc-01.yml
```

## Challenge 1 - Configuration Drift

Compare what the template intended for f01 with what is running on it:

```diff
 vlan 200
  name VOICE
+vlan 999
+ name TEMP-CAMERA-FIX
 ...
  switchport mode access
+ storm-control broadcast level 5
```

Both lines were added directly on the device during break-fix. Neither exists in any template or values file. The running config can no longer be correlated with the design, and the next deployment from the template will silently remove the fix.

## Challenge 2 - Automation Built on Snowflakes

`f01` and `f02` are the same role (floor access switch), and both were deployed by the same script. Beyond the expected hostname, VLAN and uplink values, they differ in the following ways:

```diff
- snmp-server community public123 RO
+ snmp-server group MONITOR v3 priv
+ ntp server 10.0.0.11
```

The script is correct in both cases. It faithfully rendered whichever template it was pointed at. The problem is that two templates now claim to be the standard for the same role, and nothing records which is current. The automation is an instance of the design at the time each template was written, so it produces snowflakes at the speed of automation.

Note also that the NEW template needs a variable (`ntp_server_2`) the old values files do not have, so every existing values file must be hand-edited before the new template can be used.
