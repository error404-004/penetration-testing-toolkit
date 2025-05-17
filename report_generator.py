import os
import json
from datetime import datetime
from logger import log


def ensure_reports_dir():
    """Ensure the reports/ directory exists."""
    reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    return reports_dir


def generate_scan_report(target, protocols, open_ports, banners, start_time, end_time, metadata=None):
    """
    Generates a structured JSON report for vulnerability/network scans.

    Parameters:
    - target: str – IP or hostname.
    - protocols: list of str – e.g., ["IPv4", "TCP"].
    - open_ports: list of int.
    - banners: dict {port: service banner}.
    - start_time, end_time: datetime.
    - metadata: optional dict with additional scan info.

    Returns:
    - Path to the saved JSON report.
    """
    log(f"[+] Generating scan report for target {target}...")

    report_data = {
        "target": target,
        "protocols": protocols,
        "open_ports": open_ports,
        "banners": banners,
        "scan_start": start_time.isoformat(),
        "scan_end": end_time.isoformat(),
        "duration_seconds": (end_time - start_time).total_seconds(),
        "metadata": metadata or {}
    }

    reports_dir = ensure_reports_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"scan_report_{target.replace('.', '_')}_{timestamp}.json"
    filepath = os.path.join(reports_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2)

    log(f"[+] Scan report saved to {filepath}")
    return filepath


def generate_exploit_report(data, filename=None):
    """
    Generates a text report from exploitation results.

    Parameters:
    - data: list of strings to write.
    - filename: optional custom name.

    Returns:
    - Path to the saved text report.
    """
    log("[+] Generating exploitation report...")

    reports_dir = ensure_reports_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = filename or f"exploit_report_{timestamp}.txt"
    filepath = os.path.join(reports_dir, filename)

    with open(filepath, "w") as f:
        for entry in data:
            f.write(f"{entry}\n")

    log(f"[+] Exploitation report saved to {filepath}")
    return filepath