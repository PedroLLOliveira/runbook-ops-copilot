import re

ALLOW_PREFIXES = (
    "curl", "ping", "traceroute", "nslookup", "dig",
    "journalctl", "cat", "tail", "head", "grep", "awk", "sed",
    "ps", "top", "htop", "df", "du", "free", "uptime",
    "docker ps", "docker logs",
    "kubectl get", "kubectl describe", "kubectl logs",
    "systemctl status",
)

BLOCK_PATTERNS = (
    r"\brm\b", r"\bkill\b", r"\bshutdown\b", r"\breboot\b",
    r"\bDROP\b", r"\bDELETE\b", r"\bTRUNCATE\b",
    r"kubectl\s+delete", r"systemctl\s+stop", r"iptables",
)

def is_blocked(cmd: str) -> bool:
    s = cmd.strip()
    return any(re.search(p, s, flags=re.IGNORECASE) for p in BLOCK_PATTERNS)

def is_allowed(cmd: str) -> bool:
    s = cmd.strip()
    if is_blocked(s):
        return False
    return any(s.startswith(p) for p in ALLOW_PREFIXES)
