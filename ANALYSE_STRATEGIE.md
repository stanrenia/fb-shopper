# Analyse Stratégique — PWA de Recherche Avancée sur Facebook Marketplace

> Date : 2026-02-11
> Projet : fb-shopper

---

## 1. Contexte et Objectif

Facebook Marketplace attire **plus de 1,1 milliard d'utilisateurs actifs mensuels** dans plus de 228 pays et représente environ **51 % de l'activité de social commerce mondial**. Pourtant, l'interface native de recherche reste limitée : filtres basiques, pas de sauvegarde de recherches complexes, pas d'alertes personnalisées, et navigation mobile perfectible.

**L'objectif** est de créer une **Progressive Web App (PWA)** offrant une expérience de recherche avancée par-dessus les données du Marketplace Facebook.

---

## 2. Analyse des Points d'Accès aux Données Facebook Marketplace

### 2.1 API Officielle Graph API (REST) — Commerce Platform

| Aspect | Détail |
|---|---|
| **URL de base** | `https://graph.facebook.com/v22.0/` |
| **Accès** | Nécessite un **Meta Partner Approval** (processus de revue de plusieurs semaines/mois) |
| **Catégories supportées** | Actuellement limitées à **Véhicules** et **Immobilier** |
| **Fonctionnalités** | Création, mise à jour, suppression d'annonces côté vendeur ; gestion des commandes (`GET /<page-id>/commerce_orders`) |
| **Limitation majeure** | **Aucun endpoint public pour la recherche/lecture d'annonces côté acheteur** |
| **Verdict** | Inadapté pour une PWA de recherche avancée — orienté vendeurs uniquement |

