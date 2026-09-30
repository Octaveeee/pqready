# S1 — Scan manuel d'un endpoint TLS

- **Date** : 30/09/2026
- **Cible** : site vitrine d'une PME, hébergement mutualisé (Plesk sur VPS). Entité anonymisée (règles éthiques).
- **Outils** : SSL Labs (en ligne), testssl.sh 3.3dev (image Docker `ghcr.io/testssl/testssl.sh`), onglet Security de Chrome.
- **Méthode** : un seul scan par outil, connexion TLS standard, aucun test intrusif.

## Résultat global

- SSL Labs : **A+**. testssl : **A+** (score 93).
- **Aucun échange de clés post-quantique** : `KEMs offered: None` (testssl), `PQC Key Exchange: Not Supported` (SSL Labs).
- **Constat clé** : une excellente note classique ne dit rien de l'exposition quantique. Ce site est entièrement exposé au « harvest now, decrypt later ».

## Détail

| Élément | Valeur observée | Vulnérable quantique ? | Exposé HNDL ? | Pourquoi |
|---|---|---|---|---|
| Versions TLS | TLS 1.2 et 1.3 ; SSLv2/v3, TLS 1.0/1.1 refusés | Non pertinent | — | La version du protocole ne protège pas du quantique ; seul l'échange de clés compte. Aucune faiblesse classique. |
| Échange de clés TLS 1.3 | X25519 | **Oui** (Shor) | **Oui** | Courbe elliptique : un CRQC retrouve le secret partagé à partir du trafic enregistré. |
| Échange de clés TLS 1.2 | ECDHE (P-521 négocié par SSL Labs) | **Oui** (Shor) | **Oui** | « Équivalent RSA 15360 bits » = résistance **classique** uniquement. Shor casse toute courbe elliptique, quelle que soit sa taille. |
| Groupes supportés | secp256r1/384r1/521r1, X25519, X448, ffdhe2048→8192 | **Oui** (tous) | **Oui** | ECC et DH en corps fini reposent sur le logarithme discret, cassé par Shor. Aucun groupe hybride (`X25519MLKEM768`). |
| Échange de clés RSA | Absent (pas de `TLS_RSA_*`, ROBOT non applicable) | — | — | Bon point : confidentialité persistante (FS) sur toutes les suites. Pas de P0 de ce côté. |
| Chiffrement symétrique | AES-128/256-GCM, AES-128-CCM, ChaCha20-Poly1305, ARIA-GCM | Faiblement (Grover) | Non | Grover divise la sécurité effective par deux : AES-256 et ChaCha20 restent résistants ; AES-128 est acceptable, à surveiller. |
| Certificat : clé | RSA 2048 bits | **Oui** (Shor) | **Non** | Sert à l'authentification : un attaquant ne peut l'exploiter qu'une fois le CRQC disponible, pas rétroactivement. À planifier. NIST IR 8547 (projet) : RSA 2048 (112 bits) déprécié après 2030, interdit après 2035. |
| Certificat : signature | SHA256withRSA | **Oui** (partie RSA) | Non | SHA-256 résiste (Grover) ; c'est la signature RSA qui est vulnérable. |
| Chaîne | Feuille RSA 2048 → intermédiaire RSA 2048 → racine RSA 4096 (Let's Encrypt) | **Oui** | Non | Toute la chaîne est RSA : la migration vers ML-DSA dépend de l'autorité de certification, pas seulement du site. |
| Expiration | 14/09/2026 → 13/12/2026 (90 jours) | — | — | Valide, renouvellement automatique. Pas de faiblesse classique. |

## Priorité pqready estimée

- **Findings** : `KEX_CLASSICAL_ONLY` (urgent, HNDL) + `CERT_RSA` (à planifier). Aucune faiblesse classique → pas de P0.
- **Mosca** avec Y = 3 ans, Z = 2035 − 2026 = 9 ans : violé si X > 6 ans.
- → **P1** si les données doivent rester confidentielles plus de 6 ans et que leur sensibilité est ≥ 2 ; sinon **P2**.

## Comparaison des outils

| Point | testssl.sh | SSL Labs |
|---|---|---|
| Détection PQC | Oui (`KEMs offered`) | Oui (`PQC Key Exchange`, `Supported PQC Groups`) |
| Sortie exploitable | Texte, `--jsonfile` possible | Web uniquement (API existante, non testée) |
| Particularité | Détecte les KEM via ses propres sockets, malgré un OpenSSL 1.0.2 embarqué | Simulation de nombreux clients, détail de la chaîne |

→ À évaluer en S3 (ADR-001) : testssl.sh comme option de détection, face à `sslyze` et `openssl s_client`.

## Onglet Security de Chrome (4 sites)

| Site | Échange de clés | Remarque |
|---|---|---|
| cloudflare.com | **X25519MLKEM768** | Hybride post-quantique |
| Site e-commerce | **X25519MLKEM768** | Probablement via un CDN (hypothèse non vérifiée) |
| Site d'université | X25519 | Classique |
| Plateforme d'e-learning | X25519 | Classique |

**Constat** : l'hybride dépend surtout du fournisseur d'infrastructure (CDN), pas de la taille ni de la nature de l'organisation.
**Cibles publiques pour S3** : `cloudflare.com` (hybride) et un site classique.

## Ce que je n'ai pas encore compris / à creuser

- Pourquoi la note SSL Labs reste A+ sans PQC : poids du PQC dans le guide de notation (version 2009r) ? À vérifier.
- Les simulations de clients (OpenSSL 3.5, Chrome 137) proposent-elles vraiment `X25519MLKEM768` au serveur ?
- Hors périmètre, noté pour mémoire : BREACH (compression `br`), en-tête `X-Powered-By` exposé.