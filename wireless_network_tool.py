import subprocess
import re
import logging
import time
import threading
import argparse
import requests
import sys
import os
import json
import shutil

# Configure logging
logger = logging.getLogger("WirelessNetworkTool")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WirelessNetworkTool:
    IW_CMD = "iw"
    IWLIST_CMD = "iwlist"
    AIREPLAY_CMD = "aireplay-ng"
    NMCLI_CMD = "nmcli"
    WIGLE_API_URL = "https://api.wigle.net/api/v2/network/detail"  # Note: Update this if necessary

    def __init__(self, interfaces=None, wigle_user=None, wigle_pass=None):
        self.interfaces = interfaces or self.get_wireless_interfaces()
        self.wigle_user = wigle_user or os.getenv("WIGLE_USER")
        self.wigle_pass = wigle_pass or os.getenv("WIGLE_PASS")
        self._check_required_tools()

    def _check_required_tools(self):
        tools = [self.IW_CMD, self.IWLIST_CMD, self.NMCLI_CMD]
        for tool in tools:
            if not shutil.which(tool):
                logger.warning(f"Tool '{tool}' not found. Some features may not work.")

    def get_wireless_interfaces(self):
        try:
            output = subprocess.check_output([self.IW_CMD, "dev"], text=True)
            interfaces = re.findall(r'Interface\s+(\w+)', output)
            logger.info(f"Detected interfaces: {interfaces}")
            return interfaces
        except Exception as e:
            logger.error(f"Error detecting interfaces: {e}")
            return []

    def scan_networks(self, interface):
        try:
            result = subprocess.check_output(["sudo", self.IWLIST_CMD, interface, "scanning"], text=True)
            return self._parse_scan_output(result)
        except subprocess.CalledProcessError as e:
            logger.error(f"Scan error on {interface}: {e.output.strip()}")
        except FileNotFoundError:
            logger.error(f"'{self.IWLIST_CMD}' not found. Install wireless tools.")
        except Exception as e:
            logger.error(f"Scan failed: {e}")
        return []

    def _parse_scan_output(self, raw_output):
        networks = []
        for cell in raw_output.split("Cell ")[1:]:
            ssid = re.search(r'ESSID:"(.*?)"', cell)
            bssid = re.search(r'Address: ([0-9A-Fa-f:]{17})', cell)
            signal = re.search(r"Signal level=(-?\d+) dBm", cell)
            freq = re.search(r"Frequency:(\d+\.\d+)", cell)
            channel = re.search(r"Channel:(\d+)", cell)
            encryption = self._detect_encryption(cell)

            if ssid and bssid:
                networks.append({
                    "ssid": ssid.group(1) or "<hidden>",
                    "bssid": bssid.group(1),
                    "signal": int(signal.group(1)) if signal else None,
                    "frequency": float(freq.group(1)) if freq else None,
                    "channel": int(channel.group(1)) if channel else None,
                    "encryption": encryption
                })
        return networks

    def _detect_encryption(self, cell):
        if "WPA2" in cell:
            return "WPA2"
        elif "WPA" in cell:
            return "WPA"
        elif "Encryption key:on" in cell:
            return "WEP"
        return "Open"

    def scan_all_interfaces(self):
        return {iface: self.scan_networks(iface) for iface in self.interfaces}

    def real_time_scan(self, interval=30, stop_event=None):
        stop_event = stop_event or threading.Event()
        while not stop_event.is_set():
            yield self.scan_all_interfaces()
            time.sleep(interval)

    def geolocate_network(self, bssid):
        if not (self.wigle_user and self.wigle_pass):
            logger.warning("WiGLE credentials not provided.")
            return {}

        try:
            headers = {"Accept": "application/json"}
            params = {"netid": bssid.replace(":", "")}
            response = requests.get(self.WIGLE_API_URL, params=params, auth=(self.wigle_user, self.wigle_pass), headers=headers)
            response.raise_for_status()
            data = response.json()
            loc = data.get("results", [{}])[0]
            return {
                "latitude": loc.get("trilat"),
                "longitude": loc.get("trilong"),
                "address": loc.get("address"),
                "city": loc.get("city"),
                "state": loc.get("state"),
                "country": loc.get("country")
            }
        except requests.RequestException as e:
            logger.error(f"WiGLE API error: {e}")
            return {}

    def enrich_with_geolocation(self, scan_results):
        for iface, networks in scan_results.items():
            for net in networks:
                geo = self.geolocate_network(net["bssid"])
                net["geolocation"] = geo
        return scan_results

    def deauth_attack(self, interface, target_bssid, count=5):
        warning = input("⚠️ Type 'YES' to confirm DEAUTH attack (intrusive and may be illegal): ")
        if warning.strip().upper() != "YES":
            logger.info("Deauth attack aborted.")
            return
        try:
            subprocess.run(["sudo", self.AIREPLAY_CMD, "--deauth", str(count), "-a", target_bssid, interface], check=True)
            logger.info(f"Sent {count} deauth packets to {target_bssid} via {interface}")
        except Exception as e:
            logger.error(f"Deauth attack failed: {e}")

    def connect_to_network(self, ssid, password=None):
        try:
            cmd = [self.NMCLI_CMD, "dev", "wifi", "connect", ssid]
            if password:
                cmd += ["password", password]
            subprocess.run(cmd, check=True)
            logger.info(f"Connected to {ssid}")
        except Exception as e:
            logger.error(f"Connection to {ssid} failed: {e}")

