# Analyse juridique — que peut-on publier des données Facebook Marketplace ?

> Date : 2026-08-22
> Projet : fb-shopper — site public de petites annonces en Polynésie française
> **Ceci n'est pas un avis juridique.** C'est une analyse technique de la
> littérature et de la jurisprudence disponibles, destinee a preparer une
> consultation avec un avocat. Le § 9 liste les questions a lui poser.

---

## 0. Reponse courte

**Republier sur un site concurrent les annonces extraites de Facebook
Marketplace est l'usage le plus expose juridiquement de tous ceux envisages
dans ce projet.** Ce n'est pas une zone grise : c'est exactement le schema de
fait juge dans l'affaire *Leboncoin c/ Entreparticuliers*, ou le republieur a
ete condamne. Dans ce scenario, le projet tiendrait le role
d'Entreparticuliers.

La zone reellement sure est etroite :

| | |
|---|---|
| **Publiable** | des liens, tes propres annonces, des statistiques agregees construites avec precaution |
| **Non publiable** | photos, identite des vendeurs, descriptions, et le corpus d'annonces lui-meme — meme partiel, meme reformule, meme avec un lien vers la source |

La question ajoutee sur les statistiques est la bonne piste, mais elle deplace
le risque au lieu de le supprimer : voir § 7, qui distingue deux problemes
juridiques qu'il ne faut surtout pas confondre.

---

## 1. Quel droit s'applique ? Le point le plus souvent faux

La Polynesie francaise n'est **pas** un departement d'outre-mer. C'est une
collectivite d'outre-mer dotee de l'autonomie, et au regard de l'Union
europeenne un **PTOM** (pays et territoire d'outre-mer), pas une **RUP**
(region ultraperipherique). Consequence : **le droit de l'Union ne s'y applique
pas de plein droit.** Trois blocs, trois regimes differents.

### 1.1 Donnees personnelles — regime quasi metropolitain

Le RGPD, en tant que reglement europeen, n'est pas directement applicable en
Polynesie francaise. Mais la loi « Informatique et Libertes » (loi n° 78-17),
reecrite par l'ordonnance n° 2018-1125 du 12 decembre 2018, **y est applicable
depuis le 1er juin 2019**, et elle rend applicables les dispositions du RGPD
par renvoi. La CNIL est competente. Un titre specifique de la loi prevoit
quelques adaptations pour la Polynesie, Wallis-et-Futuna, la Nouvelle-Caledonie
et les TAAF.

> **En pratique : raisonner comme si le RGPD s'appliquait.** L'ecart theorique
> n'offre aucune marge de manoeuvre exploitable.

### 1.2 Propriete intellectuelle — regime **polynesien**, et c'est decisif

La propriete intellectuelle est une **competence du Pays** depuis la loi
organique n° 2004-192 du 27 fevrier 2004. Le Conseil constitutionnel l'a
confirme (decision n° 2014-6 LOM du 7 novembre 2014) : le droit d'auteur et
les droits voisins relevent pour l'essentiel de la Polynesie, l'Etat ne gardant
que ce qui touche au droit penal, a la procedure penale et au statut de ses
agents.

La Polynesie a donc **son propre code de la propriete intellectuelle**, distinct
du CPI metropolitain.

> **QUESTION OUVERTE N° 1, ET ELLE EST DETERMINANTE.**
> Le code de la propriete intellectuelle de la Polynesie francaise
> comporte-t-il un **droit sui generis du producteur de bases de donnees**,
> equivalent aux articles L341-1 a L343-7 du CPI metropolitain ?
>
> Je n'ai **pas pu le verifier** : le serveur Lexpol (lexpol.cloud.pf), seul
> depositaire en ligne du code polynesien, a renvoye des erreurs 503 pendant
> toutes mes tentatives. C'est la premiere chose a verifier, parce que toute la
> suite en depend cote polynesien.
>
> Attention toutefois : meme une reponse negative ne mettrait pas le projet a
> l'abri, pour la raison exposee au § 1.4.

### 1.3 Responsabilite civile — parasitisme et concurrence deloyale

Le droit des obligations et la responsabilite civile delictuelle (art. 1240 du
code civil) s'appliquent. Le **parasitisme** — se placer dans le sillage
economique d'autrui pour profiter sans bourse delier de ses investissements —
est une construction pretorienne autonome, qui n'exige **aucun droit privatif**.

C'est le filet de securite du demandeur : meme si le droit sui generis
n'existait pas en droit polynesien, un site tahitien vivant des annonces
collectees chez Facebook resterait attaquable sur ce fondement. Reprendre le
travail d'autrui pour lui faire concurrence est le coeur meme de la
qualification.

### 1.4 Le risque ne vient pas seulement du droit polynesien

Meme dans l'hypothese la plus favorable en droit local, trois voies restent
ouvertes a Meta :

1. **Meta Platforms Ireland Ltd est une societe irlandaise**, donc
   ressortissante d'un Etat membre de l'UE. La condition de rattachement du
   droit sui generis (art. L341-2 CPI, transposant l'art. 11 de la directive
   96/9/CE) est remplie sans difficulte : Meta peut agir en France ou en
   Irlande.
2. **Un site web public est accessible depuis l'UE.** Le critere de
   focalisation permet de rattacher le litige a une juridiction europeenne des
   lors que le site vise, meme accessoirement, un public europeen — et un site
   polynesien francophone en fait partie.
3. **Les CGU de Meta comportent une clause attributive de juridiction** dont il
   faut verifier la portee dans le cas d'espece.

> **A retenir : le rattachement polynesien attenue peut-etre l'exposition, il ne
> la supprime pas.** Construire la strategie sur l'idee que « la Polynesie est
> hors UE » serait une erreur de conception.

---

## 2. Le precedent qui decide de tout : *Leboncoin c/ Entreparticuliers*

**Cour d'appel de Paris, 2 fevrier 2021, RG n° 17/17688** (pourvoi n° 21-16.307
ensuite examine par la Cour de cassation le 5 octobre 2022, qui a consolide
l'analyse de l'investissement substantiel).

