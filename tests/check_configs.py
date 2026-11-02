#!/usr/bin/env python3
"""
Contrôle automatique des configurations (lancé par la CI) :
 - règles de durcissement présentes sur chaque équipement
 - aucune adresse IP attribuée deux fois
 - cohérence des VLAN (chaque VLAN autorisé sur un trunk ou affecté à un port est déclaré)
 - pairs VPN symétriques entre les deux routeurs
Usage : python3 tests/check_configs.py
"""
from __future__ import annotations

import ipaddress
import re
import sys
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent.parent / "configs"

HARDENING_ALL = {
    "service password-encryption": r"^service password-encryption",
    "enable secret (pas enable password)": r"^enable secret ",
    "bannière": r"^banner motd ",
    "serveur HTTP désactivé": r"^no ip http server",
}
HARDENING_MANAGED = {
    "SSH version 2": r"^ip ssh version 2",
    "utilisateur local avec secret": r"^username \S+ privilege 15 secret ",
    "VTY en SSH uniquement": r"^ transport input ssh$",
    "ACL sur les VTY": r"^ access-class \S+ in",
    "déconnexion automatique": r"^ exec-timeout \d+ \d+",
}
HARDENING_SWITCH = {
    "VLAN natif modifié": r"switchport trunk native vlan 999",
    "négociation DTP désactivée": r"switchport nonegotiate",
}
HARDENING_ACCESS_SWITCH = {
    "port-security": r"switchport port-security$",
    "BPDU guard sur les ports d'accès": r"spanning-tree bpduguard enable",
    "DHCP snooping": r"^ip dhcp snooping$",
    "ports inutilisés coupés": r"description Port inutilise",
}


def load() -> dict[str, list[str]]:
    return {p.stem: p.read_text(encoding="utf-8").splitlines() for p in sorted(CONFIG_DIR.glob("*.txt"))}


def check(configs: dict[str, list[str]]) -> list[str]:
    errors: list[str] = []
    ip_owner: dict[str, str] = {}

    for name, lines in configs.items():
        text = "\n".join(lines)
        rules = dict(HARDENING_ALL)
        if name != "ISP":
            rules |= HARDENING_MANAGED
        if name.startswith("SW-"):
            rules |= HARDENING_SWITCH
        if name.startswith("SW-") and "CORE" not in name:
            rules |= HARDENING_ACCESS_SWITCH
        for label, pattern in rules.items():
            if not re.search(pattern, text, re.M):
                errors.append(f"{name} : règle manquante — {label}")

        if re.search(r"transport input (telnet|all)", text):
            errors.append(f"{name} : Telnet autorisé sur les VTY")
        if re.search(r"^enable password ", text, re.M):
            errors.append(f"{name} : 'enable password' utilisé au lieu de 'enable secret'")

        # Adresses IP uniques
        current_if = "?"
        for line in lines:
            m = re.match(r"^interface (\S+)", line)
            if m:
                current_if = m.group(1)
            m = re.match(r"^\s*ip address (\d+\.\d+\.\d+\.\d+) (\d+\.\d+\.\d+\.\d+)", line)
            if m:
                ip = m.group(1)
                ipaddress.ip_interface(f"{ip}/{m.group(2)}")  # lève une exception si masque invalide
                where = f"{name} {current_if}"
                if ip in ip_owner:
                    errors.append(f"IP {ip} en double : {ip_owner[ip]} et {where}")
                ip_owner[ip] = where

        # VLAN déclarés vs utilisés
        if name.startswith("SW-"):
            declared = {int(v) for v in re.findall(r"^vlan (\d+)$", text, re.M)}
            used: set[int] = set()
            for v in re.findall(r"switchport access vlan (\d+)", text):
                used.add(int(v))
            for lst in re.findall(r"switchport trunk allowed vlan ([\d,]+)", text):
                used |= {int(v) for v in lst.split(",")}
            for v in re.findall(r"^interface Vlan(\d+)", text, re.M):
                if int(v) != 1:
                    used.add(int(v))
            missing = used - declared
            if missing:
                errors.append(f"{name} : VLAN utilisés mais non déclarés {sorted(missing)}")

    # VPN : chaque routeur pointe vers l'adresse WAN de l'autre
    def wan_ip(cfg: list[str]) -> str | None:
        text = "\n".join(cfg)
        m = re.search(r"interface GigabitEthernet0/0\n(?: .*\n)*? ip address (\S+)", text)
        return m.group(1) if m else None

    s, a = configs.get("R-SIEGE"), configs.get("R-AGENCE")
    if s and a:
        for me, peer, peer_name in ((s, a, "R-AGENCE"), (a, s, "R-SIEGE")):
            peer_ip = wan_ip(peer)
            text = "\n".join(me)
            for directive in (f"set peer {peer_ip}", f"tunnel destination {peer_ip}", f"address {peer_ip}"):
                if directive not in text:
                    errors.append(f"VPN : '{directive}' attendu (pair {peer_name})")
        psk = [re.search(r"crypto isakmp key (\S+)", "\n".join(c)) for c in (s, a)]
        if not all(psk) or psk[0].group(1) != psk[1].group(1):
            errors.append("VPN : clés pré-partagées différentes entre les deux routeurs")

    return errors


def main() -> int:
    configs = load()
    if not configs:
        print("Aucune configuration trouvée", file=sys.stderr)
        return 1
    errors = check(configs)
    for name in configs:
        print(f"  {name}")
    if errors:
        print(f"\n{len(errors)} problème(s) :")
        for e in errors:
            print(f"  ✗ {e}")
        return 1
    print(f"\n✓ {len(configs)} configurations conformes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
