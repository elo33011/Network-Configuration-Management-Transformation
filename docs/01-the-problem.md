# The Problem - Why Classic Network Configuration Management Drifts

## Classic Approach - How It Works

Classic network configuration management treats the CLI template as the design. The workflow is:

1. Network design is agreed — topology, routing, VLANs, security policy.
2. A CLI template is created from the design. Site-specific values are replaced by variables, such as hostname, IP address, VLAN ID and interface name.
3. Values are filled in per deployment, turning the template into a parameterized template.
4. A network engineer logs in to each device and copy-pastes the rendered configuration, piece by piece.

The templates are stored in a classic execution platform. The platform can store and run them, but it has no version control and no capability to track changes. There is no history of who changed what, when and why.

## What's Wrong With It?

The workflow works on day one. The problem is everything after day one.

- **Design changes** — Either the existing template is updated and redeployed, or a new template is created next to the old one. Both leave no clear lineage of which version is the standard.
- **Break-fix changes** — Under outage pressure, the fix is made directly on the device. The template is never updated.
- **Partial rollouts** — A change reaches some devices and not others. Nothing records which ones.

Each action is reasonable on its own. Together they cause configuration drift: the actual device configuration can no longer be correlated with the design.

## The Real Impact - Source of Truth Is Lost

Drift is not just untidy configuration. It removes the answer to the question "what should this device look like?"

- The template may be stale, because a fix was never written back.
- The device may be the exception, because it missed a change.
- Neither can be proven right, because no history and no intent were recorded.

Once this happens, the source of truth is lost. Audits become manual comparisons, upgrades and migrations carry hidden risk, and troubleshooting slows down because "standard" no longer means anything.

The root cause is the model, not the tooling. Templates are treated as deployment aids rather than as a versioned, authoritative definition of the network. Consistency depends on engineers keeping templates and devices aligned by discipline, and discipline does not scale.