### Les faits

Entreparticuliers.com collectait quotidiennement les annonces immobilieres de
leboncoin.fr et les rediffusait a ses abonnes. Un constat d'huissier releve
que **sur 70 annonces « vente », 69 reproduisaient le contenu Leboncoin ; sur
100 annonces « location », 96**.

### Ce que la cour a juge

- **Investissement substantiel caracterise** : environ 50 salaries dedies, et
  pour la seule sous-base immobiliere 5 M€ de campagnes publicitaires et 20 M€
  d'acquisition d'une societe enrichissant cette sous-base sur trois ans. La
  cour a **refuse** de mettre ces investissements en balance avec le chiffre
  d'affaires ou la rentabilite.
- **Une sous-base est protegeable de facon autonome** — ici la seule categorie
  immobiliere.
- Les elements repris — **localisation, surface, prix, description,
  photographie** — constituent « les criteres essentiels des annonces ».
- **Condamnation** sur le fondement des articles L.341-1 et **L.342-2** du CPI :
  **50 000 € de prejudice financier + 20 000 € de prejudice d'image.**
- **Le lien hypertexte vers la source ne sauve pas** le republieur, et **le but
  de l'extraction est indifferent** a la qualification.

### Pourquoi ce precedent est plus dangereux ici que la-bas

Trois raisons, toutes defavorables :

1. **Le fondement retenu est l'article L.342-2**, celui qui vise les
   extractions **repetees et systematiques de parties non substantielles**
   excedant les conditions normales d'utilisation. C'est precisement ce que
   fait un agregateur qui interroge une source en continu. **On ne s'en sort
   donc pas en extrayant « peu a la fois ».**
2. **L'investissement de Meta dans le Marketplace ecrase celui de Leboncoin.**
   Si 50 salaries suffisent a caracteriser l'investissement substantiel, la
   question ne se plaidera meme pas.
3. **Entreparticuliers rediffusait a des abonnes ; le projet publierait en
   acces libre sur un site concurrent.** L'atteinte est plus visible, plus
   facile a constater par huissier, et le prejudice d'image plus simple a
   etablir.

La jurisprudence posterieure durcit encore le ton : astreintes de l'ordre de
500 €/annonce et dommages-interets a six chiffres ont ete prononces dans des
affaires comparables.

---

## 3. *Meta c/ Bright Data* ne constitue pas une protection

C'est la decision qu'on cite toujours pour justifier le scraping. Elle ne
s'applique pas ici, pour quatre raisons.

