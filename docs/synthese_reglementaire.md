# Synthèse réglementaire PQC

> Statut : premier jet complet (S2, 09.10.2026), à relire. Chaque affirmation cite sa source (document, page ou article). Vue d'ensemble et points non vérifiés en fin de document.

## 1. Feuille de route PQC de l'UE (NIS Cooperation Group, juin 2025)

- **Source** : *A Coordinated Implementation Roadmap for the Transition to Post-Quantum Cryptography*, Part 1, Version 1.1, EU PQC Workstream (NIS Cooperation Group), 11.06.2025, 17 pages. <https://cyber.gouv.fr/en/publications/jointly-led-international-publications/roadmap-for-the-transition-to-pqc/>
- **Statut** : recommandations **non contraignantes**, adressées aux **États membres** (p. 2, p. 5). C'est le premier livrable du groupe de travail créé à la suite de la Recommandation (UE) 2024/1101 de la Commission du 11.04.2024 (p. 2). Les entités dans le champ de NIS2 « should refer to this document » (p. 5). Les obligations contraignantes viennent de NIS2 et de DORA, qui exigent une cryptographie à l'état de l'art et engagent la responsabilité des dirigeants (p. 3).
- **Ce que dit le texte** :
  - Deux menaces : « store now, decrypt later » pour les données à longue durée de confidentialité, et les longues durées de migration des systèmes complexes comme les PKI (p. 4).
  - Estimation reprise de l'étude du BSI (2024) : un ordinateur quantique capable de casser la cryptographie actuelle est probable d'ici 16 ans au maximum, possiblement 10 ans (p. 4).
  - L'**hybridation** est recommandée : « standardised and tested hybrid solutions, whenever feasible and suitable » (p. 3, p. 6).
  - L'**inventaire cryptographique** est un « First Step » et un « no-regret move » pour toute entité ; les États membres doivent le promouvoir et le soutenir. Un format standardisé comme le CBOM est recommandé (p. 11).
  - Trois niveaux de risque quantique (faible, moyen, élevé). Un cas d'usage est à **haut risque** si la confidentialité doit être protégée **au moins 10 ans** et qu'une attaque après 10 ans aurait encore un impact significatif, ou si l'effort de migration dépasse 8 ans avec un impact élevé (p. 8, p. 10). La méthode reprend les grandeurs du théorème de Mosca (p. 10).
- **Échéances** (p. 7) :
  - **31.12.2026** : First Steps mis en œuvre par tous les États membres ; feuilles de route nationales initiales établies ; planification et pilotes lancés pour les cas à risque élevé et moyen.
  - **31.12.2030** : transition **terminée pour les cas à haut risque** ; planification et pilotes terminés pour le risque moyen ; mises à jour logicielles et firmware résistantes au quantique activées par défaut. Les mécanismes à clé publique vulnérables ne doivent plus être utilisés seuls pour les cas à haut risque (p. 6).
  - **31.12.2035** : transition terminée pour le risque moyen ; pour le risque faible, « as much as feasible ». Date alignée sur NIST IR 8547 (projet) et le NCSC britannique (p. 9).
