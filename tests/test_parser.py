from src.parser import parse_vlan


def test_parse_vlan():
    output = """\n1 DEFAULT_VLAN_1 up\n10 USERS up\n20 VOICE up\n"""
    assert parse_vlan(output) == {1: "DEFAULT_VLAN_1", 10: "USERS", 20: "VOICE"}