En janvier 2024, le juge Chen (N.D. Cal.) a donne raison a Bright Data : les
CGU de Facebook et Instagram **ne prohibaient pas** le scraping de donnees
publiques en etat deconnecte.

Mais :

1. **C'est du droit americain** — contrat et CFAA. Le droit sui generis des
   bases de donnees **n'existe pas aux Etats-Unis**. La decision ne dit
   strictement rien du risque principal ici.
2. **Meta a modifie ses CGU au 1er janvier 2025** pour fermer cette breche.
   Le texte actuel interdit la collecte automatisee « **regardless of whether
   such automated access or collection is undertaken while logged-in to a
   Facebook account** ». La faille exploitee par Bright Data est comblee.
3. La decision reposait aussi sur le fait que Bright Data avait **resilie ses
   comptes** Meta, ce qui la deliait du contrat. Un editeur qui detient un
   compte Facebook personnel ou professionnel n'est pas dans cette situation.
4. Elle ne dit rien du **droit d'auteur des vendeurs** sur leurs photos, ni du
   droit des **donnees personnelles**.

> Notre probe technique a d'ailleurs montre (voir `RESULTATS_PROBE.md`) que
> Facebook oppose desormais un **rate limit a zero** aux appels non
> authentifies et un **mur de login** sur `/marketplace/search/`. Ce sont des
> **mesures techniques de restriction d'acces**. Les contourner deteriore
> nettement la position juridique : les CGU de Meta interdisent explicitement
> de « contourner, outrepasser ou neutraliser » de telles mesures, et
> l'existence d'une barriere technique franchie volontairement pese lourd dans
> l'appreciation de la mauvaise foi.

---

## 4. Passer par Apify ne purge aucun droit

Point important, parce que c'etait l'option retenue avant cette analyse.

Apify est un **prestataire technique**, pas un fournisseur de licence. Ses
conditions generales sont explicites : *« You are solely responsible for the
legality, accuracy, quality, appropriateness, and use of all Customer Data. »*
Sa responsabilite totale est par ailleurs plafonnee a **1 000 $**.

Autrement dit : Apify change le **mode d'acces technique**, pas la
**qualification juridique de la reutilisation**. Le contrat te transfere la
charge de la conformite. Si Meta ou un vendeur agit, c'est contre l'editeur du
site, pas contre Apify — et l'indemnisation eventuelle d'Apify est plafonnee a
1 000 $.

La meme analyse vaut pour RapidAPI et pour tout revendeur de donnees scrapees :
**nul ne peut ceder plus de droits qu'il n'en detient.**

---

## 5. Categorisation des donnees par risque juridique

Echelle : **ROUGE** = ne pas publier · **ORANGE** = risque eleve, dissuasif ·
**JAUNE** = envisageable sous conditions strictes · **VERT** = risque faible.

### 5.1 ROUGE — a exclure du produit

| Donnee | Fondements du risque | Pourquoi c'est rouge |
|---|---|---|
| **Photographies des annonces** | Droit d'auteur du **vendeur** (pas de Meta) ; droit a l'image si personnes ou biens identifiables | Contrefacon. Le vendeur est titulaire et peut agir seul. Aucune base contractuelle ne peut etre obtenue a l'echelle. Y compris les miniatures et le hotlinking. |
| **Identite du vendeur** (nom, prenom, photo de profil, lien vers le profil) | Donnees personnelles ; loi 78-17 | Aucune base legale mobilisable. L'interet legitime ne resiste pas a la mise en balance quand la finalite est de concurrencer la plateforme source. Obligation d'information de l'art. 14 RGPD (collecte indirecte) impossible a satisfaire a l'echelle. |
| **Coordonnees** (telephone, e-mail, lien de messagerie) | Donnees personnelles + prospection | Cumule le risque « donnees personnelles » et le risque « demarchage ». La CNIL a deja sanctionne la reutilisation de donnees moissonnees sans information ni consentement (deliberation du 8 decembre 2020, affaire de reutilisation de donnees LinkedIn). |
| **Geolocalisation fine** (adresse, coordonnees GPS precises) | Donnees personnelles ; securite des personnes | Donnee sensible en pratique sur un territoire de 280 000 habitants ou l'identification est immediate. |
| **Le corpus d'annonces**, meme partiel, meme reformule | Droit sui generis (L341-1, **L342-2**) ; parasitisme | **C'est le cas Leboncoin.** La reformulation ne fait pas disparaitre l'extraction : ce qui est protege, c'est le contenu de la base, pas sa forme d'expression. |
| **Description integrale de l'annonce** | Droit d'auteur du vendeur si le texte est original ; sui generis | Une annonce redigee peut porter l'empreinte de son auteur. Et c'est un « critere essentiel » au sens de l'arret Leboncoin. |

