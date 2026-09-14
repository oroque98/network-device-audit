from __future__ import annotations

from dataclasses import dataclass

from .parser import ParsedDevice


@dataclass
class Finding:
    severity: str
    check: str
    status: str
    message: str


def _finding(status: str, check: str, message: str, severity: str = "INFO") -> Finding:
    return Finding(severity=severity, check=check, status=status, message=message)


def audit_device(parsed: ParsedDevice, baseline: dict) -> list[Finding]:
    findings: list[Finding] = []

    for required in baseline.get("required_vlans", []):
        vlan_id = int(required["id"])
        expected_name = str(required.get("name", "")).strip()
        actual_name = parsed.vlans.get(vlan_id)
        if actual_name is None:
            findings.append(_finding("FAIL", f"VLAN {vlan_id}", "Required VLAN is missing", "HIGH"))
        elif expected_name and actual_name.upper() != expected_name.upper():
            findings.append(
                _finding(
                    "WARN",
                    f"VLAN {vlan_id}",
                    f"Name mismatch: expected '{expected_name}', found '{actual_name}'",
                    "MEDIUM",
                )
            )
        else:
            findings.append(_finding("PASS", f"VLAN {vlan_id}", f"Present as '{actual_name}'"))

    minimum = baseline.get("stack", {}).get("minimum_members")
    if minimum is not None:
        if parsed.stack_members is None:
            findings.append(_finding("WARN", "Stack", "Could not determine stack member count", "MEDIUM"))
        elif parsed.stack_members < int(minimum):
            findings.append(
                _finding(
                    "FAIL",
                    "Stack",
                    f"Expected at least {minimum} members, found {parsed.stack_members}",
                    "HIGH",
                )
            )
        else:
            findings.append(_finding("PASS", "Stack", f"{parsed.stack_members} members detected"))

    checks = baseline.get("checks", {})
    if checks.get("require_ntp"):
        findings.append(
            _finding("PASS" if parsed.ntp_configured else "FAIL", "NTP", "NTP server configured" if parsed.ntp_configured else "No NTP server found", "HIGH" if not parsed.ntp_configured else "INFO")
        )
    if checks.get("require_lldp"):
        findings.append(
            _finding("PASS" if parsed.lldp_present else "WARN", "LLDP", "LLDP evidence found" if parsed.lldp_present else "No LLDP evidence found", "MEDIUM" if not parsed.lldp_present else "INFO")
        )
    if checks.get("require_spanning_tree"):
        findings.append(
            _finding("PASS" if parsed.spanning_tree_present else "FAIL", "Spanning Tree", "STP evidence found" if parsed.spanning_tree_present else "No STP evidence found", "HIGH" if not parsed.spanning_tree_present else "INFO")
        )

    if baseline.get("interface_hygiene", {}).get("warn_on_up_without_description"):
        for interface in parsed.up_interfaces_without_description:
            findings.append(_finding("WARN", "Interface description", f"{interface} appears up without a description", "LOW"))

    return findings
