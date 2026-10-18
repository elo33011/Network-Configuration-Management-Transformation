# Comparison - abc-dmz-sw-01 vs abc-dmz-sw-02

Same role, same environment (DMZ), same hardware platform, deployed by the same script. Only lines that differ are shown. Identical lines are omitted.

Each device section lists the template it was rendered from. A difference is either a **per-device value** (expected, e.g. hostname and management IP) or a **template divergence** (the two templates themselves disagree, which is the snowflake).

| Section | abc-dmz-sw-01 | abc-dmz-sw-02 | Why it differs |
|---|---|---|---|
| **Baseline** | `templates/baseline/nexus-9300.tmpl` | `templates/baseline/nexus-9300-NEW.tmpl` | |
| | `! baseline/nexus-9300.tmpl - hardware-platform baseline (identical for every environment)` | `! baseline/nexus-9300-NEW.tmpl - copied for the DMZ rollout, "improved" and never merged back` | ❌ template divergence |
| | `hostname abc-dmz-sw-01` | `hostname abc-dmz-sw-02` | per-device value |
| | `snmp-server community public123 ro` | `snmp-server user MONITOR network-operator auth sha EXAMPLE-ONLY` | ❌ template divergence |
| | ` ip address 10.1.0.21/24` | ` ip address 10.1.0.22/24` | per-device value |
| | `copp profile strict` | `copp profile moderate` | ❌ template divergence |
| **Environment** | `templates/environment/dmz.tmpl` | `templates/environment/dmz-NEW.tmpl` | |
| | `! environment/dmz.tmpl - config for operating in the DMZ` | `! environment/dmz-NEW.tmpl - copied after the web tier moved; old one never retired` | ❌ template divergence |
| | ` 10 permit tcp any 172.16.40.0/24 eq 443` | ` 10 permit tcp any 172.16.40.0/24 range 443 8443` | ❌ template divergence |
| | ` storm-control broadcast level 1` | ` storm-control broadcast level 5` | ❌ template divergence |

## Reading It

- 2 of the 8 differing lines are per-device values. The other 6 come from the templates.
- Each device section points at a different template file. Nothing records which one is the standard.
- The divergence cannot be spotted from the device config alone. It takes a manual diff of both templates.

Regenerate with:

```bash
python3 automation/compare.py comparison-dmz-sw-01-vs-sw-02.md \
  abc-dmz-sw-01 templates/baseline/nexus-9300.tmpl templates/environment/dmz.tmpl values/dmz-sw-01.yml \
  abc-dmz-sw-02 templates/baseline/nexus-9300-NEW.tmpl templates/environment/dmz-NEW.tmpl values/dmz-sw-02.yml
```
