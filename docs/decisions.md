# Décisions techniques

---

## ADR-001 — Détection du groupe négocié et de l'hybride PQC

- **Date** : 05/11/2026
- **Statut** : Accepté
- **Preuves** : [`docs/notes/s3_spike.md`](notes/s3_spike.md) (spike sur 2 sites publics + lab Docker de 3 serveurs)

### Contexte

Pour chaque endpoint, `pqready` doit savoir :

- **(a)** quel groupe d'échange de clés le serveur **négocie** avec un client standard ;
- **(b)** si le serveur **accepte** le groupe hybride post-quantique `X25519MLKEM768`.

C'est l'information centrale du projet : un échange de clés non hybride est exposé au « harvest now, decrypt later » et conditionne les priorités P1/P2/P3.

Contraintes :

- `X25519MLKEM768` n'est disponible qu'à partir d'**OpenSSL 3.5**.
- Le module `ssl` de Python n'expose pas facilement le groupe négocié.
- Le résultat doit être **explicable** : un RSSI doit pouvoir comprendre pourquoi un endpoint est classé « hybride » ou non.

### Options envisagées

Toutes testées le 05/11/2026 sur le lab (`hybride`, `classique`, `faible`).

| Option                                  | Version testée                                                                          | `hybride`                       | `classique`             | `faible`                                   | Durée / cible                       | Remarques                                                                                                                |
| --------------------------------------- | --------------------------------------------------------------------------------------- | ------------------------------- | ----------------------- | ------------------------------------------ | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **`openssl s_client`** via `subprocess` | OpenSSL 3.5.7 (build du 9 Jun 2026), image `pqready-tools`                              | ✅ `X25519MLKEM768`              | ✅ pas d'hybride         | ✅ pas d'hybride (avec la règle ci-dessous) | 3 handshakes, < 1 s                 | Sortie texte à parser ; logique de décision entièrement maîtrisée                                                        |
| **testssl.sh** (`-f`)                   | 3.3dev, OpenSSL embarqué 1.0.2-bad, image `ghcr.io/testssl/testssl.sh@sha256:ca2760ef…` | ✅ `KEMs offered X25519MLKEM768` | ✅ `None`                | ✅ `None`                                   | 8 à 13 s pour la seule section `-f` | Détecte les KEM avec ses propres sockets (bash), malgré un OpenSSL 1.0.2 ; gros script externe ; `--jsonfile` disponible |
| **sslyze** (`--elliptic_curves`)        | 6.3.1, image `nablac0d3/sslyze@sha256:3060ce2f…`                                        | ❌ ne rapporte que `X25519`      | ✅ (ne teste pas ML-KEM) | —                                          | 0,23 s                              | **Faux négatif** : ne teste pas les groupes ML-KEM, donc ne peut pas voir l'hybride                                      |

### Décision

**`pqready` détecte le groupe négocié et l'hybride PQC avec `openssl s_client` (OpenSSL ≥ 3.5), appelé via `subprocess` dans le conteneur `pqready-tools`.**

- **sslyze** est écarté pour cet usage : il ne détecte pas `X25519MLKEM768` (version 6.3.1). Son usage éventuel pour les versions TLS et les suites relève d'une autre décision (ADR-002).
- **testssl.sh** est écarté comme moteur (environ 10 fois plus lent, grosse dépendance), mais il sert de **référence de contrôle** : sur le lab, ses résultats et ceux de `pqready` doivent concorder.

### Méthode retenue

Trois appels par cible, où seule la liste de groupes proposée par le client change :

```bash
# (a) groupe négocié par défaut
openssl s_client -connect <hôte>:<port> -brief </dev/null

# (b) hybride seul
openssl s_client -connect <hôte>:<port> -groups X25519MLKEM768 -brief </dev/null

# (c) contrôle : classique seul
openssl s_client -connect <hôte>:<port> -groups X25519 -brief </dev/null
```

**Lignes à parser pour le groupe négocié** (le format dépend du type de groupe) :

| Cas                               | Ligne                                                         |
| --------------------------------- | ------------------------------------------------------------- |
| Groupe classique (TLS 1.2 et 1.3) | `Peer Temp Key: X25519, 253 bits`                             |
| Groupe hybride                    | `Negotiated TLS1.3 group: X25519MLKEM768`                     |
| Échange de clés RSA (TLS ≤ 1.2)   | Aucune des deux lignes ; suite sans préfixe `ECDHE-` / `DHE-` |

