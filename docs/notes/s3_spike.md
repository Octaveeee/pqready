# S3 — Spike : détection de l'hybride PQC avec `openssl s_client`

- **Date** : 09/10/2026
- **Cibles** : `cloudflare.com` (hybride, repéré en S1) et le site d'une université (classique, repéré en S1). Entité anonymisée
- **Outil** : `openssl s_client` dans un conteneur `debian:trixie-slim` (paquets `openssl` et `ca-certificates`). Version exacte d'OpenSSL : 3.5.7 (build du 9 Jun 2026)
- **Méthode** : quelques poignées de main TLS standard par cible, aucun test intrusif.

## Résultat

**La détection « hybride oui/non » est faisable avec `openssl s_client` seul.**

|                                             | Site d'université | cloudflare.com |
| ------------------------------------------- | ----------------- | -------------- |
| (a) Groupe négocié par défaut               | X25519            | X25519MLKEM768 |
| (b) Hybride seul (`-groups X25519MLKEM768`) | Refusé (alert 40) | Accepté        |
| Contrôle : X25519 seul (`-groups X25519`)   | Accepté           | Accepté        |

- **(a) groupe négocié** : ce que le serveur choisit quand le client propose sa liste par défaut ;
- **(b) hybride accepté** : ce que le serveur répond quand le client ne propose que `X25519MLKEM768`.

## Commandes

```bash
# (a) groupe négocié par défaut
openssl s_client -connect <hôte>:443 -brief </dev/null

# (b) hybride seul
openssl s_client -connect <hôte>:443 -groups X25519MLKEM768 -brief </dev/null

# contrôle : classique seul
openssl s_client -connect <hôte>:443 -groups X25519 -brief </dev/null
```

## Sorties observées

**Site d'université, hybride seul → refus**

```
Connecting to <IP>
...:error:0A000410:SSL routines:ssl3_read_bytes:ssl/tls alert handshake failure:../ssl/record/rec_layer_s3.c:918:SSL alert number 40
```

**Site d'université, X25519 seul (sortie identique sans `-groups`)**

```
CONNECTION ESTABLISHED
Protocol version: TLSv1.3
Ciphersuite: TLS_AES_256_GCM_SHA384
Peer certificate: <anonymisé>
Hash used: SHA256
Signature type: rsa_pss_rsae_sha256
Verification: OK
Peer Temp Key: X25519, 253 bits
DONE
```

**cloudflare.com, hybride seul (sortie identique sans `-groups`)**

```
CONNECTION ESTABLISHED
Protocol version: TLSv1.3
Ciphersuite: TLS_AES_256_GCM_SHA384
Peer certificate: CN=cloudflare.com
Hash used: SHA256
Signature type: ecdsa_secp256r1_sha256
Verification: OK
Negotiated TLS1.3 group: X25519MLKEM768
DONE
```

**cloudflare.com, X25519 seul**

```
CONNECTION ESTABLISHED
Protocol version: TLSv1.3
Ciphersuite: TLS_AES_256_GCM_SHA384
Peer certificate: CN=cloudflare.com
Hash used: SHA256
Signature type: ecdsa_secp256r1_sha256
Verification: OK
Peer Temp Key: X25519, 253 bits
```

## Signatures à distinguer

> **Corrigé après le lab (05/11/2026)** : `CONNECTION ESTABLISHED` en hybride seul ne suffit pas à conclure `true` (faux positif sur le serveur `faible`, voir « Lab Docker »).

| Sortie                                                                       | Étape atteinte                  | Sens pour pqready                                    |
| ---------------------------------------------------------------------------- | ------------------------------- | ---------------------------------------------------- |
| `BIO routines:BIO_lookup_ex ... Name or service not known`                   | DNS, aucun handshake            | `status: error`, rien à conclure sur la crypto       |
| `tls_setup_handshake:no protocols available`                                 | Client, aucun handshake         | Erreur de config du client, **pas** un refus serveur |
| `SSL alert number 40` en hybride seul, **et** succès en X25519 seul          | Handshake refusé                | `pq_hybrid_supported: false`                         |
| `SSL alert number 40` en hybride seul **et** en X25519 seul                  | Handshake refusé                | `pq_hybrid_supported: unknown`                       |
| `CONNECTION ESTABLISHED` en hybride seul, **sans** `Negotiated TLS1.3 group` | Handshake réussi, groupe ignoré | `pq_hybrid_supported: false`                         |
| `Negotiated TLS1.3 group: X25519MLKEM768`                                    | Handshake réussi                | `pq_hybrid_supported: true`                          |