- **Impact sur pqready** :
  - L'outil répond au First Step « inventaire cryptographique », limité aux endpoints TLS.
  - L'échéance 2026 vise les États, pas les entités : le rapport ne doit pas la présenter comme une obligation pour l'organisation scannée. 
  - L'estimation du BSI (10 à 16 ans à partir de 2024) sert de source à l'hypothèse Z = 2035, côté prudent. 
  - Finding « échange de clés non hybride » → référence `EU_PQC_ROADMAP` (recommandation d'hybridation, échéance 2030 pour le haut risque).

## 2. ANSSI

- **Sources** :
  - [A22] *ANSSI views on the Post-Quantum Cryptography transition*, 30.03.2022, 7 pages. <https://messervices.cyber.gouv.fr/documents-guides/EN_Position.pdf>
  - [A23] *ANSSI views on the Post-Quantum Cryptography transition (2023 follow up)*, 21.12.2023, 7 pages, addendum à [A22]. <https://messervices.cyber.gouv.fr/documents-guides/follow_up_position_paper_on_post_quantum_cryptography.pdf>
  - [FAQ] *FAQ sur la cryptographie post-quantique (PQC)*, page web non datée, consultée le 09.10.2026. <https://cyber.gouv.fr/enjeux-technologiques/cryptographie-post-quantique/faq-pqc/>
- **Statut** : avis et recommandations de l'autorité nationale, **non contraignants** pour la plupart des organisations. Le périmètre réglementé en cryptographie se limite aux données classifiées ou Diffusion Restreinte, aux systèmes d'information d'importance vitale (SAIV) et aux visas de sécurité (certification, qualification)
- **Ce que dit le texte** :
  - **Deux menaces distinctes.** Le « store now, decrypt later » vise l'échange de clés et agit rétroactivement [A22, p. 1]. La falsification de signatures n'est possible qu'une fois le CRQC disponible : les signatures vérifiées à la volée, comme dans un canal authentifié, ne sont pas touchées avant [A22, p. 2].
  - **Hybridation.** Déployer du PQC n'est pas obligatoire aujourd'hui, mais dès qu'on en déploie, l'hybridation est **obligatoire** en phases 1 et 2 [A22, p. 4]. L'ANSSI « strongly emphasizes the necessity of hybridation wherever post-quantum mitigation is needed both in the short and medium term » [A23, p. 2]. Cela vaut pour l'échange de clés et pour les signatures. Exception : les signatures à base de hachage (XMSS, LMS, SPHINCS+), pour lesquelles l'hybridation est facultative [A22, p. 5 ; A23, p. 4 et 6].
  - **Pas de remplacement direct.** L'ANSSI n'approuvera aucun remplacement direct des algorithmes actuels à court ou moyen terme, mais cette immaturité ne doit pas servir à repousser les premiers déploiements [A22, p. 4].
  - **Qui est concerné en priorité.** Les produits qui doivent protéger l'information après 2030, ou qui seront encore utilisés après 2030 sans mise à jour [A22, p. 5 ; A23, p. 2].
  - **Algorithmes.** Pas de liste fermée. Exemples jugés appropriés : ML-KEM (Kyber) et FrodoKEM pour l'échange de clés ; ML-DSA (Dilithium), FN-DSA (Falcon), XMSS/LMS et SLH-DSA (SPHINCS+) pour les signatures. Niveau de sécurité NIST 5 de préférence, ou 3 [A23, p. 2-4].
  - **Symétrique.** Par prudence, au moins le niveau d'AES-256 et de SHA2-384. L'ANSSI précise que c'est légèrement plus conservateur que le NIST et le BSI [A22, p. 5 ; A23, p. 2].
  - **Inventaire.** Chaque organisation doit inventorier les produits et usages qui intègrent de la cryptographie, les algorithmes utilisés et les données à protéger après 2030, en précisant cette durée [FAQ].
- **Calendrier** :
  - Trois phases, qui décrivent ce que les **visas de sécurité** attestent [A22, p. 4 à 7] :
    - **Phase 1** (aujourd'hui, jusqu'après 2025) : le PQC hybride est une défense en profondeur optionnelle ; le visa n'atteste que la sécurité pré-quantique.
    - **Phase 2** (pas avant 2025, jusqu'à au moins 2030) : la résistance quantique peut être revendiquée et évaluée ; hybridation toujours obligatoire.
    - **Phase 3** (probablement pas avant 2030) : PQC seul possible, hybridation facultative.
  - L'ANSSI a accéléré ce calendrier : premiers visas de phase 2 attendus vers 2024-2025 [A23, p. 1 et 6].
  - **2027** : l'ANSSI vise des obligations PQC pour l'entrée en qualification des produits [FAQ].
  - **2030** : ne plus acheter de produits qui n'intègrent pas de PQC [FAQ].
  - Ces dates visent les produits et les achats. Ce ne sont pas des échéances de migration imposées aux organisations, et l'ANSSI indique que le calendrier peut être avancé ou ralenti [A22, p. 6].
- **Impact sur pqready** :
  - La distinction entre échange de clés (urgent, rétroactif) et signature (à planifier) qui structure les priorités de pqready est celle de l'ANSSI.
  - `X25519MLKEM768` combine X25519 et ML-KEM-768 (niveau 3) : c'est un échange hybride au sens de l'ANSSI, d'où son classement « résistant ».
  - Un échange de clés uniquement post-quantique, sans composante classique, ne suivrait pas la recommandation de l'ANSSI avant la phase 3. Cas absent de la table de classification : à traiter ou à lister dans les limites.
  - La table de classification range SHA-256 parmi les résistants et AES-128 parmi les « à surveiller ». L'ANSSI encourage SHA2-384 et AES-256.
  - Le rapport ne doit pas présenter les phases ANSSI comme une obligation pour l'organisation scannée, sauf si elle relève du périmètre réglementé.
  - Référence `ANSSI_HYBRID` : à rattacher aux findings sur l'échange de clés et sur la signature du certificat.

## 3. DORA — RTS 2024/1774, art. 6 et 7

- **Sources** :
  - [DORA] Règlement (UE) 2022/2554 du 14.12.2022 sur la résilience opérationnelle numérique du secteur financier, JO L 333 du 27.12.2022. <https://eur-lex.europa.eu/eli/reg/2022/2554/oj/eng>
  - [RTS] Règlement délégué (UE) 2024/1774 de la Commission du 13.03.2024 (normes techniques de réglementation sur la gestion du risque TIC), JO L du 25.06.2024, 37 pages. <https://eur-lex.europa.eu/eli/reg_del/2024/1774/oj/eng>
- **Statut** : **contraignant**. Les deux textes sont des règlements, obligatoires et directement applicables dans tous les États membres [RTS, art. 42]. DORA s'applique depuis le 17.01.2025 [DORA, art. 64]. Les articles 6 et 7 du RTS relèvent du titre II, c'est-à-dire du cadre complet de gestion du risque TIC, le cadre simplifié du titre III n'est pas couvert par cette synthèse.
- **Ce que dit le texte** :
  - **Base dans DORA.** Les entités financières doivent maintenir un haut niveau de disponibilité, d'authenticité, d'intégrité et de confidentialité des données, au repos, en usage ou en transit [DORA, art. 9(2)], et protéger les clés cryptographiques [DORA, art. 9(4)(d)].
  - **Politique de chiffrement obligatoire.** Elle doit être élaborée, documentée et mise en œuvre [RTS, art. 6(1)], sur la base d'une classification des données et d'une évaluation du risque TIC. Elle couvre le chiffrement au repos et en transit, en usage si nécessaire, les connexions réseau internes et le trafic avec l'extérieur, et la gestion des clés [RTS, art. 6(2)].
  - **Choix des techniques.** La politique fixe des critères de sélection fondés sur les « leading practices » et les normes. L'entité qui ne peut pas s'y conformer adopte des mesures d'atténuation et de surveillance [RTS, art. 6(3)].
  - **Mise à jour selon la cryptanalyse.** La politique contient des « provisions for updating or changing, where necessary, the cryptographic technology on the basis of developments in cryptanalysis ». L'entité qui ne peut pas mettre à jour adopte des mesures d'atténuation et de surveillance [RTS, art. 6(4)].
  - **Traçabilité.** Ces mesures d'atténuation doivent être consignées, avec une explication motivée [RTS, art. 6(5)].
  - **Cycle de vie des clés.** Génération, renouvellement, stockage, sauvegarde, archivage, révocation, destruction ; protection contre la perte et l'accès non autorisé ; remplacement en cas de perte ou de compromission [RTS, art. 7(1) à 7(3)].
  - **Registre des certificats.** L'entité crée et tient à jour un registre de tous les certificats et des dispositifs qui les stockent, au moins pour les actifs TIC qui soutiennent des fonctions critiques ou importantes [RTS, art. 7(4)]. Elle renouvelle les certificats avant leur expiration [RTS, art. 7(5)].
  - **Le quantique n'apparaît que dans un considérant.** Les entités devraient suivre une approche souple pour faire face aux menaces cryptographiques, « including threats from quantum advancements » [RTS, considérant 9, p. 2]. Aucun article ne cite le quantique ni le post-quantique, et aucune échéance de migration n'est fixée. Un considérant éclaire l'interprétation mais ne crée pas d'obligation.
- **Échéances** : aucune échéance propre au post-quantique. Les obligations ci-dessus s'appliquent depuis le 17.01.2025.
- **Impact sur pqready** :
  - C'est le seul texte **contraignant** de cette synthèse pour une banque ou une assurance en France. Le rapport doit le distinguer nettement des recommandations (sections 1, 2 et 4).
  - L'art. 7(4) impose un registre des certificats : pqready en produit une partie, pour les endpoints TLS exposés (type et taille de clé, signature, expiration).
  - L'art. 7(5) justifie le finding « certificat expiré » en P0.
  - L'art. 6(4) ne dit pas « migrez vers le PQC ». Il oblige à prévoir la mise à jour de la cryptographie selon l'état de la cryptanalyse et, à défaut, à documenter des mesures d'atténuation. Formulation à respecter dans le rapport : un échange de clés non hybride est un point à traiter dans la politique de chiffrement, pas une non-conformité.
  - Référence `DORA_RTS_ART6` : à rattacher aux findings quantiques (art. 6(3) et 6(4)) et aux findings sur les certificats (art. 7(4) et 7(5)).

## 4. NIST IR 8547

- **Source** : [IR] NIST IR 8547 ipd, *Transition to Post-Quantum Cryptography Standards*, Initial Public Draft, novembre 2024, 29 pages. <https://nvlpubs.nist.gov/nistpubs/ir/2024/NIST.IR.8547.ipd.pdf>

- **Statut** : **projet**, non finalisé. Consultation publique close le 10.01.2025 ; la page NIST n'affiche toujours que la version « Initial Public Draft » (consultée le 09.10.2026, <https://csrc.nist.gov/pubs/ir/8547/ipd>). Le texte décrit l'approche attendue du NIST et vise les agences fédérales américaines, les fournisseurs de technologies et les organismes de normalisation [IR, p. 2]. Aucune portée juridique en Europe : c'est une référence internationale, reprise par la feuille de route de l'UE pour justifier la date de 2035 (section 1).

- **Ce que dit le texte** :
  
  - **Durée d'une migration.** De la normalisation d'un algorithme à son intégration complète, il faut historiquement 10 à 20 ans [IR, p. 1].
  - **Théorème de Mosca.** Si X est la durée pendant laquelle les données doivent rester sûres, Y la durée de la migration et Z le délai avant un CRQC, il faut commencer avant que X + Y dépasse Z [IR, p. 7].
  - **Échange de clés et authentification ne sont pas exposés de la même façon.** Un système d'authentification reste sûr tant que ses algorithmes le sont au moment de l'authentification, le « harvest now, decrypt later » concerne l'établissement de clés. Dans TLS, les deux peuvent donc migrer à des dates différentes [IR, p. 7-8].
  - **Priorité à l'échange de clés.** Le NIST compte prioriser la migration des schémas d'établissement de clés, « particularly in interactive protocols like TLS and IKE », et des guides par application pourront imposer des dates plus précoces que 2035 [IR, p. 15 et 17].
  - **Hybridation tolérée, pas recommandée.** Le NIST « intends to accommodate » les techniques hybrides, les décrit comme des mesures typiquement temporaires qui ajoutent de la complexité, et laisse la décision à chaque application [IR, p. 8 à 10]. Position plus réservée que celle de l'ANSSI et de la feuille de route de l'UE.
  - **Symétrique.** Le NIST ne prévoit pas d'abandonner ses standards symétriques ; les primitives offrant au moins 128 bits de sécurité classique atteignent au moins la catégorie 1 [IR, p. 5 et 15].

- **Échéances** (tableaux 2 et 4, [IR, p. 13-14]) :
  
  | Famille                                  | Niveau de sécurité | Transition                                   |
  | ---------------------------------------- | ------------------ | -------------------------------------------- |
  | Signatures ECDSA, RSA                    | 112 bits           | Dépréciées après 2030, interdites après 2035 |
  | Signatures ECDSA, EdDSA, RSA             | ≥ 128 bits         | Interdites après 2035                        |
  | Établissement de clés DH, ECDH, MQV, RSA | 112 bits           | Dépréciés après 2030, interdits après 2035   |
  | Établissement de clés DH, ECDH, MQV, RSA | ≥ 128 bits         | Interdits après 2035                         |
  
  - « Déprécié » : l'algorithme reste utilisable, mais avec un risque que le propriétaire des données doit évaluer. « Interdit » : il n'est plus autorisé pour l'usage visé [IR, p. 12].
  - 2035 est l'objectif fixé par le National Security Memorandum 10 pour les systèmes fédéraux américains [IR, p. 11].

- **Impact sur pqready** :
  
  - Le NIST donne une source directe pour l'inégalité de Mosca et pour la séparation entre échange de clés (urgent) et authentification (à planifier).
  - Dans le rapport, toujours écrire « projet » : ces dates peuvent changer dans la version finale.
  - Référence `NIST_IR_8547` : échéances de comparaison internationale, jamais présentées comme une obligation pour une entité française.

## 5. FIPS 203 / 204 / 205

- **Sources** : normes fédérales américaines publiées et entrées en vigueur le 13.08.2024.
  
  - [F203] FIPS 203, *Module-Lattice-Based Key-Encapsulation Mechanism Standard*. <https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf>
  - [F204] FIPS 204, *Module-Lattice-Based Digital Signature Standard*. <https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf>
  - [F205] FIPS 205, *Stateless Hash-Based Digital Signature Standard*. <https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.205.pdf>

- **Statut** : normes **finales**. Ce sont des spécifications techniques d'algorithmes, pas des textes qui imposent une migration. Elles servent de référence aux protocoles (TLS) et aux recommandations européennes.

- **À quoi sert chacune** :
  
  | Norme    | Algorithme | Rôle                                   | Issu de            | Jeux de paramètres (catégorie de sécurité)      |
  | -------- | ---------- | -------------------------------------- | ------------------ | ----------------------------------------------- |
  | FIPS 203 | ML-KEM     | Établissement de clés (KEM)            | CRYSTALS-Kyber     | ML-KEM-512 (1), ML-KEM-768 (3), ML-KEM-1024 (5) |
  | FIPS 204 | ML-DSA     | Signature                              | CRYSTALS-Dilithium | ML-DSA-44 (2), ML-DSA-65 (3), ML-DSA-87 (5)     |
  | FIPS 205 | SLH-DSA    | Signature à base de hachage, sans état | SPHINCS+           | 12 jeux, catégories 1, 3 et 5                   |

- **Ce qu'il faut retenir** :
  
  - ML-KEM remplace l'échange de clés (ECDH, DH, RSA) ; ML-DSA et SLH-DSA remplacent les signatures (RSA, ECDSA, EdDSA).
  - ML-KEM est à ce jour le seul schéma post-quantique d'établissement de clés approuvé par le NIST, d'autres sont attendus [IR, p. 15].
  - Une norme dérivée de FALCON (FN-DSA) est prévue [IR, p. 3]. Non vérifié : si elle a été publiée depuis.
  - Les catégories de sécurité se comparent à AES : 1 = AES-128, 3 = AES-192, 5 = AES-256 [IR, tableau 1, p. 12].

- **Impact sur pqready** :
  
  - `X25519MLKEM768` utilise ML-KEM-768, catégorie 3 : niveau accepté par l'ANSSI (« de préférence 5, ou 3 », section 2).
  - Dans le rapport, la recommandation de remplacement suit ce tableau : échange de clés → hybride avec ML-KEM, signature du certificat → ML-DSA ou SLH-DSA quand l'autorité de certification le proposera.
  - Référence `NIST_FIPS_203_205` : recommandations de remplacement uniquement. 





## Vue d'ensemble

| Texte                              | Contraignant pour une banque française ? | Échéance utile                                  | Ce qu'il apporte à pqready                                                            |
| ---------------------------------- | ---------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------- |
| Feuille de route PQC de l'UE       | Non (recommandations aux États membres)  | 2030 haut risque, 2035 risque moyen             | Calendrier, définition du haut risque (10 ans), inventaire                            |
| ANSSI (avis 2022, suivi 2023, FAQ) | Non, hors périmètre réglementé           | 2027 qualification, 2030 achats                 | Hybridation, distinction échange de clés / signature                                  |
| DORA et RTS 2024/1774              | **Oui**                                  | En vigueur depuis le 17.01.2025                 | Politique de chiffrement, mise à jour selon la cryptanalyse, registre des certificats |
| NIST IR 8547 (projet)              | Non                                      | 2030 dépréciation (112 bits), 2035 interdiction | Mosca, priorité à l'échange de clés                                                   |
| FIPS 203 / 204 / 205               | Non                                      | —                                               | Algorithmes de remplacement                                                           |

## Points non vérifiés

- NIST SP 800-57 partie 1 (correspondance taille de clé / niveau de sécurité) : non lue.
- OSFI B-13 : non lue directement.
- Publication éventuelle de la norme FN-DSA (FALCON) et d'une version finale de NIST IR 8547 : à recontrôler avant la V1.
- Recommandation (UE) 2024/1101 de la Commission : citée par la feuille de route, non lue.