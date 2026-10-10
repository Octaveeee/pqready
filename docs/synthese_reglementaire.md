# Synthèse réglementaire PQC

> Statut : en cours (S2). Chaque affirmation cite sa source (document, page ou article).

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

## 4. NIST IR 8547

## 5. FIPS 203 / 204 / 205

## 6. Canada (non vérifié)