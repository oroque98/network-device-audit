from src.audit import audit_device
from src.parser import ParsedDevice


def test_missing_required_vlan_fails():
    parsed = ParsedDevice(name="SW1", vlans={10: "USERS"}, stack_members=2, ntp_configured=True, lldp_present=True, spanning_tree_present=True)
    baseline = {"required_vlans": [{"id": 10, "name": "USERS"}, {"id": 20, "name": "VOICE"}]}
    findings = audit_device(parsed, baseline)
    assert any(f.status == "FAIL" and f.check == "VLAN 20" for f in findings)
