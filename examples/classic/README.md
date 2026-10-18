# Classic Approach - Worked Example

A small, runnable example of the classic workflow and the two challenges described in [the problem statement](../../docs/01-the-problem.md). All devices and values are made up for illustration.

## Template Structure - Baseline + Environment

The configuration is split into two layers of CLI templates:

- **Baseline** — specific to the hardware platform (`nexus-9300`). Management, NTP, syslog, SNMP, AAA, banner, CoPP. The same baseline applies in every environment.
- **Environment** — what the device needs to operate in a given environment. `datacenter` (jumbo MTU, vPC, server VLAN) or `dmz` (ACLs, port-security, storm-control, shut unused ports).

A device is built by rendering one baseline plus one environment template with a values file. A Data Center switch and a DMZ switch get the same baseline and different environment config.

| Path | What it is |
|---|---|
| `templates/baseline/nexus-9300.tmpl` | Platform baseline. |
| `templates/environment/datacenter.tmpl` | Data Center environment template. |
| `templates/environment/dmz.tmpl` | DMZ environment template. |
| `templates/baseline/nexus-9300-NEW.tmpl` | A copy of the baseline modified for a rollout and never merged back. |
| `templates/environment/dmz-NEW.tmpl` | A copy of the DMZ template modified after a design change. The original was never retired. |
| `values/*.yml` | Per-device variables filled in by the engineer. |
| `automation/render_and_push.py` | The "automation": baseline + environment + values, then push. |
| `devices/` | Intended, running and deployed configs. |

## Reproduce

```bash
pip install jinja2 pyyaml
python3 automation/render_and_push.py \
  templates/baseline/nexus-9300.tmpl templates/environment/dmz.tmpl values/dmz-sw-01.yml
```

## The Split Works - dc-sw-01 vs dmz-sw-01

Rendered from the same baseline, the first 20 lines differ only by the per-device values:

```diff
< hostname abc-dc-sw-01
> hostname abc-dmz-sw-01
...
<  ip address 10.1.0.11/24
>  ip address 10.1.0.21/24
```

Everything after the baseline is environment config. The structure is sound. The problem is that both layers are still unmanaged templates.

## Challenge 1 - Configuration Drift

`dmz-sw-01`, intended (templates) vs running (device) after a break-fix:

```diff
  20 deny ip any any log
+ 15 permit tcp any 172.16.40.0/24 eq 8080
 ...
+interface Ethernet1/30
+ no shutdown
+ switchport access vlan 400
```

An extra ACL entry and a re-enabled port were added directly on the device. Neither is in any template or values file, and the second one undoes the "shut unused ports" intent of the DMZ environment. The next deployment from the template silently removes the fix, or nobody knows to check.

## Challenge 2 - Automation Built on Snowflakes

Side-by-side with template references: [comparison-dmz-sw-01-vs-sw-02.md](comparison-dmz-sw-01-vs-sw-02.md).

`dmz-sw-01` and `dmz-sw-02` are the same role in the same environment, deployed by the same script. Besides hostname and management IP, they differ in:

```diff
- snmp-server community public123 ro
+ snmp-server user MONITOR network-operator auth sha EXAMPLE-ONLY
- copp profile strict
+ copp profile moderate
-  10 permit tcp any 172.16.40.0/24 eq 443
+  10 permit tcp any 172.16.40.0/24 range 443 8443
-  storm-control broadcast level 1
+  storm-control broadcast level 5
```

The script is correct in both cases. It rendered whichever baseline and environment templates it was pointed at. Now two baselines and two DMZ templates claim to be the standard, and nothing records which is current. The "same baseline everywhere" property exists only by convention, and the first copy-and-modify breaks it. The new baseline also needs a `snmp_auth` variable that existing values files do not have.
