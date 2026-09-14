from __future__ import annotations

import argparse
import getpass
from datetime import datetime
from pathlib import Path

import yaml

from src.audit import Finding, audit_device
from src.collector import collect_device, save_raw_outputs
from src.parser import parse_device
from src.report import write_summary_csv, write_text_report


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_example_outputs(example_dir: Path) -> dict[str, str]:
    mapping = {
        "show vlan": "show_vlan.txt",
        "show stacking": "show_stacking.txt",
        "show running-config": "show_running_config.txt",
        "show lldp neighbor-info": "show_lldp_neighbor-info.txt",
        "show spanning-tree": "show_spanning-tree.txt",
        "show interface brief": "show_interface_brief.txt",
    }
    outputs = {}
    for command, filename in mapping.items():
        path = example_dir / filename
        outputs[command] = path.read_text(encoding="utf-8") if path.exists() else ""
    return outputs


def print_device_findings(device: str, findings: list[Finding]) -> None:
    print(f"\n{device}")
    print("-" * len(device))
    for item in findings:
        print(f"[{item.status:<4}] {item.check}: {item.message}")


def run_demo(baseline: dict, report_dir: Path) -> int:
    outputs = load_example_outputs(Path("examples"))
    parsed = parse_device("LAB-SW01", outputs)
    findings = audit_device(parsed, baseline)
    print_device_findings("LAB-SW01", findings)
    write_text_report("LAB-SW01", findings, report_dir)
    write_summary_csv({"LAB-SW01": findings}, report_dir)
    return 0


def run_live(devices_cfg: dict, baseline: dict, report_dir: Path) -> int:
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")
    raw_dir = report_dir / "raw_cli"
    all_findings: dict[str, list[Finding]] = {}

    devices = devices_cfg.get("devices", [])
    if not devices:
        print("No devices found in devices file.")
        return 2

    for device in devices:
        name = device["name"]
        print(f"\n[RUNNING] {name} ({device['host']})")
        result = collect_device(device, username, password)
        save_raw_outputs(result, raw_dir)
        if not result.success:
            print(f"[FAILED] {name}: {result.error}")
            all_findings[name] = [Finding("HIGH", "Collection", "FAIL", result.error or "Unknown error")]
            continue

        parsed = parse_device(name, result.outputs)
        findings = audit_device(parsed, baseline)
        all_findings[name] = findings
        write_text_report(name, findings, report_dir)
        print_device_findings(name, findings)

    write_summary_csv(all_findings, report_dir)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only network device audit tool")
    parser.add_argument("--baseline", default="configs/baseline.yaml")
    parser.add_argument("--devices", default="configs/devices.example.yaml")
    parser.add_argument("--demo", action="store_true", help="Run using bundled fictional CLI outputs")
    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = Path("reports") / timestamp
    baseline = load_yaml(Path(args.baseline))

    if args.demo:
        return run_demo(baseline, report_dir)

    devices_cfg = load_yaml(Path(args.devices))
    return run_live(devices_cfg, baseline, report_dir)


if __name__ == "__main__":
    raise SystemExit(main())
