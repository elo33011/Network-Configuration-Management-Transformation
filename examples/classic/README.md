# Classic Approach - Worked Example

A small, runnable example of the classic workflow and the two challenges described in [the problem statement](../../docs/01-the-problem.md). All devices and values are made up for illustration.

## Template Structure - Baseline + Environment

The configuration is split into two layers of CLI templates:

- **Baseline** — specific to the hardware platform (`nexus-9300`). Management, AAA, banner, CoPP, plus the network management system (NMS) parameters: NTP, syslog and SNMP. The same baseline applies in every environment.
- **Environment** — what the device needs to operate in a given environment. `datacenter` (jumbo MTU, vPC, server VLAN) or `dmz` (ACLs, port-security, storm-control, shut unused ports).

A device is built by rendering one baseline plus one environment template with a values file. A Data Center switch and a DMZ switch get the same baseline and different environment config.

| Path | What it is |
|---|---|
| `templates/baseline/nexus-9300.tmpl` | Platform baseline. |
| `templates/environment/datacenter.tmpl` | Data Center environment template. |
| `templates/environment/dmz.tmpl` | DMZ environment template. |
| `templates/baseline/nexus-9300-NEW.tmpl` | A copy of the baseline modified for a rollout and never merged back. |
| `templates/environment/dmz-NEW.tmpl` | A copy of the DMZ template modified after a design change. The original was never retired. |
| `values/*.yml` | Per-device variables filled in by the engineer. These include a copy of the NMS parameters (NTP, syslog, SNMP). |
| `reference/nms-parameters.csv` | The spreadsheet where someone once recorded the NMS parameters. |
| `automation/render_and_push.py` | The "automation": baseline + environment + values, then push. It also carries its own default SNMP community. |
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

### Drift in Network Management Parameters

The same drift happens to the NMS parameters. NTP, syslog and SNMP values are part of every baseline, so every device uses them. Searching this example for where they live:

```bash
grep -rnE "10\.0\.0\.(9|1[0-9]|2[0-9])\b|public123" . --exclude-dir=devices --exclude=README.md
```

```text
./automation/render_and_push.py:10:v.setdefault("snmp_community", "public123")
./values/dc-sw-01.yml:1:ntp_server: 10.0.0.10
./values/dc-sw-01.yml:2:syslog_server: 10.0.0.20
./values/dc-sw-01.yml:3:snmp_community: public123
./values/dmz-sw-01.yml:1:ntp_server: 10.0.0.10
./values/dmz-sw-01.yml:2:syslog_server: 10.0.0.20
./values/dmz-sw-01.yml:3:snmp_community: public123
./values/dmz-sw-02.yml:1:ntp_server: 10.0.0.11
./values/dmz-sw-02.yml:2:syslog_server: 10.0.0.20
./values/dmz-sw-02.yml:3:snmp_community: public123
./templates/baseline/nexus-9300-NEW.tmpl:10:logging server 10.0.0.25 use-vrf management
./reference/nms-parameters.csv:2:ntp_server,10.0.0.9,unknown,2021-03
./reference/nms-parameters.csv:3:syslog_server,10.0.0.20,unknown,2022-07
./reference/nms-parameters.csv:4:snmp_community,public123,unknown,2020-11
```

- **No single location** — The values sit in per-device values files, hard-coded in a template, in the automation script and in a spreadsheet. There are five different places for three parameters.
- **No governance** — Nothing records who changed a value, when, or who approved it. The spreadsheet's owner column says "unknown".
- **Changes are partial** — `dmz-sw-02` uses NTP server `10.0.0.11`, so someone changed it in one values file only. The spreadsheet still says `10.0.0.9`. Which one is correct cannot be answered from the data.
- **Hard-coded copies hide** — `nexus-9300-NEW.tmpl` points syslog at `10.0.0.25`, a value that appears in no values file. Updating the values files would never reach it.
- **Credentials sit in plain text** — The SNMP community string is stored in every one of those places.