### 5.2 ORANGE — techniquement possible, economiquement irrationnel

| Donnee | Fondements du risque | Analyse |
|---|---|---|
| **Titre + prix + commune + date**, en volume | Sui generis ; parasitisme | On croit souvent que se limiter aux « donnees factuelles » protege. **Faux** : ce sont exactement les elements que la cour a qualifies de « criteres essentiels » dans l'arret Leboncoin. Le caractere factuel d'une donnee n'empeche pas qu'elle soit une partie substantielle d'une base. |
| **Collecte continue de faible volume** | **L342-2 CPI** | Le texte vise precisement les extractions **repetees et systematiques** de parties **non substantielles**. Etaler la collecte dans le temps **aggrave** la qualification au lieu de l'attenuer. |
| **Deep links + copie du titre et du prix** | Sui generis | Le lien hypertexte seul est licite. Accompagne d'une copie du contenu, l'ensemble se requalifie en reutilisation : la cour a juge que le lien vers la source ne fait pas obstacle a la condamnation. |
| **Donnees agregees a maille fine** (prix median par commune et par mois) | Loi 78-17 (reidentification) | Sur un marche de la taille de Tahiti, un agregat fin redevient une donnee personnelle. Voir § 7.2. |

### 5.3 JAUNE — envisageable, sous conditions strictes et avec conseil

| Usage | Conditions cumulatives |
|---|---|
| **Citation editoriale ponctuelle** (« les 5 meilleures affaires de la semaine ») | Volume tres faible, selection editoriale humaine reelle, texte propre, **aucune photo reprise**, lien vers la source, **pas d'automatisation**. Le passage a l'echelle ou l'automatisation fait basculer en orange puis en rouge. |
| **Veille concurrentielle interne, non publiee** | Usage strictement interne, pas de rediffusion, pas de revente, retention courte, aucune donnee personnelle conservee. Reste une extraction au sens de L342-1, mais sans reutilisation publique le prejudice est difficile a etablir. |
| **Statistiques agregees** | Voir § 7 — c'est la piste la plus serieuse, mais elle a ses propres conditions. |

### 5.4 VERT — exploitable

| Usage | Pourquoi c'est sur |
|---|---|
| **Lien hypertexte simple**, sans copie de contenu | Le lien vers un contenu librement accessible est licite (jurisprudence constante de la CJUE en matiere de liens). Sans reproduction, il n'y a ni extraction ni reutilisation. |
| **Tes propres annonces**, deposees par tes utilisateurs | Tu en es le producteur. Mieux : **tu peux invoquer le droit sui generis a ton tour** contre qui te scraperait. |
| **Sources publiques et officielles** | ISPF (Institut de la statistique de la Polynesie francaise), open data, publications administratives. Verifier la licence de reutilisation, souvent tres permissive. |
| **Graph API officielle de Meta** avec App Access Token | Pour lire une Page publique, c'est la voie contractuellement propre. Perimetre limite mais juridiquement net. |
| **Donnees obtenues sous licence** | Partenariat ou contrat avec la source. Seule voie qui securise reellement la reutilisation d'un corpus tiers. |

---

## 6. Une asymetrie a garder en tete

Les droits en cause n'appartiennent pas tous a la meme personne, et cela change
la strategie de defense :

| Element | Titulaire | Qui peut agir |
|---|---|---|
| La **base** d'annonces | Meta (producteur) | Meta |
| Les **photos** | Le vendeur | Chaque vendeur, individuellement |
| Le **texte** de l'annonce | Le vendeur | Chaque vendeur, individuellement |
| Les **donnees personnelles** | La personne concernee | La personne **et** la CNIL, d'office |

