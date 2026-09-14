# Network Device Audit Tool

A read-only network auditing project built with **Python**, **Netmiko** and **YAML**. It connects to network devices over SSH, collects operational CLI data, parses selected outputs, compares the device state with a configurable baseline, and generates human-readable and CSV reports.

The bundled examples are fictional and safe to publish.

## Why this project exists

Manual network audits are repetitive and inconsistent when an engineer must log in to many switches and run the same commands one by one. This project automates that workflow while keeping the collection process read-only.

```text
Device inventory
      |
      v
Python + Netmiko
      |
      v
Read-only show commands
      |
      v
Parser
      |
      v
Baseline checks
      |
      +----> PASS / WARN / FAIL
      |
      v
TXT + CSV reports
```

## Current capabilities

- SSH collection with Netmiko
- Aruba AOS-CX oriented command set
- YAML device inventory
- YAML compliance baseline
- VLAN presence and name validation
- Stack member validation
- NTP, LLDP and Spanning Tree checks
- Basic interface-description hygiene check
- Raw CLI archival
- Per-device text reports
- Consolidated CSV report
- Offline demo mode using fictional outputs
- Basic unit tests

## Project structure

```text
network-device-audit/
├── configs/
│   ├── baseline.yaml
│   └── devices.example.yaml
├── examples/
│   └── fictional CLI outputs
├── reports/
├── src/
│   ├── audit.py
│   ├── collector.py
│   ├── parser.py
│   └── report.py
├── tests/
├── main.py
├── requirements.txt
└── README.md
```

## Installation

Python 3.10+ is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Demo mode

The easiest way to test the project is with the included fictional CLI outputs. No network equipment is required.

```bash
python main.py --demo
```

Example output:

```text
LAB-SW01
--------
[PASS] VLAN 10: Present as 'USERS'
[PASS] VLAN 20: Present as 'VOICE'
[PASS] VLAN 30: Present as 'IOT'
[PASS] Stack: 2 members detected
[PASS] NTP: NTP server configured
[PASS] LLDP: LLDP evidence found
[PASS] Spanning Tree: STP evidence found
```

Reports are written under a timestamped directory inside `reports/`.

## Live mode

Copy the example device inventory and replace the fictional addresses with lab devices you are authorized to access.

```bash
cp configs/devices.example.yaml configs/devices.local.yaml
```

Example:

```yaml
devices:
  - name: LAB-SW01
    host: 192.0.2.10
    device_type: aruba_aoscx
```

Then run:

```bash
python main.py --devices configs/devices.local.yaml
```

Credentials are requested interactively and are **not stored in the repository**.

## Baseline example

```yaml
required_vlans:
  - id: 10
    name: USERS
  - id: 20
    name: VOICE
  - id: 30
    name: IOT

stack:
  minimum_members: 2

checks:
  require_ntp: true
  require_lldp: true
  require_spanning_tree: true
```

## Example report

```text
NETWORK DEVICE AUDIT - LAB-SW01
========================================================================

[PASS] [INFO  ] VLAN 10: Present as 'USERS'
[PASS] [INFO  ] VLAN 20: Present as 'VOICE'
[PASS] [INFO  ] VLAN 30: Present as 'IOT'
[PASS] [INFO  ] Stack: 2 members detected
[PASS] [INFO  ] NTP: NTP server configured
[PASS] [INFO  ] LLDP: LLDP evidence found
[PASS] [INFO  ] Spanning Tree: STP evidence found
```

## Security principles

This repository is intentionally designed around safe operational practices:

- Read-only `show` commands only
- No configuration changes
- No credentials in source files
- Example IP addresses use documentation ranges
- Example hostnames and CLI outputs are fictional
- Production data should be sanitized before being committed

Never publish real credentials, internal IP addressing, serial numbers, topology information, customer names, corporate hostnames, or raw production configurations without authorization.

## Roadmap

Potential future improvements:

- Cisco IOS / IOS-XE support
- Junos support
- TextFSM / TTP structured parsing
- LLDP topology discovery
- LACP consistency checks
- JSON output
- HTML dashboard
- NetBox integration
- FastAPI REST interface
- CI pipeline for tests and linting

## Skills demonstrated

`Python` · `Netmiko` · `SSH` · `Aruba AOS-CX` · `YAML` · `Network Automation` · `Switching` · `LLDP` · `LACP` · `STP` · `VLANs` · `Network Compliance` · `Troubleshooting`

## Disclaimer

Use this tool only on systems you own or are explicitly authorized to access. Validate parsers and baseline rules in a lab before using them operationally.
