PENETRATION TESTING TOOLKIT

*COMPANY* - CODTECH IT SOLUTIONS

*NAME* - DEEPAYAN DEY

*INTERN ID* - CT04DL977

*DOMAIN* - CYBER SECURITY AND ETHICAL HACKING

*DURATION* - 4 WEEKS

*MENTOR* - NEELA SANTOSH

---
##OUTPUT

![Image](https://github.com/user-attachments/assets/89ce4b50-4052-47da-9909-aff2771028b1)

![Image](https://github.com/user-attachments/assets/fd4cae53-7054-4745-a14e-5c98462f3642)

----

# 🛡️ Penetration Testing Toolkit

A modular and extensible Python-based penetration testing framework designed for ethical hacking, vulnerability scanning, exploitation, brute-forcing, and wireless network auditing. Built for security researchers and red team professionals who need automation and flexibility.

---

## 🚀 Features

- 🔍 **Vulnerability Scanner**: Fingerprint services, match CVEs using NVD, and generate JSON/HTML reports.
- 💣 **Exploitation Tool**: Easily spawn reverse shells with configurable payloads.
- 🔑 **Brute Forcer**: HTTP and SSH brute-forcing with customizable user/pass lists.
- 🌐 **Wireless Network Tool**: Scan for networks, geolocate via WiGLE API, perform deauth attacks, and connect to WiFi.
- 🧠 **Modular CLI**: Each module is independently runnable and configurable via CLI.
- 🛠️ **Reporting Engine**: Auto-generate detailed reports for audit purposes.
- 📄 **Configurable**: Default values can be overridden via `config.json`.

---

## 📦 Installation

```bash
git clone https://github.com/error404-004/penetration-testing-toolkit.git
cd penetration-testing-toolkit
pip install -r requirements.txt

🧪 Running the Toolkit
General Usage (CLI launcher)
bash
python src/main.py --module exploit --args --target <IP>

Or if installed via setup:

bash 
pentoolkit --module exploit --args --target <IP>



🔍 Module Overview

✅ Vulnerability Scanner
bash
python src/modules/vulnerability_scanner.py
Scans for open ports and banners

Matches vulnerabilities using the CVE database (NVD)

Generates JSON and optionally HTML reports

💣 Exploitation Tool
bash
python src/modules/exploitation_tool.py --target 192.168.1.5 --port 4444 --shell bash

Launches a reverse shell payload to a listener

Supports Linux/Windows/OSX shells

🔑 Brute Force Module :
bash
python src/modules/brute_forcer.py
Supports:

HTTP brute-force

SSH brute-force

Accepts user/password lists

Supports delay and proxy settings

📡 Wireless Network Tool
bash
python src/modules/wireless_network_tool.py --interfaces wlan0 --scan

Passive scan of nearby networks

WiGLE API integration (optional geolocation)

Real-time scanning (--realtime)

Deauthentication attacks (--deauth)

Connect to network (--connect SSID PASSWORD)

⚙️ Configuration
You can define defaults in config.json:

{
  "default_ip": "127.0.0.1",
  "default_port": 4444,
  "default_os": "linux",
  "default_shell": "bash",
  "log_file": "pentest.log"
}

📝 Reporting
Reports are generated in JSON format and saved in the reports/ directory. Optional Nmap results can be appended.

📁 Project Structure:
├── __init__.py                  
├── __init__2.py               
├── brute_forcer.py                
├── config.py                  
├── exploitation.py        
├── INSTALLATION.md                 
├── logger.py              
├── main.py                  
├── nmap_runner.py                  
├── port_scanner.py 
├── README.md              
├── report_generator.py       
├── requirements.txt              
├── setup.py             
├── test_brute_forcer.py        
├── test_exploitation_tool.py                
├── test_port_scanner.py               
├── test_vulnerability_scanner.py
├── test_wireless_network_tool.py              
├── USAGE.md               
├── vulnerability_scanner.py               
└── wireless_network_tool.py
                


🤝 Contributing
Fork the repository

Create your feature branch (git checkout -b feature/new-feature)

Commit your changes (git commit -am 'Add new feature')

Push to the branch (git push origin feature/new-feature)

Open a pull request 🚀


🙏 Acknowledgments
Offensive Security

NIST NVD

WiGLE.net

Python Nmap

📬 Contact
Author: Deepayan Dey
GitHub: @error404-004
Email: your.pandaaahacker007@gmail.com



