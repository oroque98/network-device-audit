from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class ParsedDevice:
    name: str
    vlans: dict[int, str] = field(default_factory=dict)
    stack_members: int | None = None
    ntp_configured: bool = False
    lldp_present: bool = False
    spanning_tree_present: bool = False
    up_interfaces_without_description: list[str] = field(default_factory=list)


def parse_vlan(output: str) -> dict[int, str]:
    """Best-effort Aruba AOS-CX VLAN parser."""
    vlans: dict[int, str] = {}
    for line in output.splitlines():
        # Typical examples: "10 USERS ..." or "10    USERS"
        match = re.match(r"^\s*(\d{1,4})\s+([A-Za-z0-9_.:-]+)", line)
        if match:
            vlan_id = int(match.group(1))
            if 1 <= vlan_id <= 4094:
                vlans[vlan_id] = match.group(2)
    return vlans


def parse_stack_member_count(output: str) -> int | None:
    members: set[str] = set()
    for line in output.splitlines():
        match = re.match(r"^\s*(\d+)\s+", line)
        if match and any(token in line.lower() for token in ("active", "standby", "member", "ready")):
            members.add(match.group(1))
    return len(members) if members else None


def parse_up_without_description(output: str) -> list[str]:
    """Conservative parser for 'show interface brief'.

    Flags interfaces that appear up/up and have no trailing description text.
    Exact columns vary by AOS-CX release, so this is intentionally best-effort.
    """
    findings: list[str] = []
    for line in output.splitlines():
        if not re.match(r"^\s*\d+/\d+/\d+", line):
            continue
        fields = line.split()
        if len(fields) < 3:
            continue
        states = [f.lower() for f in fields[1:5]]
        if states.count("up") >= 1:
            # Treat a short line as likely lacking a description.
            if len(fields) <= 5:
                findings.append(fields[0])
    return findings


def parse_device(name: str, outputs: dict[str, str]) -> ParsedDevice:
    running = outputs.get("show running-config", "")
    lldp = outputs.get("show lldp neighbor-info", "")
    stp = outputs.get("show spanning-tree", "")

    return ParsedDevice(
        name=name,
        vlans=parse_vlan(outputs.get("show vlan", "")),
        stack_members=parse_stack_member_count(outputs.get("show stacking", "")),
        ntp_configured=bool(re.search(r"^\s*ntp\s+server\b", running, flags=re.I | re.M)),
        lldp_present=bool(lldp.strip()) or bool(re.search(r"\blldp\b", running, flags=re.I)),
        spanning_tree_present=bool(stp.strip()) or bool(re.search(r"spanning-tree", running, flags=re.I)),
        up_interfaces_without_description=parse_up_without_description(outputs.get("show interface brief", "")),
    )
