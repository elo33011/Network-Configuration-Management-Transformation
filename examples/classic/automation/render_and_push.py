"""Typical 'automation' built around unmanaged templates: baseline + environment -> push.
It knows template paths and a values file - nothing about the design behind them.
Usage: render_and_push.py <baseline.tmpl> <environment.tmpl> <values.yml>
"""
import sys, yaml
from jinja2 import Template

baseline, environment, values = sys.argv[1:4]
v = yaml.safe_load(open(values))
v.setdefault("snmp_community", "public123")  # the script carries its own copy, 'just in case'
cfg = "\n".join(Template(open(p).read()).render(**v) for p in (baseline, environment))
print(cfg)  # stand-in for: netmiko.send_config_set(cfg.splitlines())