**L'alert 40 seule ne prouve rien.** C'est une erreur générique : pas de groupe en commun, pas de suite en commun, version refusée. Il faut l'appel de contrôle en X25519 seul, où seul le groupe change : s'il réussit, l'échec venait bien du groupe. S'il échoue aussi, le résultat est « inconnu », pas « hybride non ».

## Ligne à parser pour le groupe négocié

Le format dépend du type de groupe, avec ou sans `-brief` :

| Cas              | Ligne affichée                            |
| ---------------- | ----------------------------------------- |
| Groupe classique | `Peer Temp Key: X25519, 253 bits`         |
| Groupe hybride   | `Negotiated TLS1.3 group: X25519MLKEM768` |

## Lab Docker

- **Date** : 05/11/2026
- **Lab** : `docker/lab/docker-compose.yml`, nginx 1.26.3 sur `debian:trixie-slim` (OpenSSL 3.5.7), réseau `pqready-lab`. Certificats auto-signés.
- **Client** : image `pqready-tools`, lancée sur le réseau du lab

| Serveur     | Config TLS                                                                                         | Certificat  |
| ----------- | -------------------------------------------------------------------------------------------------- | ----------- |
| `hybride`   | TLS 1.3, `ssl_ecdh_curve X25519MLKEM768:X25519`                                                    | ECDSA P-256 |
| `classique` | TLS 1.2 et 1.3, `ssl_ecdh_curve X25519`                                                            | ECDSA P-256 |
| `faible`    | TLS 1.0, 1.1 et 1.2, `ssl_ciphers "AES128-SHA:ECDHE-RSA-AES128-SHA:@SECLEVEL=0"`, ordre du serveur | RSA 1024    |

Pour `faible`, `@SECLEVEL=0` dans `ssl_ciphers` suffit : nginx démarre sans abaisser le niveau de sécurité dans `openssl.cnf`.

### Résultat

**La matrice donne le bon résultat sur les trois serveurs, à condition de lire la ligne du groupe négocié et pas seulement `CONNECTION ESTABLISHED`.**

|                                             | `classique`                       | `hybride`                                 | `faible`                                   |
| ------------------------------------------- | --------------------------------- | ----------------------------------------- | ------------------------------------------ |
| (a) Groupe négocié par défaut               | `Peer Temp Key: X25519`           | `Negotiated TLS1.3 group: X25519MLKEM768` | Aucun (TLS 1.2, `AES128-SHA`, échange RSA) |
| (b) Hybride seul (`-groups X25519MLKEM768`) | Refusé (alert 40)                 | Accepté                                   | **Accepté, sans ligne de groupe**          |
| Contrôle : X25519 seul (`-groups X25519`)   | Accepté                           | Accepté (`Peer Temp Key: X25519`)         | Accepté, sans ligne de groupe              |
| TLS 1.2 (`-tls1_2`)                         | Accepté (`Peer Temp Key: X25519`) | Non testé (TLS 1.3 seul)                  | Accepté (par défaut)                       |
| TLS 1.0 / 1.1 (`-tls1`, `-tls1_1`)          | Non testé                         | Non testé                                 | Acceptés (client en `@SECLEVEL=0`)         |
| → `pq_hybrid_supported`                     | `false`                           | `true`                                    | `false`                                    |

Pour `faible`, ces appels ont été faits avec `-cipher 'DEFAULT:@SECLEVEL=0'` côté client (appels sans : voir « Niveau de sécurité du client »).

### Sortie TLS 1.2 (`classique`)

```
CONNECTION ESTABLISHED
Protocol version: TLSv1.2
Ciphersuite: ECDHE-ECDSA-AES256-GCM-SHA384
Peer certificate: CN=classique
Hash used: SHA256
Signature type: ecdsa_secp256r1_sha256
Verification error: self-signed certificate
Supported Elliptic Curve Point Formats: uncompressed:ansiX962_compressed_prime:ansiX962_compressed_char2
Peer Temp Key: X25519, 253 bits
DONE
```

### Sortie TLS 1.2 avec échange de clés RSA (`faible`, hybride seul)