**Table de décision pour `pq_hybrid_supported`** (évaluée dans cet ordre) :

| #   | Observation                                                          | Résultat                                                           |
| --- | -------------------------------------------------------------------- | ------------------------------------------------------------------ |
| 1   | Erreur DNS / TCP sur l'appel (a)                                     | `status: error`, rien à conclure                                   |
| 2   | Appel (b) : ligne `Negotiated TLS1.3 group: X25519MLKEM768` présente | `true`                                                             |
| 3   | Appel (b) : `CONNECTION ESTABLISHED` **sans** cette ligne            | `false` (le serveur a ignoré la liste de groupes, ex. échange RSA) |
| 4   | Appel (b) refusé (ex. `SSL alert number 40`) **et** appel (c) réussi | `false`                                                            |
| 5   | Appels (b) et (c) refusés tous les deux                              | `unknown`                                                          |

**Règle centrale : la preuve de l'hybride est la ligne du groupe négocié, jamais `CONNECTION ESTABLISHED` seul.** Le serveur `faible` du lab (échange de clés RSA en TLS 1.2) accepte la connexion même quand le client ne propose que `X25519MLKEM768`.

**Pourquoi l'appel de contrôle (c)** : l'alerte 40 est générique (pas de groupe commun, pas de suite commune, version refusée). L'appel (c) ne change que le groupe : s'il réussit, l'échec de (b) venait bien du groupe. Sinon, le résultat est `unknown`, pas `false`.

**Lignes ignorées par le parser** : `Can't use SSL_get_servername`, `depth=...`, `verify error:...`, `Verification error: ...`, `Supported Elliptic Curve Point Formats: ...`. La vérification du certificat est indépendante du handshake : un certificat auto-signé ou trop faible n'empêche pas la détection du groupe. Le certificat est analysé séparément (`scanner/cert.py`, bibliothèque `cryptography`).

### Preuves

Résultats sur le lab (détail et sorties brutes dans `docs/notes/s3_spike.md`) :

|                             | `hybride`                     | `classique`       | `faible`                          |
| --------------------------- | ----------------------------- | ----------------- | --------------------------------- |
| (a) Groupe négocié          | `X25519MLKEM768`              | `X25519`          | aucun (TLS 1.2, `AES128-SHA`)     |
| (b) Hybride seul            | accepté, avec ligne de groupe | refusé (alert 40) | accepté, **sans** ligne de groupe |
| (c) Contrôle X25519         | accepté                       | accepté           | accepté, sans ligne de groupe     |
| → `pq_hybrid_supported`     | `true`                        | `false`           | `false`                           |
| testssl.sh (`KEMs offered`) | `X25519MLKEM768`              | `None`            | `None`                            |

Même résultat sur les sites publics du spike : `cloudflare.com` → `true`, site d'université → `false`.

---

## ADR-002 — Détection des versions TLS et de l'échange de clés RSA

- **Date** : 05/11/2026
- **Statut** : Accepté
- **Preuves** : [`docs/notes/s3_spike.md`](notes/s3_spike.md), section « Sondes de versions et kRSA »

### Contexte

En plus du groupe négocié (ADR-001), `pqready` doit remplir deux champs de `TlsInfo` :

- **`versions`** : les versions TLS acceptées par le serveur. TLS 1.0 et 1.1 sont des faiblesses classiques (**P0**).
- **`rsa_key_exchange`** : le serveur accepte-t-il un échange de clés RSA (suites `TLS_RSA_*`, sans confidentialité persistante) ? C'est aussi un **P0** : une clé privée volée déchiffre tout le trafic enregistré.

Contrainte observée : OpenSSL 3.5 refuse côté client d'envoyer du TLS 1.0/1.1 avec le niveau de sécurité par défaut (`no protocols available`).

### Méthode retenue

