# Plan d'adressage

## Principe

| Bloc | Usage |
|---|---|
| `10.10.0.0/16` | Siège (Bayonne) — le 3e octet = numéro de VLAN |
| `10.20.0.0/16` | Agence (Pau) — même logique |
| `172.16.0.0/30` | Tunnel VPN entre les sites |
| `203.0.113.0/30`, `198.51.100.0/30`, `192.0.2.0/24` | « Internet » (plages réservées à la documentation, RFC 5737) |

Dans chaque VLAN : `.1` = passerelle, `.2` à `.20` = adresses fixes (serveurs, imprimantes), `.21` à `.254` = DHCP.

## VLAN

| VLAN | Nom | Siège | Agence | Passerelle | DHCP |
|---|---|---|---|---|---|
| 10 | ADMINISTRATIF | 10.10.10.0/24 | 10.20.10.0/24 | .1 (SVI cœur / sous-interface R-AGENCE) | oui |
| 20 | COMPTABILITE | 10.10.20.0/24 | — | 10.10.20.1 | oui |
| 30 | SERVEURS | 10.10.30.0/24 | — | 10.10.30.1 | non (fixes) |
| 40 | WIFI-INVITES | 10.10.40.0/24 | — | 10.10.40.1 | oui (DNS public) |
| 99 | MANAGEMENT | 10.10.99.0/24 | 10.20.99.0/24 | .1 | non |
| 999 | PARKING-NATIF | — | — | — | VLAN natif des trunks et ports inutilisés, aucun trafic |

## Interfaces des équipements réseau

| Équipement | Interface | Adresse | Description |
|---|---|---|---|
| ISP | G0/0 | 203.0.113.1/30 | vers R-SIEGE |
| ISP | G0/1 | 198.51.100.1/30 | vers R-AGENCE |
| ISP | G0/2 | 192.0.2.1/24 | réseau « Internet » |
| R-SIEGE | G0/0 | 203.0.113.2/30 | WAN, NAT outside, crypto map |
| R-SIEGE | G0/1 | 10.10.255.1/30 | vers SW-CORE, NAT inside, serveur DHCP |
| R-SIEGE | Tunnel0 | 172.16.0.1/30 | GRE over IPsec vers l'agence |
| SW-CORE-SIEGE | Gi0/1 (routé) | 10.10.255.2/30 | vers R-SIEGE |
| SW-CORE-SIEGE | Vlan10 / 20 / 30 / 40 / 99 | 10.10.x.1/24 | passerelles |
| SW-ACC1-SIEGE | Vlan99 | 10.10.99.11/24 | management |
| SW-ACC2-SIEGE | Vlan99 | 10.10.99.12/24 | management |
| R-AGENCE | G0/0 | 198.51.100.2/30 | WAN |
| R-AGENCE | G0/1.10 | 10.20.10.1/24 | passerelle VLAN 10 |
| R-AGENCE | G0/1.99 | 10.20.99.1/24 | passerelle management |
| R-AGENCE | Tunnel0 | 172.16.0.2/30 | VPN vers le siège |
| SW-AGENCE | Vlan99 | 10.20.99.11/24 | management |

## Hôtes à adresse fixe

| Hôte | Adresse | Passerelle | DNS | Rôle |
|---|---|---|---|---|
| SRV-AD | 10.10.30.10/24 | 10.10.30.1 | 10.10.30.10 | DNS interne (`pme.local`) |
| SRV-FICHIERS | 10.10.30.20/24 | 10.10.30.1 | 10.10.30.10 | partage de fichiers |
| SRV-WEB | 10.10.30.30/24 | 10.10.30.1 | 10.10.30.10 | intranet, publié sur 203.0.113.2:80 |
| PC-ADMIN-IT | 10.10.99.50/24 | 10.10.99.1 | 10.10.30.10 | administration (seul réseau autorisé en SSH) |
| SRV-INTERNET | 192.0.2.10/24 | 192.0.2.1 | — | site web et DNS « publics » |

## Routage

- **OSPF zone 0** (processus 1) entre R-SIEGE (1.1.1.1), SW-CORE-SIEGE (2.2.2.2) et R-AGENCE (3.3.3.3), authentification MD5, interfaces passives par défaut.
- Route par défaut statique sur chaque routeur vers l'ISP ; R-SIEGE la diffuse au cœur (`default-information originate`).
- Le trafic inter-sites passe par `Tunnel0` ; il n'est pas traduit (NAT) et il est chiffré (IPsec AES-256 / SHA).