These parameters have the widest reach of anything in the config, and they have no owner and no home.

## Challenge 2 - Automation Built on Snowflakes

`dmz-sw-01` and `dmz-sw-02` are the same role in the same environment, deployed by the same script. Besides hostname and management IP, they differ in:

```diff
- snmp-server community public123 ro
+ snmp-server user MONITOR network-operator auth sha EXAMPLE-ONLY
- logging server 10.0.0.20 use-vrf management
+ logging server 10.0.0.25 use-vrf management
- copp profile strict
+ copp profile moderate
-  10 permit tcp any 172.16.40.0/24 eq 443
+  10 permit tcp any 172.16.40.0/24 range 443 8443
-  storm-control broadcast level 1
+  storm-control broadcast level 5
```

### Side by Side - dmz-sw-01 vs dmz-sw-02

Same role, same environment (DMZ), same hardware platform, deployed by the same script. Only differing lines are shown. Each device section lists the template it was rendered from. A difference is a **per-device value** (expected, e.g. hostname and management IP), a **template divergence** (the templates themselves disagree, which is the snowflake) or an **NMS parameter** (the same shared value held in more than one place).

| Section | abc-dmz-sw-01 | abc-dmz-sw-02 | Why it differs |
|---|---|---|---|
| **Baseline** | `templates/baseline/nexus-9300.tmpl` | `templates/baseline/nexus-9300-NEW.tmpl` | |
| | `! baseline/nexus-9300.tmpl - hardware-platform baseline (identical for every environment)` | `! baseline/nexus-9300-NEW.tmpl - copied for the DMZ rollout, "improved" and never merged back` | ❌ template divergence |
| | `hostname abc-dmz-sw-01` | `hostname abc-dmz-sw-02` | per-device value |
| | `ntp server 10.0.0.10 use-vrf management` | `ntp server 10.0.0.11 use-vrf management` | ❌ NMS parameter, no single home |
| | `logging server 10.0.0.20 use-vrf management` | `logging server 10.0.0.25 use-vrf management` | ❌ template divergence |
| | `snmp-server community public123 ro` | `snmp-server user MONITOR network-operator auth sha EXAMPLE-ONLY` | ❌ template divergence |
| | ` ip address 10.1.0.21/24` | ` ip address 10.1.0.22/24` | per-device value |
| | `copp profile strict` | `copp profile moderate` | ❌ template divergence |
| **Environment** | `templates/environment/dmz.tmpl` | `templates/environment/dmz-NEW.tmpl` | |
| | `! environment/dmz.tmpl - config for operating in the DMZ` | `! environment/dmz-NEW.tmpl - copied after the web tier moved; old one never retired` | ❌ template divergence |
| | ` 10 permit tcp any 172.16.40.0/24 eq 443` | ` 10 permit tcp any 172.16.40.0/24 range 443 8443` | ❌ template divergence |
| | ` storm-control broadcast level 1` | ` storm-control broadcast level 5` | ❌ template divergence |

**Reading it**

- Of the 10 differing lines, 2 are per-device values, 1 is an NMS parameter and 7 come from the templates.
- Each device section points at a different template file. Nothing records which one is the standard.
- The divergence cannot be spotted from the device config alone. It takes a manual diff of both templates.

Regenerate the table (printed to stdout) with:

```bash
python3 automation/compare.py /dev/stdout \
  abc-dmz-sw-01 templates/baseline/nexus-9300.tmpl templates/environment/dmz.tmpl values/dmz-sw-01.yml \
  abc-dmz-sw-02 templates/baseline/nexus-9300-NEW.tmpl templates/environment/dmz-NEW.tmpl values/dmz-sw-02.yml
```

### Why It Matters

The script is correct in both cases. It rendered whichever baseline and environment templates it was pointed at. Now two baselines and two DMZ templates claim to be the standard, and nothing records which is current. The "same baseline everywhere" property exists only by convention, and the first copy-and-modify breaks it. The new baseline also needs a `snmp_auth` variable that existing values files do not have.
