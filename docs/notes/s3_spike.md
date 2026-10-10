# S3 — Spike : détection de l'hybride PQC avec `openssl s_client`

- **Date** : 09/10/2026
- **Cibles** : `cloudflare.com` (hybride, repéré en S1) et le site d'une université (classique, repéré en S1). Entité anonymisée
- **Outil** : `openssl s_client` dans un conteneur `debian:trixie-slim` (paquets `openssl` et `ca-certificates`). Version exacte d'OpenSSL : 3.5.7 9
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

- ## Sorties observées

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

| Sortie                                                              | Étape atteinte       | Sens pour pqready                              |
| ------------------------------------------------------------------- | -------------------- | ---------------------------------------------- |
| `BIO routines:BIO_lookup_ex ... Name or service not known`          | DNS, aucun handshake | `status: error`, rien à conclure sur la crypto |
| `SSL alert number 40` en hybride seul, **et** succès en X25519 seul | Handshake refusé     | `pq_hybrid_supported: false`                   |
| `CONNECTION ESTABLISHED` en hybride seul                            | Handshake réussi     | `pq_hybrid_supported: true`                    |

**L'alert 40 seule ne prouve rien.** C'est une erreur générique : pas de groupe en commun, pas de suite en commun, version refusée. Il faut l'appel de contrôle en X25519 seul, où seul le groupe change : s'il réussit, l'échec venait bien du groupe. S'il échoue aussi, le résultat est « inconnu », pas « hybride non ».

## Ligne à parser pour le groupe négocié

Le format dépend du type de groupe, avec ou sans `-brief` :

| Cas              | Ligne affichée                            |
| ---------------- | ----------------------------------------- |
| Groupe classique | `Peer Temp Key: X25519, 253 bits`         |
| Groupe hybride   | `Negotiated TLS1.3 group: X25519MLKEM768` |



## À creuser

- Le format des deux lignes est-il stable d'une version d'OpenSSL à l'autre ?
- Que montre la sortie pour un échange de clés TLS 1.2 (ECDHE) ?
- 