```
CONNECTION ESTABLISHED
Protocol version: TLSv1.2
Ciphersuite: AES128-SHA
Peer certificate: CN=faible
Verification error: self-signed certificate
DONE
```

- **Faux positif évité** : le client ne propose que `X25519MLKEM768`, et la connexion s'établit quand même. L'échange de clés RSA n'utilise aucun groupe, donc le serveur ignore la liste du client. Avec l'ancienne règle (« `CONNECTION ESTABLISHED` → `true` »), le pire serveur du lab serait déclaré hybride PQC.
- **Échange de clés RSA reconnaissable à deux signes** : une suite sans préfixe `ECDHE-` / `DHE-` (`AES128-SHA`), et l'absence de ligne `Peer Temp Key`. Les lignes `Hash used` et `Signature type` sont absentes aussi (en échange RSA, le serveur n'envoie pas de `ServerKeyExchange` signé).

### Niveau de sécurité du client

| Appel sur `faible`                        | Résultat                                                                         |
| ----------------------------------------- | -------------------------------------------------------------------------------- |
| Par défaut, **sans** `@SECLEVEL=0`        | Accepté en TLS 1.2, avec `Verification error: EE certificate key too weak`       |
| `-tls1`, **sans** `@SECLEVEL=0`           | `tls_setup_handshake:no protocols available` : le client refuse avant tout envoi |
| `-tls1`, `-tls1_1` **avec** `@SECLEVEL=0` | Acceptés                                                                         |

- En TLS 1.2, le niveau de sécurité par défaut ne bloque pas le handshake : il dégrade seulement la vérification du certificat (`EE certificate key too weak` pour RSA 1024).
- **Les sondes de versions anciennes doivent utiliser `-cipher 'DEFAULT:@SECLEVEL=0'`**. Sans ça, tout serveur qui accepte TLS 1.0 apparaîtrait comme le refusant : faux négatif sur un P0.

### Constats pour le parser

- **Preuve de l'hybride = la ligne `Negotiated TLS1.3 group: X25519MLKEM768`**, pas `CONNECTION ESTABLISHED`.
- **Vérification du certificat et handshake sont indépendants** : avec un certificat auto-signé, `s_client` affiche `Verification error: self-signed certificate` mais va jusqu'à `CONNECTION ESTABLISHED`. La détection du groupe n'en dépend pas.
- **Lignes à ignorer** : `Can't use SSL_get_servername`, `depth=...`, `verify error:...`, `Supported Elliptic Curve Point Formats: ...` (TLS 1.2 uniquement).

### Sondes de versions et kRSA

But : remplir `versions` et `rsa_key_exchange` avec `s_client` seul (→ ADR-002). Une sonde par version (protocole forcé) et une sonde qui ne propose que des suites à échange de clés RSA (`kRSA`).

```bash
openssl s_client -connect <hôte>:443 -cipher 'DEFAULT:@SECLEVEL=0' -tls1   -brief </dev/null
openssl s_client -connect <hôte>:443 -cipher 'DEFAULT:@SECLEVEL=0' -tls1_1 -brief </dev/null
openssl s_client -connect <hôte>:443 -cipher 'DEFAULT:@SECLEVEL=0' -tls1_2 -brief </dev/null
openssl s_client -connect <hôte>:443 -tls1_3 -brief </dev/null
openssl s_client -connect <hôte>:443 -tls1_2 -cipher 'kRSA:@SECLEVEL=0' -brief </dev/null
```

| Sonde     | `faible`                        | `classique`                               |
| --------- | ------------------------------- | ----------------------------------------- |
| `-tls1`   | Accepté (TLSv1, `AES128-SHA`)   | Refusé (alert 70)                         |
| `-tls1_1` | Accepté (TLSv1.1, `AES128-SHA`) | Refusé (alert 70)                         |
| `-tls1_2` | Accepté (`AES128-SHA`)          | Accepté (`ECDHE-ECDSA-AES256-GCM-SHA384`) |
| `-tls1_3` | Refusé (alert 70)               | Accepté (`TLS_AES_256_GCM_SHA384`)        |
| `kRSA`    | Accepté (`AES128-SHA`)          | Refusé (alert 40)                         |

**Version refusée par le serveur → alerte 70** :

```
...:error:0A00042E:SSL routines:ssl3_read_bytes:tlsv1 alert protocol version:../ssl/record/rec_layer_s3.c:918:SSL alert number 70
```
