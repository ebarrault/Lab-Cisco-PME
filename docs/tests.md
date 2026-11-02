# Page de tests

Chaque test indique **où** lancer la commande, **ce qu'on attend** et une case pour le résultat. Remplacer les cases par ✅ / ❌ au fil des vérifications.

## 1. Commutation et VLAN

| # | Où | Commande | Résultat attendu | OK |
|---|---|---|---|---|
| 1.1 | SW-ACC1-SIEGE | `show vlan brief` | VLAN 10, 30, 99, 999 ; Fa0/1-9 en 10, Fa0/10-12 en 30, ports inutilisés en 999 | ☐ |
| 1.2 | SW-CORE-SIEGE | `show interfaces trunk` | Fa0/1 et Fa0/2 en trunk, natif 999, VLAN autorisés conformes | ☐ |
| 1.3 | SW-CORE-SIEGE | `show spanning-tree vlan 10` | « This bridge is the root » | ☐ |
| 1.4 | SW-ACC1-SIEGE | `show port-security interface fa0/1` | Port Security Enabled, Secure-up | ☐ |
| 1.5 | SW-ACC2-SIEGE | `show ip dhcp snooping` | snooping actif sur VLAN 10, 20, 40, Gi0/1 trusted | ☐ |

## 2. DHCP et routage inter-VLAN

| # | Où | Commande | Résultat attendu | OK |
|---|---|---|---|---|
| 2.1 | PC-ADM1 | `ipconfig` | 10.10.10.21+ / passerelle 10.10.10.1 / DNS 10.10.30.10 | ☐ |
| 2.2 | PC-COMPTA1 | `ipconfig` | 10.10.20.x | ☐ |
| 2.3 | PC-AGENCE1 | `ipconfig` | 10.20.10.x / passerelle 10.20.10.1 | ☐ |
| 2.4 | R-SIEGE | `show ip dhcp binding` | baux des VLAN 10, 20, 40 | ☐ |
| 2.5 | PC-ADM1 | `ping 10.10.20.21` (PC-COMPTA1) | réponses (routage inter-VLAN par le cœur) | ☐ |

## 3. OSPF et VPN

| # | Où | Commande | Résultat attendu | OK |
|---|---|---|---|---|
| 3.1 | R-SIEGE | `show ip ospf neighbor` | 2.2.2.2 (Gi0/1) et 3.3.3.3 (Tunnel0) en FULL | ☐ |
| 3.2 | R-AGENCE | `show ip route ospf` | routes `O 10.10.x.0/24` via 172.16.0.1 | ☐ |
| 3.3 | R-SIEGE | `show crypto isakmp sa` | état `QM_IDLE` avec 198.51.100.2 | ☐ |
| 3.4 | R-SIEGE | `show crypto ipsec sa` | compteurs `#pkts encaps / decaps` qui augmentent | ☐ |
| 3.5 | PC-AGENCE1 | `tracert 10.10.30.10` | 10.20.10.1 → 172.16.0.1 → 10.10.255.2 → 10.10.30.10 (le tunnel, pas l'ISP) | ☐ |
| 3.6 | PC-AGENCE1 | navigateur `http://intranet.pme.local` | page « Intranet PME » | ☐ |

## 4. Internet et NAT

| # | Où | Commande | Résultat attendu | OK |
|---|---|---|---|---|
| 4.1 | PC-ADM1 | `ping 192.0.2.10` | réponses | ☐ |
| 4.2 | R-SIEGE | `show ip nat translations` | traductions `203.0.113.2:port` | ☐ |
| 4.3 | PC-AGENCE1 | navigateur `http://www.exemple.com` | « Site Internet » (NAT de l'agence) | ☐ |
| 4.4 | SRV-INTERNET | navigateur `http://203.0.113.2` | « Intranet PME » (redirection de port vers SRV-WEB) | ☐ |
| 4.5 | SRV-INTERNET | `ping 10.10.10.21` | échec : les réseaux privés ne sont pas routés sur Internet | ☐ |

## 5. ACL

| # | Où | Commande | Résultat attendu | OK |
|---|---|---|---|---|
| 5.1 | LAPTOP-INVITE | `ipconfig` | 10.10.40.x, DNS 192.0.2.10 | ☐ |
| 5.2 | LAPTOP-INVITE | `ping 192.0.2.10` | réponses (Internet autorisé) | ☐ |
| 5.3 | LAPTOP-INVITE | `ping 10.10.30.10` | « Destination host unreachable » (invités isolés) | ☐ |
| 5.4 | LAPTOP-INVITE | `ping 10.10.10.1` | échec | ☐ |
| 5.5 | PC-COMPTA1 | navigateur `http://10.10.30.30` | page intranet (HTTP autorisé) | ☐ |
| 5.6 | PC-COMPTA1 | `telnet 10.10.30.10 23` ou FTP vers un serveur | refusé (seuls HTTP/HTTPS/SMB/DNS/ping sont ouverts) | ☐ |
| 5.7 | SW-CORE-SIEGE | `show access-lists` | compteurs `matches` sur les lignes deny | ☐ |

## 6. Administration et durcissement

| # | Où | Commande | Résultat attendu | OK |
|---|---|---|---|---|
| 6.1 | PC-ADMIN-IT | `ssh -l admin 10.10.99.11` | bannière puis invite `SW-ACC1-SIEGE#` | ☐ |
| 6.2 | PC-ADMIN-IT | `ssh -l admin 10.10.255.1` | connexion à R-SIEGE | ☐ |
| 6.3 | PC-ADM1 | `ssh -l admin 10.10.99.11` | refus (ACL-ADMIN-SSH) | ☐ |
| 6.4 | PC-ADMIN-IT | `telnet 10.10.99.11` | refus (SSH uniquement) | ☐ |
| 6.5 | R-SIEGE | `show ip ssh` | SSH Enabled - version 2.0 | ☐ |
| 6.6 | R-SIEGE | `show running-config \| include password\|secret` | aucun mot de passe en clair | ☐ |
| 6.7 | SW-ACC1-SIEGE | brancher un 2e PC sur Fa0/10 (serveur) | port en `err-disabled` (violation shutdown) | ☐ |
| 6.8 | R-SIEGE | 3 mauvais mots de passe SSH en 60 s | connexions bloquées 120 s (`login block-for`) | ☐ |

## 7. Résilience

| # | Où | Action | Résultat attendu | OK |
|---|---|---|---|---|
| 7.1 | R-SIEGE | `shutdown` sur Tunnel0 | `show ip route` sur R-AGENCE : routes 10.10.x disparaissent | ☐ |
| 7.2 | R-SIEGE | `no shutdown` sur Tunnel0 | voisinage OSPF rétabli en quelques secondes, ping inter-sites OK | ☐ |