**Sources :**
- [Facebook Marketplace API — Guide complet 2026](https://api2cart.com/api-technology/facebook-marketplace-api/)
- [Meta Graph API Considerations](https://data365.co/blog/meta-graph-api)

### 2.2 Meta Content Library API — Accès Recherche

| Aspect | Détail |
|---|---|
| **Couverture** | Pages, posts, groupes, événements, profils, commentaires, **annonces Marketplace**, collectes de fonds |
| **Capacités** | Recherche sur 100+ champs, jusqu'à 100 000 résultats/requête, recherche async, recherche texte dans les images |
| **Quotas** | 500 000 enregistrements / 7 jours glissants / chercheur ; 60 recherches sync/min |
| **Accès** | Réservé aux **chercheurs académiques** via le Secure Data Access Center (CASD) |
| **Environnements** | Meta Secure Research Environment (gratuit) ou SOMAR VDE (371 $/mois à partir de 01/2026) |
| **Limitation majeure** | **Accès strictement réservé à la recherche académique** — non exploitable commercialement |
| **Verdict** | Non viable pour une application grand public |

**Sources :**
- [Meta Content Library and API — Transparency Center](https://transparency.meta.com/researchtools/meta-content-library/)
- [Mises à jour MCL 2025](https://transparency.meta.com/MCL-API-update-supporting-independent-research)

### 2.3 API GraphQL Interne de Facebook (non officielle)

| Aspect | Détail |
|---|---|
| **Endpoint** | `https://www.facebook.com/api/graphql/` |
| **Méthode** | POST avec `content-type: application/x-www-form-urlencoded` |
| **Opération clé** | `MarketplaceSearch` via `doc_id` spécifique |
| **Paramètres** | `listingQuery`, `locationLatitude`, `locationLongitude`, `filter_radius_km`, `price_range`, `count`, `cursor` |
| **Réponse** | `data.marketplace_search.feed_units.edges[]` avec pagination (`end_cursor`) |
| **Avantages** | Pas d'authentification requise, données riches (prix, images, descriptions, vendeur) |
| **Risques** | API **non documentée** et **non supportée** — peut changer sans préavis ; violation potentielle des CGU Meta ; rate-limiting agressif |
| **Verdict** | **Approche la plus prometteuse techniquement** mais avec des risques juridiques/stabilité significatifs |

**Sources :**
- [marketplace-api — GitHub (kyleronayne)](https://github.com/kyleronayne/marketplace-api)
- [Gist Wes Bos — Facebook Marketplace GraphQL](https://gist.github.com/wesbos/4d05bcc6aac16866259e818de1d1c4ad)
- [fb-marketplace-api — GitHub (jongan69)](https://github.com/jongan69/fb-marketplace-api)

### 2.4 Outils Tiers de Scraping

| Outil | Description | Coût |
|---|---|---|
| **Apify — Facebook Marketplace Scraper** | Actor Apify dédié, extraction complète des listings | Freemium / à l'usage |
| **Stevesie — No-Code Scraper** | Extraction via fichiers HAR, interface visuelle | Payant |
| **RapidAPI — Facebook Marketplace** | API wrapper REST hébergée | Pay-per-use |

**Sources :**
- [Apify Facebook Marketplace Scraper](https://apify.com/apify/facebook-marketplace-scraper)
- [Stevesie Facebook Marketplace Scraper](https://stevesie.com/apps/facebook-api/scrape/marketplace)
- [RapidAPI — Facebook Marketplace](https://rapidapi.com/moxall/api/facebook-marketplace)

### 2.5 Commerce Manager / Catalog API (Feed de Produits)

| Aspect | Détail |
|---|---|
| **Fonction** | Gestion des catalogues produit pour Facebook Shops, Marketplace (côté vendeur), Dynamic Ads |
| **Formats** | CSV, TSV, XML, JSON, API temps réel |
| **Intégrations** | Shopify, WooCommerce, Magento, BigCommerce |
| **Limitation** | **Orienté publication/gestion de catalogues vendeur** — pas de lecture des annonces d'autres vendeurs |
| **Verdict** | Utile si le projet évolue vers un outil vendeur, mais pas pour la recherche acheteur |

---

## 3. Matrice de Décision

| Critère | Graph API Officielle | Content Library | GraphQL Interne | Scraping Tiers |
|---|---|---|---|---|
| **Accès aux listings acheteur** | Non | Oui (limité) | Oui | Oui |
| **Facilité d'accès** | Difficile (partenaire) | Très difficile (académique) | Facile | Moyen |
| **Richesse des données** | Faible | Élevée | Élevée | Variable |
| **Stabilité** | Haute | Haute | **Basse** | Basse |
| **Conformité CGU** | Oui | Oui | **Risque** | **Risque** |
| **Coût** | Gratuit | Gratuit/371$/mois | Gratuit | Variable |
| **Temps réel** | N/A | Non | Quasi temps réel | Variable |
| **Scalabilité** | N/A | Limitée (quotas) | Limitée (rate limits) | Dépend du provider |

---

## 4. Stratégie Recommandée : Architecture Multi-Couches

### 4.1 Approche Retenue : Backend Proxy + GraphQL Interne + Cache Intelligent

```
┌─────────────────────────────────────────────────────┐
│                   PWA (Frontend)                     │
│  React/Next.js + Service Worker + IndexedDB          │
│  - Recherche avancée (filtres combinés)              │
│  - Alertes push (nouvelles annonces)                 │
│  - Mode hors-ligne (résultats cachés)                │
│  - Comparaison de prix                               │
│  - Favoris & historique                              │
└──────────────────────┬──────────────────────────────┘
                       │ HTTPS/REST
┌──────────────────────▼──────────────────────────────┐
│               Backend API (Node.js/Express)           │
│  - Rate limiting intelligent                         │
│  - Cache Redis/mémoire (TTL configurable)            │
│  - File d'attente de requêtes                        │
│  - Rotation d'agents utilisateurs                    │
│  - Normalisation des données                         │
│  - Système d'alertes (cron/webhook)                  │
└──────────────────────┬──────────────────────────────┘
                       │ POST /api/graphql/
┌──────────────────────▼──────────────────────────────┐
│          Facebook GraphQL Interne                     │
│  Endpoint: https://www.facebook.com/api/graphql/     │
│  Operation: MarketplaceSearch                        │
└─────────────────────────────────────────────────────┘
```

### 4.2 Justification de l'Architecture

1. **GraphQL interne comme source primaire** : c'est la seule voie offrant un accès en quasi-temps réel aux annonces Marketplace sans authentification et avec des données riches (prix, photos, localisation, vendeur).

2. **Backend proxy obligatoire** : pour protéger les mécanismes d'accès, gérer le rate-limiting, mettre en cache les résultats et normaliser les données avant de les servir à la PWA.

3. **Cache multicouche** :
   - **Redis** côté serveur (TTL 5-15 min pour les recherches, 1h pour les détails d'annonce)
   - **IndexedDB** côté client via la PWA pour le mode offline et les favoris

4. **PWA pour l'expérience utilisateur** : installation sans store, notifications push, mode hors-ligne, performances natives.

### 4.3 Stratégie de Résilience (Plan B)

En cas de blocage de l'accès GraphQL interne par Facebook :

| Priorité | Fallback | Délai de mise en œuvre |
|---|---|---|
| 1 | Intégration **Apify Marketplace Scraper** comme source alternative | < 1 jour |
| 2 | Intégration **RapidAPI Facebook Marketplace** | < 1 jour |
| 3 | Demande d'accès **Meta Partner** pour l'API officielle (véhicules/immobilier) | Semaines/Mois |
| 4 | Pivot vers un modèle d'**agrégation multi-sources** (Leboncoin, Vinted, eBay...) | 1-2 semaines |

---

## 5. Fonctionnalités de Recherche Avancée de la PWA

### 5.1 Fonctionnalités Core (MVP)

| Fonctionnalité | Description |
|---|---|
| **Recherche multi-critères** | Combinaison mots-clés + catégorie + prix min/max + rayon géographique + état (neuf/occasion) |
| **Géolocalisation dynamique** | Recherche autour de la position de l'utilisateur ou d'une adresse saisie |
| **Tri avancé** | Par prix, distance, date de publication, pertinence |
| **Sauvegarde de recherches** | Enregistrer des combinaisons de filtres nommées |
| **Favoris** | Marquer des annonces pour consultation ultérieure |
| **Mode hors-ligne** | Consultation des résultats et favoris sans connexion |

### 5.2 Fonctionnalités Avancées (v2)

| Fonctionnalité | Description |
|---|---|
| **Alertes push** | Notification quand une nouvelle annonce correspond à une recherche sauvegardée |
| **Historique de prix** | Suivi de l'évolution du prix d'une annonce dans le temps |
| **Comparaison** | Comparer côte à côte 2-4 annonces |
| **Score de bonne affaire** | Algorithme comparant le prix à la médiane du marché |
| **Recherche par image** | Upload d'une photo pour trouver des articles similaires |
| **Exclusion de vendeurs** | Blacklister certains vendeurs (spam, arnaques) |
| **Multi-localisation** | Rechercher simultanément dans plusieurs zones géographiques |

---

## 6. Stack Technique Recommandée

### Frontend (PWA)
| Technologie | Justification |
|---|---|
| **Next.js 15 (App Router)** | SSR/SSG, excellent support PWA, écosystème React |
| **TypeScript** | Typage fort, meilleure maintenabilité |
| **Tailwind CSS** | UI rapide et responsive |
| **next-pwa / Workbox** | Service Worker, cache offline, push notifications |
| **IndexedDB (Dexie.js)** | Stockage local structuré pour favoris et cache |
| **Leaflet / Mapbox** | Carte interactive pour la géolocalisation |

### Backend
| Technologie | Justification |
|---|---|
| **Node.js + Express/Fastify** | Léger, performant, même langage que le front |
| **Redis** | Cache haute performance pour les résultats de recherche |
| **Bull / BullMQ** | File d'attente pour les requêtes vers Facebook et les alertes |
| **node-cron** | Planification des recherches récurrentes (alertes) |
| **Zod** | Validation des données entrantes et sortantes |

### Infrastructure
| Technologie | Justification |
|---|---|
| **Vercel** (front) | Déploiement optimisé Next.js, CDN global |
| **Railway / Fly.io** (back) | Déploiement simple du backend Node.js |
| **Upstash Redis** | Redis serverless, tier gratuit généreux |
| **GitHub Actions** | CI/CD |

---

## 7. Risques et Mitigations

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| **Changement de l'API GraphQL interne** | Élevée | Élevé | Abstraction de la couche data source ; fallbacks multiples (Apify, RapidAPI) ; tests de monitoring automatisés |
| **Rate-limiting / IP ban** | Moyenne | Élevé | Cache agressif ; rotation user-agents ; espacement des requêtes (10-20s min) ; retry avec backoff exponentiel |
| **Violation des CGU Meta** | Moyenne | Élevé | Pas de stockage massif des données ; cache temporaire uniquement ; pas de redistribution des données brutes ; consultation du cadre juridique |
| **Changement de structure des données** | Moyenne | Moyen | Parsing résilient avec fallbacks ; schéma de validation souple (Zod) ; alertes de monitoring |
| **CORS / Blocage navigateur** | Faible | Moyen | Le backend proxy élimine ce problème |

---

## 8. Considérations Juridiques

### Points d'attention
1. **CGU Facebook** : L'utilisation de l'API GraphQL interne est techniquement une violation des conditions d'utilisation de Meta. Cependant, l'accès aux données publiques du Marketplace (sans authentification) est dans une zone grise juridique.

2. **RGPD / Données personnelles** : Les annonces Marketplace contiennent potentiellement des données personnelles (nom du vendeur, localisation). La PWA ne doit **jamais stocker durablement** ces données — cache temporaire uniquement.

3. **Directive européenne sur le scraping** : Le cadre juridique européen (Digital Services Act) impose des obligations de transparence mais n'interdit pas explicitement la consultation automatisée de données publiques.

### Recommandations
- Limiter le cache à des durées courtes (< 1h)
- Ne pas exposer les données personnelles des vendeurs au-delà de ce que Facebook affiche
- Implémenter un mécanisme de respect du `robots.txt`
- Prévoir un mécanisme de suppression des données sur demande
- Consulter un juriste spécialisé avant le lancement commercial

---

## 9. Roadmap Proposée

### Phase 1 — MVP (4-6 semaines)
- [ ] Setup projet Next.js + PWA + Backend Node.js
- [ ] Intégration GraphQL interne Facebook (recherche + détails)
- [ ] Interface de recherche avec filtres combinés
- [ ] Géolocalisation et recherche par rayon
- [ ] Cache Redis + mode hors-ligne
- [ ] Déploiement initial

### Phase 2 — Enrichissement (4-6 semaines)
- [ ] Sauvegarde de recherches et favoris
- [ ] Alertes push (nouvelles annonces)
- [ ] Historique de prix
- [ ] Comparaison d'annonces
- [ ] Score de bonne affaire

### Phase 3 — Robustesse & Scale (2-4 semaines)
- [ ] Intégration des fallbacks (Apify, RapidAPI)
- [ ] Monitoring et alertes de changement d'API
- [ ] Optimisation des performances
- [ ] Tests E2E

### Phase 4 — Extensions (optionnel)
- [ ] Multi-sources (Leboncoin, Vinted, eBay)
- [ ] Recherche par image
- [ ] Application mobile (Capacitor)

---

## 10. Conclusion

La création d'une PWA de recherche avancée sur Facebook Marketplace est **techniquement faisable** en s'appuyant sur l'API GraphQL interne de Facebook comme source de données primaire. Cette approche offre le meilleur compromis entre richesse des données, facilité d'implémentation et coût.

Les **principaux défis** sont :
1. La **stabilité** de l'API non officielle (atténuée par les fallbacks)
2. La **conformité juridique** (atténuée par un usage respectueux et un cache temporaire)
3. Le **rate-limiting** (atténué par un cache intelligent et un espacement des requêtes)

La stack **Next.js + Node.js + Redis** offre un excellent rapport productivité/performance pour ce type de projet.

---

*Document généré dans le cadre de l'analyse préliminaire du projet fb-shopper.*