Consequence pratique : **une hypothetique tolerance de Meta ne protegerait de
rien.** Un seul vendeur mecontent, ou un signalement a la CNIL, suffit a ouvrir
un contentieux — et sur un territoire de 280 000 habitants, ou un site
d'annonces local est immediatement visible de tous, la probabilite qu'un
vendeur reconnaisse sa propre annonce republiee sans son accord est elevee.

---

## 7. Statistiques anonymes : ce qui marche, ce qui ne marche pas

C'est la bonne question, et la piste la plus prometteuse. Mais elle recouvre
**deux problemes juridiques distincts** que l'agregation ne resout pas de la
meme facon.

### 7.1 Le raisonnement en une phrase

> L'anonymisation regle le probleme des **donnees personnelles**.
> Elle ne regle **pas** celui du **droit sui generis**, parce que l'infraction
> se situe a l'**extraction**, pas a la publication.
>
> Autrement dit : le risque se deplace de « ce que tu publies » vers
> « **comment tu l'obtiens** ». Le produit fini devient defendable ; le
> procede reste attaquable.

### 7.2 Volet donnees personnelles — soluble, mais pas trivialement

Une donnee reellement anonyme sort du champ de la loi 78-17. Le critere est
celui du G29 repris par la CNIL : l'anonymisation n'est acquise que si les
**trois** risques sont ecartes.

| Critere | Question | Le piege polynesien |
|---|---|---|
| **Individualisation** | Peut-on isoler un individu dans le jeu ? | « Prix median des Hilux a Punaauia en mars, n = 3 » individualise. |
| **Correlation** | Peut-on relier deux enregistrements a la meme personne ? | Recoupement avec l'annonce encore en ligne sur Facebook. |
| **Inference** | Peut-on deduire un attribut a partir des autres ? | Sur un petit marche, « le seul bateau de peche a plus de 8 M XPF vendu en juillet » designe une personne. |

**Regles operationnelles a respecter :**

- **Seuil minimal d'agregation** : ne jamais publier une statistique reposant
  sur moins de **k** observations. Viser **k ≥ 10** plutot que 5, vu la taille
  du marche.
- **Maille geographique large** : archipel ou grande zone urbaine, jamais la
  commune isolee sur des categories peu fournies.
- **Maille temporelle large** : trimestre plutot que semaine.
- **Ecretage des valeurs extremes** : une valeur atypique est un identifiant.
- **Pas de croisement fin** : categorie × commune × mois × tranche de prix
  reidentifie mecaniquement.
- **Ne jamais conserver la donnee brute** au-dela du calcul, et surtout pas
  l'identite du vendeur, meme « en interne, au cas ou ».
- **Documenter la methode d'anonymisation** : la charge de la preuve pese sur
  le responsable de traitement.

Attention : **le stock intermediaire est un traitement de donnees
personnelles.** Meme si seule la statistique finale est publiee, collecter puis
stocker les annonces nominatives pour la calculer reste soumis a la loi 78-17.

### 7.3 Volet propriete intellectuelle — le point dur

L'article L342-1 vise l'extraction « par transfert **permanent ou temporaire** »
sur un autre support. **Calculer une statistique suppose d'extraire.** Et
l'article L342-2 vise explicitement la collecte **repetee et systematique** —
c'est-a-dire exactement ce que suppose une serie statistique dans le temps.

Deux elements jouent toutefois en faveur du projet :

1. **Une statistique n'est pas une partie substantielle du contenu.** Ce qui est
   protege, c'est la base, pas l'information. Un indice de prix agrege est une
   **donnee nouvelle**, produite par un travail d'analyse propre. Sa
   **publication** est difficilement qualifiable de « reutilisation d'une partie
   substantielle du contenu de la base ». Le produit fini est defendable.
2. **L'exception de fouille de textes et de donnees (TDM)** existe et couvre
   meme les usages commerciaux — mais elle est assortie d'un **droit
   d'opposition (opt-out)** du titulaire. Or Facebook s'oppose de toutes les
   manieres possibles : CGU explicites, `robots.txt`, mur de login, rate limit
   a zero. **L'exception TDM est donc tres probablement neutralisee ici.**
   Son existence et son regime en droit polynesien restent par ailleurs a
   verifier.

