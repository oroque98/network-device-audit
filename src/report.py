from __future__ import annotations

import csv
from pathlib import Path

from .audit import Finding


def write_text_report(device: str, findings: list[Finding], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{device}_audit.txt"
    with path.open("w", encoding="utf-8") as fh:
        fh.write(f"NETWORK DEVICE AUDIT - {device}\n")
        fh.write("=" * 72 + "\n\n")
        for item in findings:
            fh.write(f"[{item.status:<4}] [{item.severity:<6}] {item.check}: {item.message}\n")
    return path


def write_summary_csv(results: dict[str, list[Finding]], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "audit_summary.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["device", "status", "severity", "check", "message"])
        for device, findings in results.items():
            for item in findings:
                writer.writerow([device, item.status, item.severity, item.check, item.message])
    return path