```bash
# Versions : une sonde par version, protocole forcé
openssl s_client -connect <hôte>:<port> -cipher 'DEFAULT:@SECLEVEL=0' -tls1   -brief </dev/null
openssl s_client -connect <hôte>:<port> -cipher 'DEFAULT:@SECLEVEL=0' -tls1_1 -brief </dev/null
openssl s_client -connect <hôte>:<port> -cipher 'DEFAULT:@SECLEVEL=0' -tls1_2 -brief </dev/null
openssl s_client -connect <hôte>:<port> -tls1_3 -brief </dev/null

# Échange de clés RSA : le client ne propose que des suites kRSA
openssl s_client -connect <hôte>:<port> -tls1_2 -cipher 'kRSA:@SECLEVEL=0' -brief </dev/null
```

- **`@SECLEVEL=0`** est obligatoire pour les sondes TLS ≤ 1.2 : sans lui, le client refuse TLS 1.0/1.1 avant tout envoi, et un serveur qui les accepte apparaîtrait comme les refusant (faux négatif sur un P0).
- **Pas de `-cipher` pour TLS 1.3** : cette option ne s'applique pas aux suites TLS 1.3.
- **`kRSA`** est la chaîne OpenSSL qui sélectionne uniquement les suites à échange de clés RSA.

**Règles de décision**

| Observation                                                                                 | `versions`      | `rsa_key_exchange`                                                         |
| ------------------------------------------------------------------------------------------- | --------------- | -------------------------------------------------------------------------- |
| Sonde de version : `CONNECTION ESTABLISHED` et `Protocol version` égale à la version forcée | Version ajoutée | —                                                                          |
| Sonde de version : `SSL alert number 70` (protocol version)                                 | Version absente | —                                                                          |
| Sonde `kRSA` : `CONNECTION ESTABLISHED`                                                     | —               | `true`                                                                     |
| Sonde `kRSA` : `SSL alert number 40` (aucune suite commune) ou `70` (pas de TLS 1.2)        | —               | `false`                                                                    |
| N'importe quelle sonde : `no protocols available`                                           | —               | — → `status: error` (erreur de configuration du client, jamais « refusé ») |

**Trois signatures d'échec à ne pas confondre**

| Sortie                                       | Origine | Sens                                                            |
| -------------------------------------------- | ------- | --------------------------------------------------------------- |
| `SSL alert number 70`                        | Serveur | Version refusée : spécifique                                    |
| `SSL alert number 40`                        | Serveur | Rien en commun (groupe, suite…) : générique, dépend de la sonde |
| `tls_setup_handshake:no protocols available` | Client  | Bug de configuration de `pqready`                               |

### Preuves

Lab, 05/11/2026 :

| Sonde        | `faible`                      | `classique`                       |
| ------------ | ----------------------------- | --------------------------------- |
| `-tls1`      | ✅ TLSv1                       | ❌ alert 70                        |
| `-tls1_1`    | ✅ TLSv1.1                     | ❌ alert 70                        |
| `-tls1_2`    | ✅ `AES128-SHA`                | ✅ `ECDHE-ECDSA-AES256-GCM-SHA384` |
| `-tls1_3`    | ❌ alert 70                    | ✅                                 |
| `kRSA`       | ✅ → `true`                    | ❌ alert 40 → `false`              |
| → `versions` | `TLSv1`, `TLSv1.1`, `TLSv1.2` | `TLSv1.2`, `TLSv1.3`              |

Conforme à la configuration nginx des deux serveurs.

### Limites

- **Le cas courant n'est pas testé** : un serveur avec certificat **RSA** mais sans suites `kRSA` (ex. `ECDHE-RSA` seul). Le refus de `classique` était garanti d'avance, puisqu'un échange de clés RSA exige un certificat RSA et que `classique` a un certificat ECDSA. Alerte 40 attendue
- **La sonde `kRSA` ne teste que TLS 1.2.** Un serveur qui n'accepterait l'échange RSA qu'en TLS 1.0/1.1 ne serait pas détecté.
- **Un seul certificat rapporté.** Un serveur peut servir plusieurs certificats selon le client (ex. EC aux clients modernes, RSA aux anciens). `pqready` ne rapporte que celui présenté au client par défaut. Observé en S4 sur un site public : certificat EC rapporté, mais sonde `kRSA` acceptée, donc certificat RSA également servi (voir `docs/notes/s3_spike.md`, section « Scan public (S4) »).