**Bilan du volet PI :** publier des statistiques est defendable ; les obtenir
par extraction automatisee de Facebook ne l'est pas. C'est le maillon faible,
et il ne disparait pas avec l'agregation.

### 7.4 Revente des statistiques

Si les donnees sont **reellement** anonymes et **licitement** obtenues, rien
n'interdit de les revendre. Mais la revente **aggrave** l'exposition sur les
deux volets :

- Elle etablit un **usage commercial direct**, ce qui alourdit l'evaluation du
  prejudice sur le terrain du parasitisme.
- Elle cree une **tracabilite** : un client institutionnel demandera l'origine
  des donnees et une garantie de conformite. Difficile a fournir si la source
  est une extraction non autorisee.
- Elle expose a une **action en garantie** de l'acheteur si la source est
  contestee.

> **Verdict : le produit statistique est commercialement pertinent et
> juridiquement defendable — a condition de changer de source.**

### 7.5 Sources de statistiques reellement exploitables

Par ordre de solidite decroissante :

1. **Tes propres annonces.** Des que le site a du volume, tu produis ta propre
   serie de prix. C'est la source la plus solide : tu en es proprietaire, tu
   peux la revendre sans reserve, et elle se valorise avec le temps.
2. **Sources publiques polynesiennes.** ISPF, indices de prix, donnees
   douanieres et administratives. Gratuites, citables, licites.
3. **Accords avec des acteurs locaux** (concessionnaires, agences immobilieres,
   assureurs) qui ont interet a un indice de reference partage.
4. **Observation manuelle a petite echelle**, documentee comme une etude de
   marche. Un releve humain periodique sur un echantillon reduit reste une
   pratique d'etude de marche classique — mais l'automatiser le fait basculer
   dans le § 7.3.
5. **Achat de donnees sous licence** aupres d'un fournisseur qui garantit
   contractuellement l'origine — ce qu'Apify, precisement, ne fait pas (§ 4).

---

## 8. Ce que ca implique pour le projet

L'analyse technique (`RESULTATS_PROBE.md`) avait deja montre que la voie
GraphQL ne tenait pas : rate limit anonyme a zero, mur de login sur la
recherche. L'analyse juridique conduit a la meme conclusion par un autre
chemin, et **elle disqualifie aussi le plan de repli** — Apify et RapidAPI ne
resolvent que le probleme technique, pas le probleme juridique (§ 4).

**Recommandation : abandonner l'agregation d'annonces Facebook comme fondement
du produit.** Ce n'est pas un obstacle contournable par un meilleur design
technique ; c'est un defaut de conception du modele.

Trois pivots, par ordre de solidite :

**A. Marketplace autonome** — le modele « leboncoin tahitien » authentique. Les
vendeurs deposent chez toi. Tu deviens producteur de ta propre base, protegeable
a ton tour. L'amorcage est plus lent (probleme classique de l'oeuf et de la
poule sur un marche biface), mais c'est le seul modele sans dette juridique.
Toutes les fonctionnalites prevues — filtres combines, alertes push, favoris,
carte, mode hors-ligne, comparaison — gardent leur valeur : c'est precisement
la ou l'interface de Facebook est faible.

**B. Agregation multi-sources sous licence** — Leboncoin, Vinted, eBay et
acteurs locaux exposent des programmes d'affiliation ou des API officielles.
Moins de donnees, mais un droit d'usage ecrit.

**C. Produit statistique** — l'observatoire des prix de l'occasion en Polynesie,
construit sur tes propres donnees (A) plus les sources publiques. C'est un
produit revendable, et il n'existe probablement pas aujourd'hui sur ce
territoire.

Ces trois pivots se cumulent : **A** alimente **C**, et **B** accelere
l'amorcage de **A**.

---

## 9. Questions a poser a un avocat

A soumettre a un avocat inscrit au barreau de Papeete, competent en droit du
numerique. La question 1 est prioritaire : elle conditionne tout le reste.

1. **Le code de la propriete intellectuelle de la Polynesie francaise
   comporte-t-il un droit sui generis du producteur de bases de donnees ?**
   Si oui, quel est son regime et sa duree ? Si non, quel fondement de
   substitution (parasitisme, concurrence deloyale) et avec quelle
   jurisprudence locale ?
