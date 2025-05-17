# src/main.py

import argparse
import json
from config import load_config
from logger import setup_logger
from nmap_runner import run_nmap_scan
from report_generator import report_generator
from exploitation_tool import exploitation_tool
from vulnerability_scanner import main as vuln_scan_main
from wireless_network_tool import WirelessNetworkTool, print_scan_results
import threading
import time
import sys

def run_report_generation(target: str, open_ports: list):
    scan_results = {
        "open_ports": open_ports,
        "banner_info": {}  # Replace this with actual service info if available
    }
    report_filename = report_generator.generate_report(target, scan_results)

    choice = input("Run Nmap and include in report? (y/N) ").strip().lower()
    if choice == 'y':
        run_nmap_scan(target, ports=open_ports, append_to=report_filename)

def run_wireless_tool(args):
    interfaces = args.interfaces.split(",") if args.interfaces else None

    tool = WirelessNetworkTool(
        interfaces=interfaces,
        wigle_user=args.wigle_user,
        wigle_pass=args.wigle_pass
    )

    if args.deauth:
        interface, bssid = args.deauth
        tool.deauth_attack(interface, bssid, count=args.deauth_count)
        return

    if args.connect:
        ssid = args.connect[0]
        password = args.connect[1] if len(args.connect) > 1 else None
        tool.connect_to_network(ssid, password)
        return

    if args.realtime:
        stop_event = threading.Event()
        try:
            for results in tool.real_time_scan(interval=args.interval, stop_event=stop_event):
                print(f"\nScan at {time.strftime('%Y-%m-%d %H:%M:%S')}")
                enriched = tool.enrich_with_geolocation(results)
                print_scan_results(enriched)
        except KeyboardInterrupt:
            stop_event.set()
            print("Real-time scanning stopped.")
        return

    if args.scan:
        results = tool.scan_all_interfaces()
        enriched = tool.enrich_with_geolocation(results)
        print_scan_results(enriched)
        if args.export_report:
            with open(args.export_report, 'w', encoding='utf-8') as f:
                json.dump(enriched, f, indent=2)
        return

    print("No action specified for wireless tool. Use --scan or --realtime.")

def main():
    config = load_config()
    logger = setup_logger("Main", config["log_file"])

    parser = argparse.ArgumentParser(description="Penetration Testing Toolkit")
    subparsers = parser.add_subparsers(dest="command", help="Available modules")

    # Exploitation module
    exploit_parser = subparsers.add_parser("exploit", help="Run exploitation tool")
    exploit_parser.add_argument("--args", nargs=argparse.REMAINDER)

    # Vulnerability scanner
    subparsers.add_parser("vulnscan", help="Run vulnerability scanner")

    # Wireless tool
    wireless_parser = subparsers.add_parser("wireless", help="Wireless network module")
    wireless_parser.add_argument('--interfaces')
    wireless_parser.add_argument('--wigle-user')
    wireless_parser.add_argument('--wigle-pass')
    wireless_parser.add_argument('--scan', action='store_true')
    wireless_parser.add_argument('--realtime', action='store_true')
    wireless_parser.add_argument('--interval', type=int, default=30)
    wireless_parser.add_argument('--deauth', nargs=2, metavar=('INTERFACE', 'BSSID'))
    wireless_parser.add_argument('--deauth-count', type=int, default=5)
    wireless_parser.add_argument('--connect', nargs='+', metavar=('SSID', 'PASSWORD'))
    wireless_parser.add_argument('--export-report')

    # Report generator + optional Nmap
    report_parser = subparsers.add_parser("report", help="Generate report and optionally run Nmap")
    report_parser.add_argument("target", help="Target hostname or IP")
    report_parser.add_argument("--ports", help="Comma-separated open ports", required=True)

    args = parser.parse_args()

    if args.command == "exploit":
        logger.info("Launching exploitation module...")
        sys.argv = [sys.argv[0]] + (args.args if args.args else [])
        exploitation_tool.main()

    elif args.command == "vulnscan":
        logger.info("Launching vulnerability scanner...")
        vuln_scan_main()

    elif args.command == "wireless":
        logger.info("Launching wireless module...")
        run_wireless_tool(args)

    elif args.command == "report":
        ports = [int(p) for p in args.ports.split(",")]
        run_report_generation(args.target, ports)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()