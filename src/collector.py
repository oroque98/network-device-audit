from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

DEFAULT_COMMANDS = [
    "show interface brief",
    "show lacp interfaces",
    "show lldp neighbor-info",
    "show running-config",
    "show spanning-tree",
    "show stacking",
    "show system",
    "show version",
    "show vlan",
]


@dataclass
class CollectionResult:
    device: str
    host: str
    success: bool
    outputs: dict[str, str]
    error: str | None = None


def collect_device(
    device: dict,
    username: str,
    password: str,
    commands: Iterable[str] = DEFAULT_COMMANDS,
) -> CollectionResult:
    """Collect read-only CLI output from one network device."""
    name = device["name"]
    host = device["host"]
    params = {
        "device_type": device.get("device_type", "aruba_aoscx"),
        "host": host,
        "username": username,
        "password": password,
        "fast_cli": False,
    }

    connection = None
    try:
        from netmiko import ConnectHandler
        connection = ConnectHandler(**params)
        outputs: dict[str, str] = {}
        for command in commands:
            outputs[command] = connection.send_command(command, read_timeout=60)
        return CollectionResult(name, host, True, outputs)
    except Exception as exc:  # Netmiko raises several transport/auth exceptions
        return CollectionResult(name, host, False, {}, str(exc))
    finally:
        if connection:
            connection.disconnect()


def save_raw_outputs(result: CollectionResult, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = result.device.replace("/", "_")
    path = output_dir / f"{safe_name}.txt"

    with path.open("w", encoding="utf-8") as fh:
        fh.write(f"DEVICE: {result.device}\nHOST: {result.host}\n\n")
        if not result.success:
            fh.write(f"COLLECTION FAILED: {result.error}\n")
            return path
        for command, output in result.outputs.items():
            fh.write(f"{'=' * 78}\nCOMMAND: {command}\n{'=' * 78}\n")
            fh.write(output.rstrip() + "\n\n")
    return path
