# The Problem: When the Template Is Not the Truth

## The classic workflow

For most of my career, network configuration management followed a familiar pattern.

1. **Design the network.** An architect or engineer decides on the topology, routing, VLANs, security policy, and so on.
2. **Write a CLI template.** The design is turned into configuration snippets, with the site-specific parts replaced by variables: hostnames, IP addresses, VLAN IDs, and interface names.
3. **Fill in the variables.** For each deployment, an engineer supplies the values, turning the generic template into a parameterized one.
4. **Paste it onto the device.** The engineer logs in to each device, one at a time, and copies and pastes the rendered configuration piece by piece.

The templates themselves lived in a traditional execution platform. It stored them and ran them, but it had no version control, no history of who changed what, and no way to compare today's template with last quarter's.

This workflow works, up to a point. The trouble starts after day one.

## Where it breaks: configuration drift

Networks don't stand still, and each kind of change widens the gap between design and reality.

- **Design changes.** Sometimes the engineer updates the template and deploys it. Sometimes they create a new template instead, so now there are two versions of the "standard" with no clear lineage.
- **Break-fix changes.** At 2 a.m. during an outage, nobody edits a template first. The engineer fixes the problem directly on the device, and the template never hears about it.
- **Partial rollouts.** A change goes to some devices and not others. The template says one thing, half the estate says another, and nothing records which half.

Each of these is reasonable on its own. Together they produce **configuration drift**: the running config on a device can no longer be traced back to the design that was meant to produce it.

## The real cost: the lost source of truth

Drift is more than untidy configs. It means the question "what *should* this device look like?" no longer has a reliable answer.

- The template may be stale, because it wasn't updated after a fix.
- The device may be the odd one out, because it missed a change.
- Neither can be proven right, because nothing records history or intent.

Once that happens, the source of truth is gone. Audits turn into manual comparisons. Upgrades and migrations carry hidden risk, because you don't know what is really on the devices. Troubleshooting slows down, because "standard" no longer means anything. Every new change adds to the problem.

The tooling wasn't the root cause. The *model* was: templates treated as one-off deployment aids, not as a versioned, authoritative definition of the network.
