#!/usr/bin/env bash
# Put the simulated devices back to their starting state (old NTP server) and remove backups.
cd "$(dirname "$0")/../../sim"
for env in dev qa prod; do
  rm -f "$env"/*
  for n in 01 02; do
    cat > "$env/abc-$env-sw-$n.cfg" <<CFG
hostname abc-$env-sw-$n
feature ssh
ntp server 10.0.0.9 use-vrf management
logging server 10.0.0.20 use-vrf management
snmp-server community EXAMPLE-ONLY ro
CFG
  done
done
