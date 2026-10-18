"""Side-by-side comparison of two devices built by render_and_push.py.
Shows only the lines that differ, the template each device section came from, and whether the
difference is a per-device value (expected) or the templates themselves diverging (a snowflake).
Usage: compare.py <markdown-out> <label_a> <baseline_a> <env_a> <values_a> <label_b> <baseline_b> <env_b> <values_b>
"""
import sys, difflib, yaml
from jinja2 import Template

out, *args = sys.argv[1:]
(la, ba, ea, va), (lb, bb, eb, vb) = [args[i:i + 4] for i in (0, 4)]
va, vb = yaml.safe_load(open(va)), yaml.safe_load(open(vb))


def render(path, values):
    return Template(open(path).read()).render(**values).splitlines()


md = [f"| Section | {la} | {lb} | Why it differs |", "|---|---|---|---|"]
for kind, pa, pb in (("Baseline", ba, bb), ("Environment", ea, eb)):
    a, b = render(pa, va), render(pb, vb)
    # render B's template with A's values: what is left is template divergence, not device values
    b_same_values = render(pb, {**vb, **va})
    md.append(f"| **{kind}** | `{pa}` | `{pb}` | |")
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes():
        if tag == "equal":
            continue
        for k in range(max(i2 - i1, j2 - j1)):
            l = a[i1 + k] if i1 + k < i2 else ""
            r = b[j1 + k] if j1 + k < j2 else ""
            template_diff = (l != (b_same_values[j1 + k] if j1 + k < j2 else ""))
            why = "❌ template divergence" if template_diff else "per-device value"
            md.append(f"| | `{l}` | `{r}` | {why} |")
open(out, "w").write("\n".join(md) + "\n")
