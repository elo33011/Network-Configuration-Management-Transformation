"""Typical 'automation' built around an unmanaged template: renders it and pushes it.
It knows the template path and the values file - nothing about the design behind them.
"""
import sys, yaml
from jinja2 import Template

template_path, values_path = sys.argv[1], sys.argv[2]
cfg = Template(open(template_path).read()).render(**yaml.safe_load(open(values_path)))
print(cfg)  # stand-in for: netmiko.send_config_set(cfg.splitlines())