def print_scan_results(scan_results):
    for iface, networks in scan_results.items():
        print(f"\nInterface: {iface}")
        if not networks:
            print("  No networks found.")
            continue
        for net in networks:
            geo = net.get("geolocation", {})
            print(f"  SSID: {net['ssid']}, BSSID: {net['bssid']}, "
                  f"Signal: {net.get('signal', 'N/A')} dBm, "
                  f"Channel: {net.get('channel', 'N/A')}, "
                  f"Frequency: {net.get('frequency', 'N/A')} GHz, "
                  f"Encryption: {net['encryption']}, "
                  f"Geo: {geo.get('latitude', 'N/A')}, {geo.get('longitude', 'N/A')}")

def main():
    parser = argparse.ArgumentParser(description="Wireless Network Tool - Scan and manage Wi-Fi networks.")
    parser.add_argument('--interfaces', help="Comma-separated interfaces (e.g., wlan0,wlan1)")
    parser.add_argument('--wigle-user', help="WiGLE API username")
    parser.add_argument('--wigle-pass', help="WiGLE API password")
    parser.add_argument('--scan', action='store_true', help="One-time scan")
    parser.add_argument('--realtime', action='store_true', help="Real-time scanning")
    parser.add_argument('--interval', type=int, default=30, help="Interval for real-time scan (default: 30)")
    parser.add_argument('--deauth', nargs=2, metavar=('IFACE', 'BSSID'), help="Perform deauth attack")
    parser.add_argument('--deauth-count', type=int, default=5, help="Deauth packet count (default: 5)")
    parser.add_argument('--connect', nargs='+', metavar=('SSID', 'PASSWORD'), help="Connect to a network")
    parser.add_argument('--export-report', help="Export scan results to JSON")

    args = parser.parse_args()

    interfaces = args.interfaces.split(",") if args.interfaces else None
    tool = WirelessNetworkTool(interfaces, args.wigle_user, args.wigle_pass)

    if args.deauth:
        iface, bssid = args.deauth
        tool.deauth_attack(iface, bssid, count=args.deauth_count)
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
                print(f"\n[Scan @ {time.strftime('%Y-%m-%d %H:%M:%S')}]")
                enriched = tool.enrich_with_geolocation(results)
                print_scan_results(enriched)
        except KeyboardInterrupt:
            stop_event.set()
            logger.info("Real-time scan interrupted by user.")
        return

    if args.scan:
        results = tool.scan_all_interfaces()
        enriched = tool.enrich_with_geolocation(results)
        print_scan_results(enriched)
        if args.export_report:
            try:
                with open(args.export_report, "w", encoding="utf-8") as f:
                    json.dump(enriched, f, indent=4)
                logger.info(f"Report saved to {args.export_report}")
            except Exception as e:
                logger.error(f"Could not write report: {e}")
        return

    parser.print_help()

if __name__ == "__main__":
    main()