# src/utils/nmap_runner.py

import subprocess
import datetime
import json
import os

def run_nmap_scan(target: str, ports: list = None, append_to: str = None) -> str:
    """
    Run an Nmap scan against the specified target.

    Args:
        target (str): The target IP or hostname.
        ports (list): Optional list of ports to scan.
        append_to (str): Optional path to a JSON file to append the output.

    Returns:
        str: Nmap stdout result.
    """
    nmap_cmd = ["nmap", "-sV"]
    if ports:
        ports_str = ",".join(str(p) for p in ports)
        nmap_cmd += ["-p", ports_str]
    nmap_cmd.append(target)

    print(f"\n📡 Running Nmap: {' '.join(nmap_cmd)}")

    try:
        result = subprocess.run(nmap_cmd, capture_output=True, text=True, check=False)
        output = result.stdout
        print("\n🧾 Nmap output:\n")
        print(output)

        if append_to and os.path.exists(append_to):
            try:
                with open(append_to, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                data['nmap_results'] = output
                with open(append_to, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                print(f"\n✅ Nmap results appended to {append_to}")
            except Exception as e:
                print(f"⚠️ Failed to append to report: {e}")
        else:
            filename = datetime.datetime.now().strftime("nmap_results_%Y%m%d_%H%M%S.txt")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"\n✅ Nmap results saved to {filename}")

        return output

    except FileNotFoundError:
        print("❌ Error: Nmap is not installed or not found in PATH.")
        return ""