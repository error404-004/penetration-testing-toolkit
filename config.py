# config.py

import json
import os

DEFAULT_CONFIG = {
    "default_ip": "127.0.0.1",
    "default_port": 4444,
    "default_os": "linux",
    "default_shell": "bash",
    "log_file": "pentest.log",
    "proxy": {},               # Proxy settings, e.g., {"http": "http://127.0.0.1:8080"}
    "timeout": 5,              # Timeout in seconds for network requests
    "retry_limit": 3,          # Number of retries for attacks/scans
    "log_level": "INFO"        # Logging level (DEBUG, INFO, WARNING, ERROR)
}

def load_config(config_path="config.json"):
    """
    Loads configuration from JSON file and merges with defaults.
    Returns the configuration dictionary.
    """
    if not os.path.exists(config_path):
        print(f"Config file {config_path} not found. Using default configuration.")
        return DEFAULT_CONFIG.copy()

    try:
        with open(config_path, "r") as f:
            user_config = json.load(f)
        config = {**DEFAULT_CONFIG, **user_config}

        # Basic validation
        if not (1 <= config.get("default_port", 0) <= 65535):
            print(f"Invalid port in config. Resetting to default: {DEFAULT_CONFIG['default_port']}")
            config["default_port"] = DEFAULT_CONFIG["default_port"]

        if config.get("timeout", 0) <= 0:
            config["timeout"] = DEFAULT_CONFIG["timeout"]

        if config.get("retry_limit", -1) < 0:
            config["retry_limit"] = DEFAULT_CONFIG["retry_limit"]

        if config.get("log_level", "").upper() not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            config["log_level"] = DEFAULT_CONFIG["log_level"]

        if not isinstance(config.get("proxy"), dict):
            config["proxy"] = DEFAULT_CONFIG["proxy"]

        return config
    except Exception as e:
        print(f"Failed to load config: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config, config_path="config.json"):
    """
    Saves the given configuration dictionary to a JSON file.
    """
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)
        print(f"Configuration saved to {config_path}.")
    except Exception as e:
        print(f"Failed to save config: {e}")

# --- Global Configuration ---
CONFIG = load_config()

# --- Exported Constants for Convenience ---
DELAY = CONFIG.get("timeout", DEFAULT_CONFIG["timeout"])
PROXIES = CONFIG.get("proxy", DEFAULT_CONFIG["proxy"])
RETRY_LIMIT = CONFIG.get("retry_limit", DEFAULT_CONFIG["retry_limit"])
