# Monter le labo dans Packet Tracer

Temps estimé : 45 min à 1 h. Testé pour Packet Tracer 8.x.

## 1. Équipements

| Nom | Modèle Packet Tracer |
|---|---|
| ISP, R-SIEGE, R-AGENCE | 2911 |
| SW-CORE-SIEGE | 3560-24PS |
| SW-ACC1-SIEGE, SW-ACC2-SIEGE, SW-AGENCE | 2960-24TT |
| SRV-AD, SRV-FICHIERS, SRV-WEB, SRV-INTERNET | Server-PT |
| PC-ADM1, PC-ADM2, PC-COMPTA1, PC-ADMIN-IT, PC-AGENCE1, PC-AGENCE2 | PC-PT |
| LAPTOP-INVITE | Laptop-PT |

## 2. Câblage (câble droit cuivre, sauf indication)

| De | Port | Vers | Port |
|---|---|---|---|
| ISP | G0/0 | R-SIEGE | G0/0 |
| ISP | G0/1 | R-AGENCE | G0/0 |
| ISP | G0/2 | SRV-INTERNET | Fa0 |
| R-SIEGE | G0/1 | SW-CORE-SIEGE | Gi0/1 |
| SW-CORE-SIEGE | Fa0/1 | SW-ACC1-SIEGE | Gi0/1 (câble croisé) |
| SW-CORE-SIEGE | Fa0/2 | SW-ACC2-SIEGE | Gi0/1 (câble croisé) |
| SW-ACC1-SIEGE | Fa0/1 | PC-ADM1 | Fa0 |
| SW-ACC1-SIEGE | Fa0/10 | SRV-AD | Fa0 |
| SW-ACC1-SIEGE | Fa0/11 | SRV-FICHIERS | Fa0 |
| SW-ACC1-SIEGE | Fa0/12 | SRV-WEB | Fa0 |
| SW-ACC1-SIEGE | Fa0/24 | PC-ADMIN-IT | Fa0 |
| SW-ACC2-SIEGE | Fa0/1 | PC-COMPTA1 | Fa0 |
| SW-ACC2-SIEGE | Fa0/10 | PC-ADM2 | Fa0 |
| SW-ACC2-SIEGE | Fa0/20 | LAPTOP-INVITE | Fa0 |
| R-AGENCE | G0/1 | SW-AGENCE | Gi0/1 |
| SW-AGENCE | Fa0/1 | PC-AGENCE1 | Fa0 |
| SW-AGENCE | Fa0/2 | PC-AGENCE2 | Fa0 |

> Astuce : l'outil « Automatically Choose Connection Type » (l'éclair) choisit le bon câble tout seul.

## 3. Licence sécurité des routeurs (pour IPsec)

Sur **R-SIEGE** et **R-AGENCE** :

```
enable
configure terminal
license boot module c2900 technology-package securityk9
yes
end
write memory
reload
```

Vérification : `show version` → `securityk9` doit apparaître en *Permanent* ou *Evaluation*.

## 4. Configurations

Dans l'onglet **CLI** de chaque équipement, coller le contenu du fichier correspondant de `configs/` (de préférence par blocs, Packet Tracer peut perdre des lignes sur les très longs collages). Ordre conseillé :

1. `ISP.txt`
2. `R-SIEGE.txt`, puis `SW-CORE-SIEGE.txt`
3. `SW-ACC1-SIEGE.txt`, `SW-ACC2-SIEGE.txt`
4. `R-AGENCE.txt`, puis `SW-AGENCE.txt`

## 5. Postes et serveurs

- PC-ADM1, PC-ADM2, PC-COMPTA1, LAPTOP-INVITE, PC-AGENCE1, PC-AGENCE2 : *Desktop → IP Configuration → DHCP*.
- Serveurs et PC-ADMIN-IT : adresses fixes du [plan d'adressage](plan-adressage.md).
- **SRV-AD** : *Services → DNS* activé, enregistrements A `intranet.pme.local → 10.10.30.30`, `fichiers.pme.local → 10.10.30.20`, `www.exemple.com → 192.0.2.10`.
- **SRV-WEB** : *Services → HTTP* activé, modifier `index.html` (« Intranet PME »).
- **SRV-INTERNET** : HTTP activé (« Site Internet ») et DNS activé avec `www.exemple.com → 192.0.2.10`.
- Désactiver les services inutiles (FTP, SMTP, etc.) sur tous les serveurs.

## 6. Enregistrer

*File → Save As* pour conserver le labo, puis dérouler la [page de tests](tests.md).
