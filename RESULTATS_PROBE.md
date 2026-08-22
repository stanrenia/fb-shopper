# Resultats du probe — 2026-08-22

Execution reelle de `scripts/probe_marketplace.py` depuis un environnement avec
acces internet non filtre. La session d'analyse precedente n'avait jamais pu le
lancer (sandbox bloquant facebook.com), donc le postulat central de
`ANALYSE_STRATEGIE.md` n'avait jamais ete verifie.

**Verdict : le postulat ne tient qu'a moitie. La recherche GraphQL sans
authentification ne peut pas etre la source primaire du MVP.**

---

## 1. Ce qui a ete mesure

| Etape | Resultat | Detail |
|---|---|---|
| 1. Joignabilite `facebook.com` | **OK** | HTTP 200, ~760 ms. Pose 3 cookies (`datr`, `fr`, `sb`). |
| 2a. `GET /marketplace/` | **OK** | HTTP 200, ~765 Ko, avec de vraies annonces rendues cote serveur. |
| 2b. `GET /marketplace/search/?query=…` | **MUR DE LOGIN** | Redirection 302 vers `/login/?next=…`. |
| 3. `POST /api/graphql/` (MarketplaceSearch) | **RATE LIMIT** | `{"errors":[{"message":"Rate limit exceeded","code":1675004}]}` |

Code de sortie du probe : `5` (rate limit anonyme).

---

## 2. Les trois conclusions qui changent l'architecture

### 2.1 Les `doc_id` de 2023 sont morts — les nouveaux ont ete releves

Les identifiants repris des projets open-source de ~2023 sont bien perimes :

```
POST /api/graphql/  doc_id=7111969432204814
-> {"errors":[{"message":"The GraphQL document with ID 7111969432204814 was not found."}]}
```

Les `doc_id` **courants** ont ete releves automatiquement dans les bundles JS
publics du CDN (`probe_marketplace.py --discover`) :

| Operation | `doc_id` (2026-08-22) |
|---|---|
| `CometMarketplaceSearchContentContainerQuery` | `27517490627932547` |
| `CometMarketplaceSearchRootQuery` | `27840804775528031` |
| `CometMarketplaceSavedSearchDialogQuery` | `27652967024323416` |

Le chemin de decouverte, scripte dans `--discover`, est l'equivalent de
l'onglet Reseau du navigateur :

```
GET /marketplace/  ->  rsrcMap  (hash de bundle -> URL CDN)
                   ->  compMap  (CometMarketplaceSearchContentContainer.react -> hashes)
                   ->  bundle JS
                   ->  __d("<Query>_facebookRelayOperation",[],(function(…){a.exports="<doc_id>"}))
```

Ces identifiants tournent a chaque deploiement Facebook : **le backend doit les
lire depuis une variable d'environnement**, jamais les coder en dur, et le probe
doit tourner en CI pour detecter leur peremption.

### 2.2 La recherche est fermee aux visiteurs deconnectes