2. Une societe etablie en Polynesie francaise, editant un site accessible depuis
   l'UE, peut-elle etre attraite devant une juridiction francaise ou irlandaise
   par Meta Platforms Ireland ? Quelle est la portee de la clause attributive
   de juridiction des CGU Meta ?
3. L'exception de fouille de textes et de donnees existe-t-elle en droit
   polynesien, et dans quelles conditions ?
4. Quelles obligations pesent sur un site de petites annonces en Polynesie au
   titre du droit de la consommation local et du statut d'operateur de
   plateforme ?
5. Sur le volet statistique : quel seuil d'agregation retenir compte tenu de la
   taille du marche polynesien, et quelle documentation constituer pour etablir
   le caractere anonyme des donnees publiees ?
6. Le franchissement d'un mur de login ou d'un rate limit est-il susceptible de
   qualification penale en droit polynesien (acces frauduleux a un systeme de
   traitement automatise de donnees — l'Etat restant competent en matiere
   penale) ?

---

## Sources

**Protection des donnees**
- [CNIL — Loi Informatique et Libertes et RGPD : ce qui change pour l'outre-mer](https://www.cnil.fr/fr/loi-informatique-et-libertes-et-rgpd-ce-qui-change-pour-loutre-mer)
- [CNIL — L'anonymisation de donnees personnelles](https://www.cnil.fr/fr/technologies/lanonymisation-de-donnees-personnelles)
- [CNIL — Avis du G29 sur les techniques d'anonymisation](https://www.cnil.fr/fr/le-g29-publie-un-avis-sur-les-techniques-danonymisation)
- [CNIL — Interet legitime : collecte de donnees par moissonnage (web scraping)](https://www.cnil.fr/fr/focus-interet-legitime-collecte-par-moissonnage)
- [DSI Polynesie francaise — Protection des donnees (RGPD)](https://www.service-public.pf/dsi/protection-des-donnees-rgpd/)

**Droit sui generis et web scraping**
- [CMS — Arret LeBonCoin : web scraping et droit sui generis](https://cms.law/fr/fra/news-information/arret-leboncoin-web-scraping-droit-sui-generis-sur-les-bases-de-donnees)
- [August Debouzy — Protection du site leboncoin.fr contre le web scraping](https://www.august-debouzy.com/fr/blog/1638-protection-du-site-leboncoinfr-contre-le-web-scraping-de-ses-donnees)
- [Kohen Avocats — La protection sui generis a l'epreuve du web scraping, 2022-2026](https://kohenavocats.fr/2026/05/30/protection-sui-generis-bases-donnees-scraping-jurisprudence-2022-2026/)
- [Legifrance — CPI, Titre IV : Droits des producteurs de bases de donnees (L341-1 a L343-7)](https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006069414/LEGISCTA000006146357/)
- [Legifrance — Article L342-1 CPI](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006279247)
- [Legifrance — Article L342-3 CPI (exception de fouille de textes et de donnees)](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000044365654)

**Competences en Polynesie francaise**
- [Conseil constitutionnel — Decision n° 2014-6 LOM du 7 novembre 2014](https://www.conseil-constitutionnel.fr/decision/2014/20146LOM.htm)
- [Legifrance — Loi organique n° 2004-192 du 27 fevrier 2004, statut d'autonomie](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006399376/2026-04-21)
- [Lexpol — Code de la propriete intellectuelle de la Polynesie francaise](https://lexpol.cloud.pf/LexpolAfficheCodes.php?code=74) *(inaccessible — HTTP 503 — lors de la redaction)*
- [DGAE Polynesie francaise — Propriete industrielle](https://www.service-public.pf/dgae/propriete-industrielle/presentation-de-la-propriete-industrielle/)

**Meta et prestataires**
- [Quinn Emanuel — Meta v. Bright Data: Significant Decision For Web Scraping](https://www.quinnemanuel.com/the-firm/news-events/client-alert-meta-v-bright-data-significant-decision-for-web-scraping-industry/)
- [Farella Braun + Martel — Major Decision Affects Law of Scraping, Meta Platforms v. Bright Data](https://www.fbm.com/publications/major-decision-affects-law-of-scraping-and-online-data-collection-meta-platforms-v-bright-data/)
- [Apify — General Terms and Conditions](https://docs.apify.com/legal/general-terms-and-conditions)
