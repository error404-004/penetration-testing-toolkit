# tests/test_port_scanner.py

import pytest
from unittest.mock import patch, MagicMock
from port_scanner import port_scanner


def test_port_scanner_initialization():
    scanner = port_scanner.PortScanner(timeout=2, max_threads=50)
    assert scanner.timeout == 2
    assert scanner.max_threads == 50


@patch("socket.socket")
def test_scan_open_port(mock_socket):
    mock_instance = MagicMock()
    mock_instance.connect_ex.return_value = 0  # Simulate open port
    mock_socket.return_value = mock_instance

    scanner = port_scanner.PortScanner()
    result = scanner._scan_port("127.0.0.1", 80)
    assert result["status"] == "open"
    assert result["port"] == 80


@patch("socket.socket")
def test_scan_closed_port(mock_socket):
    mock_instance = MagicMock()
    mock_instance.connect_ex.return_value = 1  # Simulate closed port
    mock_socket.return_value = mock_instance

    scanner = port_scanner.PortScanner()
    result = scanner._scan_port("127.0.0.1", 81)
    assert result["status"] == "closed"
    assert result["port"] == 81


@patch("modules.port_scanner.PortScanner._scan_port")
def test_scan_single_host(mock_scan_port):
    mock_scan_port.side_effect = lambda ip, port: {
        "ip": ip,
        "port": port,
        "status": "open" if port == 22 else "closed"
    }

    scanner = port_scanner.PortScanner()
    results = scanner.scan_single_host("192.168.1.1", [22, 80])

    assert any(r["port"] == 22 and r["status"] == "open" for r in results)
    assert any(r["port"] == 80 and r["status"] == "closed" for r in results)


@patch("modules.port_scanner.PortScanner.scan_single_host")
def test_scan_multiple_hosts(mock_scan_single_host):
    mock_scan_single_host.side_effect = lambda ip, ports: [
        {"ip": ip, "port": p, "status": "open" if p % 2 == 0 else "closed"} for p in ports
    ]

    scanner = port_scanner.PortScanner()
    results = scanner.scan_multiple_hosts(["10.0.0.1", "10.0.0.2"], [21, 22])

    assert "10.0.0.1" in results
    assert "10.0.0.2" in results
    assert results["10.0.0.1"][0]["status"] in ["open", "closed"]