C'est le point qui invalide la section 2.3 de `ANALYSE_STRATEGIE.md`
(« Pas d'authentification requise »).

- `/marketplace/` (feed d'accueil) : **servi**, HTTP 200.
- `/marketplace/search/?query=…` : **redirige vers `/login/`**, y compris avec
  les cookies d'amorce d'une session anonyme legitime.

L'asymetrie est nette : Facebook laisse voir sa vitrine, pas son moteur de
recherche.

### 2.3 `MarketplaceSearch` est rate-limite a zero sans authentification

Avec un `doc_id` valide et une requete fidele au navigateur — jetons `lsd`,
`__spin_r`/`__spin_b`/`__spin_t`, `__hsi`, en-tetes `x-fb-lsd`, `x-asbd-id`,
`sec-fetch-site: same-origin` — la reponse est constante :

```json
{"errors":[{"message":"Rate limit exceeded","severity":"CRITICAL","code":1675004}]}
```

Deux controles ecartent l'hypothese du quota epuise ou du bannissement d'IP :

1. **Des la premiere requete** d'une session fraiche. Ce n'est pas un quota
   qu'on epuise, c'est un quota nul.
2. **L'endpoint nous repond toujours** : un `doc_id` bidon renvoie
   « document with ID … was not found », pas un rate limit. On n'est donc pas
   bloques en amont — la requete est bien evaluee, puis refusee.

`fb_dtsg` est absent, ce qui est normal hors session connectee. L'obtenir
supposerait d'automatiser un vrai compte : hors perimetre (risque de
bannissement, donnees personnelles de tiers).

---

## 3. Piste secondaire : les annonces rendues cote serveur

`/marketplace/` embarque une vingtaine d'annonces directement dans le HTML,
sans authentification :

```json
"listing_price":{"amount":"850.00"},
"formatted_price":{"text":"850 $US"},
"marketplace_listing_title":"1972 Honda cb100",
"location":{"reverse_geocode":{"city":"Fairfield","state":"CA"}}
```

Attention, le HTML et l'API ne portent pas le prix au meme endroit :

| Source | Chemin du titre | Chemin du prix |
|---|---|---|
| HTML SSR | `marketplace_listing_title` | `formatted_price.text` |
| API GraphQL | `…listing.marketplace_listing_title` | `…listing.listing_price.formatted_amount` |

Limites de cette piste : c'est le **feed d'accueil**, pas une recherche ; il est
geolocalise sur l'IP sortante (ici la baie de San Francisco, pas Papeete) et
n'accepte ni mot-cle, ni filtre, ni rayon. Utile pour du monitoring de
disponibilite, insuffisant pour le MVP.

---

## 4. Consequences sur la strategie

| Section de `ANALYSE_STRATEGIE.md` | Statut |
|---|---|
| 2.3 « Pas d'authentification requise » | **Faux.** Rate limit anonyme a zero. |
| 4.1 GraphQL interne comme source primaire | **A abandonner** comme source primaire. |
| 4.3 Fallbacks Apify / RapidAPI | **Promus source primaire.** |
| 7 « Rate-limiting / IP ban : probabilite moyenne » | **A relever a certaine** — c'est l'etat par defaut. |

Ordre de bataille propose :

1. **Apify — Facebook Marketplace Scraper** en source primaire (tarification a
   l'usage, a valider sur un volume reel avant de s'engager).
2. **RapidAPI — Facebook Marketplace** en second fournisseur, pour ne pas
   dependre d'un seul.
3. Garder la couche GraphQL derriere l'abstraction de source de donnees, avec
   son `doc_id` configurable : elle redeviendra exploitable depuis des IP
   residentielles, et le probe en CI dira quand.
4. Le pivot multi-sources (Leboncoin, Vinted, eBay) devient l'axe de
   differenciation credible plutot qu'un plan D.

L'architecture generale — PWA Next.js + backend proxy + cache Redis +
normalisation Zod — n'est pas remise en cause. C'est la couche fournisseur qui
change, et elle etait deja prevue derriere une abstraction.

---

## 5. Reproduire

```bash
python3 scripts/probe_marketplace.py                 # 4 requetes, espacees de 3s
python3 scripts/probe_marketplace.py --discover -v   # + releve des doc_id courants
python3 scripts/probe_marketplace.py --json 2>&1 >/dev/null | jq .
```

Codes de sortie : `0` l'approche tient · `2` reseau bloque · `3` mur de login
complet · `4` `doc_id` perime · `5` rate limit anonyme · `6` auth exigee ·
`7` erreur non concluante · `8` reponse vide.

Pages et Groupes Facebook restent hors perimetre : ils sont derriere un mur de
login qui exigerait les cookies d'un compte reel. Pour lire une Page publique,
la voie propre reste la Graph API officielle avec un App Access Token.
