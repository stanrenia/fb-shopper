#!/usr/bin/env python3
"""
probe_marketplace.py — Diagnostic de l'acces aux donnees Facebook Marketplace.

Valide le postulat central de ANALYSE_STRATEGIE.md AVANT qu'on ecrive le backend :
« Facebook sert le Marketplace aux visiteurs deconnectes, et l'operation GraphQL
interne MarketplaceSearch repond sans authentification. »

Les 3 etapes :
  1. Joignabilite de https://www.facebook.com/   (sert aussi d'amorce de cookies)
  2. Le Marketplace est-il servi aux visiteurs deconnectes ?
       2a. GET /marketplace/          -> le feed d'accueil
       2b. GET /marketplace/search/   -> LA recherche, c'est ce qui nous interesse
  3. POST /api/graphql/               -> MarketplaceSearch repond-il sans auth ?

C'est un PROBE, pas un collecteur : 4 requetes vers facebook.com au total,
espacees de ~3s. L'etape 2 en compte deux parce que le feed d'accueil et la
recherche ne donnent PAS la meme reponse — voir RESULTATS.md.

Le doc_id d'une operation GraphQL Facebook tourne a chaque deploiement. Le mode
`--discover` le releve automatiquement dans les bundles JS publics du CDN
(c'est l'equivalent scriptable de l'onglet Reseau du navigateur).

Usage :
    python3 scripts/probe_marketplace.py
    python3 scripts/probe_marketplace.py --query "velo" --lat 48.85 --lon 2.35
    python3 scripts/probe_marketplace.py --discover -v
    python3 scripts/probe_marketplace.py --doc-id 27517490627932547
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, field
from typing import Any

try:
    import requests
except ImportError:  # pragma: no cover
    sys.exit("Dependance manquante : pip install requests")


# --------------------------------------------------------------------------
# Constantes
# --------------------------------------------------------------------------

BASE_URL = "https://www.facebook.com/"
MARKETPLACE_URL = "https://www.facebook.com/marketplace/"
MARKETPLACE_SEARCH_URL = "https://www.facebook.com/marketplace/search/?query={query}"
GRAPHQL_URL = "https://www.facebook.com/api/graphql/"

# doc_id de l'operation de recherche, releve le 2026-08-22 dans les bundles JS
# publics (voir --discover). Il TOURNE a chaque deploiement Facebook : ne jamais
# le considerer comme stable, le rendre configurable cote backend.
DOC_ID_SEARCH = "27517490627932547"   # CometMarketplaceSearchContentContainerQuery
DOC_ID_SEARCH_ROOT = "27840804775528031"  # CometMarketplaceSearchRootQuery

# doc_id historiques, releves sur des projets open-source de ~2023.
# Verifies morts le 2026-08-22 : « The GraphQL document with ID ... was not found. »
DOC_ID_LEGACY_2023 = {
    "7111969432204814": "recherche (kyleronayne / jongan69, ~2023) — MORT",
    "5585904654783609": "locations (~2023) — MORT",
}

# Composant Comet qui embarque la requete de recherche. Sert de point d'entree
# a --discover : page -> rsrcMap -> bundles -> _facebookRelayOperation.
SEARCH_COMPONENTS = (
    "CometMarketplaceSearchContentContainer.react",
    "CometMarketplaceSearchRoot.react",
)
RELAY_OP_RE = re.compile(
    r'__d\("([A-Za-z0-9_]*Marketplace[A-Za-z0-9_]*Search[A-Za-z0-9_]*)'
    r'_facebookRelayOperation",\[\],\(function\([^)]*\)\{(\w+)\.exports="(\d+)"'
)
PREFERRED_OP = "CometMarketplaceSearchContentContainerQuery"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

# Papeete, Tahiti — defaut du projet
DEFAULT_LAT = -17.53
DEFAULT_LON = -149.57
DEFAULT_RADIUS_KM = 60
DEFAULT_QUERY = "velo"

REQUEST_DELAY_S = 3.0
TIMEOUT_S = 30

JSON_PREFIXES = ("for (;;);", "for(;;);", ")]}'")

# Signaux textuels
LOGIN_WALL_MARKERS = (
    "login_form", "loginform",
    "you must log in to continue", "vous devez vous connecter",
    "log in to facebook", "connexion a facebook",
)
MARKETPLACE_MARKERS = ("marketplace_listing_title", "CometMarketplace", "marketplace")

# Messages FB quand le doc_id n'existe plus. Le premier motif est celui
# reellement renvoye en 2026 — les autres sont des variantes historiques.
STALE_DOC_ID_RE = re.compile(
    r"graphql document with id \d+ was not found"
    r"|persisted ?query ?not ?found"
    r"|unknown doc_id|doc_id not found|invalid doc_id|query not found",
    re.I,
)
RATE_LIMIT_RE = re.compile(r"rate limit exceeded|\b1675004\b", re.I)
AUTH_REQUIRED_RE = re.compile(
    r"login required|must be logged ?in|not logged ?in|session has expired"
    r"|requires_reauth\":true|fb_dtsg",
    re.I,
)


# --------------------------------------------------------------------------
# Sortie
# --------------------------------------------------------------------------

class C:
    _tty = sys.stdout.isatty()
    RESET = "\033[0m" if _tty else ""
    BOLD = "\033[1m" if _tty else ""
    DIM = "\033[2m" if _tty else ""
    RED = "\033[31m" if _tty else ""
    GREEN = "\033[32m" if _tty else ""
    YELLOW = "\033[33m" if _tty else ""
    BLUE = "\033[34m" if _tty else ""


def header(text: str) -> None:
    print(f"\n{C.BOLD}{C.BLUE}{'=' * 74}{C.RESET}")
    print(f"{C.BOLD}{C.BLUE}{text}{C.RESET}")
    print(f"{C.BOLD}{C.BLUE}{'=' * 74}{C.RESET}")


def ok(t: str) -> None:
    print(f"  {C.GREEN}[OK]{C.RESET}   {t}")


def warn(t: str) -> None:
    print(f"  {C.YELLOW}[WARN]{C.RESET} {t}")


def fail(t: str) -> None:
    print(f"  {C.RED}[FAIL]{C.RESET} {t}")


def info(t: str) -> None:
    print(f"  {C.DIM}·{C.RESET}      {t}")


# --------------------------------------------------------------------------
# Resultats
# --------------------------------------------------------------------------

@dataclass
class StepResult:
    name: str
    status: str          # "ok" | "warn" | "fail"
    summary: str
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status == "ok"


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def build_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": USER_AGENT,
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Upgrade-Insecure-Requests": "1",
        "sec-ch-ua": '"Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
    })
    return s


def strip_fb_json_prefix(text: str) -> str:
    stripped = text.lstrip()
    for prefix in JSON_PREFIXES:
        if stripped.startswith(prefix):
            return stripped[len(prefix):]
    return stripped


def parse_fb_json(text: str) -> Any | None:
    """Facebook peut concatener plusieurs objets JSON (reponse streamee).
    On ne garde que le premier, suffisant pour un probe."""
    payload = strip_fb_json_prefix(text)
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        pass
    try:
        obj, _ = json.JSONDecoder().raw_decode(payload)
        return obj
    except (json.JSONDecodeError, ValueError):
        return None


def extract_page_tokens(page: str) -> dict[str, str]:
    """Jetons anonymes que le navigateur renvoie sur chaque appel GraphQL.

    `lsd` est le jeton de session anonyme ; `fb_dtsg` n'existe QUE connecte,
    son absence est normale ici."""
    def g(pat: str, default: str = "") -> str:
        m = re.search(pat, page)
        return m.group(1) if m else default

    return {
        "lsd": g(r'"LSD",\[\],\{"token":"(.*?)"'),
        "rev": g(r'"__spin_r":(\d+)'),
        "spin_b": g(r'"__spin_b":"(.*?)"', "trunk"),
        "spin_t": g(r'"__spin_t":(\d+)'),
        "hsi": g(r'"hsi":"(.*?)"'),
        "hs": g(r'"haste_session":"(.*?)"'),
    }


def extract_ssr_listings(page: str, limit: int = 5) -> list[dict[str, str | None]]:
    """Annonces que Facebook injecte deja dans le HTML rendu cote serveur.

    Attention, le HTML et l'API GraphQL ne portent pas le prix au meme endroit :
    le SSR expose `formatted_price.text` (place AVANT le titre dans l'objet),
    l'API expose `listing_price.formatted_amount`.
    """
    def unescape(raw: str) -> str:
        try:
            return json.loads(f'"{raw}"')
        except json.JSONDecodeError:
            return raw

    price_re = re.compile(r'"formatted_price":\{"text":"(.*?)(?<!\\)"')
    out: list[dict[str, str | None]] = []
    for m in re.finditer(r'"marketplace_listing_title":"(.*?)(?<!\\)"', page):
        before = page[max(0, m.start() - 2000):m.start()]
        matches = price_re.findall(before) or price_re.findall(
            page[m.end():m.end() + 2000])
        out.append({
            "title": unescape(m.group(1)),
            "price": unescape(matches[-1]) if matches else None,
        })
        if len(out) >= limit:
            break
    return out


def build_variables(query: str, lat: float, lon: float, radius_km: int) -> dict:
    """Forme relevee dans le Relay artifact CometMarketplaceSearchContentContainerQuery."""
    return {
        "count": 24,
        "cursor": None,
        "params": {
            "bqf": {"callsite": "COMMERCE_MKTPLACE_WWW", "text": query},
            "browse_request_params": {
                "commerce_enable_local_pickup": True,
                "commerce_enable_shipping": True,
                "commerce_search_and_rp_available": True,
                "commerce_search_and_rp_category_id": [],
                "commerce_search_and_rp_condition": None,
                "commerce_search_and_rp_ctime_days": None,
                "filter_location_latitude": lat,
                "filter_location_longitude": lon,
                "filter_price_lower_bound": 0,
                "filter_price_upper_bound": 214748364700,
                "filter_radius_km": radius_km,
            },
            "custom_request_params": {
                "browse_context": None,
                "contextual_filters": [],
                "referral_code": None,
                "saved_search_strid": None,
                "search_vertical": "C2C",
                "seo_url": None,
                "surface": "SEARCH",
                "virtual_contextual_filters": [],
            },
        },
        "buyLocation": {"latitude": lat, "longitude": lon},
        "scale": 1,
        "shouldDeferNonCritical": False,
        "shouldIncludePopularSearches": False,
        "topicPageParams": None,
        "savedSearchID": None,
        "savedSearchQuery": None,
        "contextual_data": None,
    }


# --------------------------------------------------------------------------
# Decouverte automatique du doc_id
# --------------------------------------------------------------------------

def discover_doc_id(page: str, verbose: bool) -> dict[str, str]:
    """Releve les doc_id de recherche dans les bundles JS publics du CDN.

    Chemin : page HTML -> rsrcMap (hash -> URL de bundle)
             -> compMap (composant -> hashes)
             -> bundle -> __d("<Query>_facebookRelayOperation", ... exports="<doc_id>")

    Les bundles sont des assets statiques sur static.xx.fbcdn.net : les telecharger
    n'interroge pas l'API Marketplace et ne consomme pas de quota.
    """
    rsrc: dict[str, str] = {}
    for m in re.finditer(
        r'"([A-Za-z0-9_+/\\]{5,12})":\{"type":"js","src":"'
        r'(https:\\?/\\?/static\.xx\.fbcdn\.net[^"]+?)"', page
    ):
        rsrc[m.group(1).replace("\\/", "/")] = m.group(2).replace("\\/", "/")

    hashes: list[str] = []
    for comp in SEARCH_COMPONENTS:
        m = re.search(re.escape(f'"{comp}":{{"r":[') + r'(.*?)\]', page)
        if not m:
            continue
        for raw in m.group(1).split(","):
            h = raw.strip().strip('"').replace("\\/", "/")
            if h and h not in hashes:
                hashes.append(h)

    urls = [rsrc[h] for h in hashes if h in rsrc]
    if verbose:
        info(f"rsrcMap : {len(rsrc)} bundles ; composants de recherche : "
             f"{len(hashes)} hashes ; {len(urls)} resolus")

    found: dict[str, str] = {}
    for url in urls:
        try:
            body = requests.get(url, headers={"User-Agent": USER_AGENT},
                                timeout=TIMEOUT_S).text
        except requests.RequestException as e:
            if verbose:
                info(f"bundle injoignable ({type(e).__name__}) : {url[-40:]}")
            continue
        for m in RELAY_OP_RE.finditer(body):
            found[m.group(1)] = m.group(3)
        if verbose and found:
            info(f"bundle {url[-34:]} -> {len(found)} operation(s)")
    return found


# --------------------------------------------------------------------------
# Etape 1 — joignabilite
# --------------------------------------------------------------------------

def step1_reachability(session: requests.Session, verbose: bool) -> StepResult:
    header("ETAPE 1/3 — Joignabilite de facebook.com")
    info(f"GET {BASE_URL}")
    try:
        t0 = time.monotonic()
        r = session.get(BASE_URL, timeout=TIMEOUT_S, allow_redirects=True)
        elapsed = (time.monotonic() - t0) * 1000
    except requests.RequestException as e:
        fail(f"Requete impossible : {type(e).__name__}: {e}")
        info("Reseau bloque, DNS filtre ou proxy sortant absent.")
        return StepResult("joignabilite", "fail", f"{type(e).__name__}: {e}")

    info(f"HTTP {r.status_code} en {elapsed:.0f} ms — {len(r.content)} octets")
    if verbose:
        info(f"URL finale : {r.url}")
        info(f"Cookies amorces : {sorted(session.cookies.get_dict())}")

    if r.status_code >= 500:
        fail(f"Facebook renvoie {r.status_code} (erreur serveur).")
        return StepResult("joignabilite", "fail", f"HTTP {r.status_code}")
    if r.status_code >= 400:
        warn(f"HTTP {r.status_code} — joignable mais reponse anormale.")
        return StepResult("joignabilite", "warn", f"HTTP {r.status_code}")

    ok(f"facebook.com repond (HTTP {r.status_code}). Cookies d'amorce poses "
       f"({len(session.cookies)}).")
    return StepResult("joignabilite", "ok", f"HTTP {r.status_code}",
                      {"elapsed_ms": round(elapsed), "final_url": r.url})


# --------------------------------------------------------------------------
# Etape 2 — mur de login
# --------------------------------------------------------------------------

def _is_login_redirect(url: str) -> bool:
    return bool(re.search(r"/login/?(\?|$)|/checkpoint", url, re.I))


def step2_marketplace_public(session: requests.Session, query: str,
                             delay: float, verbose: bool) -> tuple[StepResult, str]:
    header("ETAPE 2/3 — Le Marketplace est-il servi aux visiteurs deconnectes ?")

    # --- 2a : le feed d'accueil ------------------------------------------
    info(f"[2a] GET {MARKETPLACE_URL}")
    try:
        r = session.get(MARKETPLACE_URL, timeout=TIMEOUT_S, allow_redirects=True)
    except requests.RequestException as e:
        fail(f"Requete impossible : {type(e).__name__}: {e}")
        return StepResult("marketplace_public", "fail", f"{type(e).__name__}: {e}"), ""

    feed_page = r.text
    info(f"     HTTP {r.status_code} — {len(feed_page)} octets — {r.url}")

    feed_walled = _is_login_redirect(r.url) or r.status_code >= 400
    ssr = [] if feed_walled else extract_ssr_listings(feed_page)

    if feed_walled:
        fail(f"     Feed d'accueil derriere un mur de login ({r.url}).")
    elif ssr:
        ok(f"     Feed d'accueil servi, avec {len(ssr)} annonce(s) deja "
           "presentes dans le HTML rendu cote serveur :")
        for l in ssr:
            print(f"           - {(l['title'] or '')[:52]:<52} {l['price'] or ''}")
        info("     Ces annonces sont geolocalisees sur l'IP sortante, pas sur "
             "--lat/--lon.")
    else:
        warn("     Feed servi mais aucune annonce dans le HTML.")

    # --- 2b : la recherche, c'est ce qui nous interesse -------------------
    time.sleep(delay)
    search_url = MARKETPLACE_SEARCH_URL.format(query=query)
    info(f"[2b] GET {search_url}")
    try:
        r2 = session.get(search_url, timeout=TIMEOUT_S, allow_redirects=True,
                         headers={"sec-fetch-site": "same-origin",
                                  "referer": MARKETPLACE_URL})
    except requests.RequestException as e:
        fail(f"Requete impossible : {type(e).__name__}: {e}")
        return StepResult("marketplace_public", "fail",
                          f"{type(e).__name__}: {e}"), feed_page

    search_walled = _is_login_redirect(r2.url) or r2.status_code >= 400
    search_listings = 0 if search_walled else len(extract_ssr_listings(r2.text, 50))
    info(f"     HTTP {r2.status_code} — {len(r2.text)} octets — {r2.url}")
    if verbose:
        for h in r2.history:
            info(f"       redirection {h.status_code} -> "
                 f"{h.headers.get('location', '?')}")

    details = {
        "feed_url": r.url, "feed_status": r.status_code,
        "feed_bytes": len(feed_page), "feed_walled": feed_walled,
        "feed_ssr_listings": len(ssr), "feed_ssr_sample": ssr,
        "search_url": r2.url, "search_status": r2.status_code,
        "search_walled": search_walled, "search_ssr_listings": search_listings,
    }

    if search_walled:
        fail(f"     RECHERCHE derriere un mur de login -> {r2.url}")
        if not feed_walled:
            info("     Asymetrie : le feed d'accueil passe, la recherche non.")
            return StepResult("marketplace_public", "warn",
                              "feed public, recherche derriere un mur de login",
                              details), feed_page
        return StepResult("marketplace_public", "fail",
                          "mur de login sur le Marketplace", details), feed_page

    if search_listings:
        ok(f"     Recherche servie sans authentification "
           f"({search_listings} annonce(s)).")
        return StepResult("marketplace_public", "ok",
                          "feed et recherche publics", details), feed_page

    warn("     Recherche servie mais sans annonce exploitable.")
    return StepResult("marketplace_public", "warn",
                      "recherche servie, 0 annonce", details), feed_page


# --------------------------------------------------------------------------
# Etape 3 — MarketplaceSearch via GraphQL interne
# --------------------------------------------------------------------------

def step3_graphql(session: requests.Session, doc_id: str, query: str,
                  lat: float, lon: float, radius_km: int,
                  tokens: dict[str, str], verbose: bool) -> StepResult:
    header("ETAPE 3/3 — MarketplaceSearch repond-il sans authentification ?")
    variables = build_variables(query, lat, lon, radius_km)
    info(f"POST {GRAPHQL_URL}")
    info(f"doc_id={doc_id}  query={query!r}  lat={lat} lon={lon} radius={radius_km}km")
    if doc_id in DOC_ID_LEGACY_2023:
        warn(f"doc_id historique : {DOC_ID_LEGACY_2023[doc_id]}")
    if tokens.get("lsd"):
        info(f"jeton anonyme lsd={tokens['lsd'][:12]}… (fb_dtsg absent : normal "
             "hors session connectee)")
    else:
        warn("jeton lsd introuvable dans la page — requete moins fidele au navigateur.")
    if verbose:
        info("variables = " + json.dumps(variables, ensure_ascii=False)[:600])

    payload = {
        "av": "0", "__aaid": "0", "__user": "0", "__a": "1", "__req": "a",
        "__hs": tokens.get("hs", ""), "dpr": "1", "__ccg": "EXCELLENT",
        "__rev": tokens.get("rev", ""), "__s": "::", "__hsi": tokens.get("hsi", ""),
        "__comet_req": "15", "lsd": tokens.get("lsd", ""),
        "__spin_r": tokens.get("rev", ""), "__spin_b": tokens.get("spin_b", "trunk"),
        "__spin_t": tokens.get("spin_t", ""),
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": PREFERRED_OP,
        "variables": json.dumps(variables, separators=(",", ":")),
        "server_timestamps": "true",
        "doc_id": doc_id,
    }
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "accept": "*/*",
        "origin": "https://www.facebook.com",
        "referer": MARKETPLACE_URL,
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-fb-friendly-name": PREFERRED_OP,
        "x-fb-lsd": tokens.get("lsd", ""),
        "x-asbd-id": "359341",
    }

    try:
        r = session.post(GRAPHQL_URL, data=payload, headers=headers, timeout=TIMEOUT_S)
    except requests.RequestException as e:
        fail(f"Requete impossible : {type(e).__name__}: {e}")
        return StepResult("graphql_search", "fail", f"{type(e).__name__}: {e}",
                          {"doc_id": doc_id})

    body = r.text
    info(f"HTTP {r.status_code} — {len(body)} octets — "
         f"content-type: {r.headers.get('content-type', '?')}")
    excerpt = body[:400].replace("\n", " ")
    if verbose:
        info(f"Extrait : {excerpt}")

    details: dict[str, Any] = {
        "doc_id": doc_id, "http_status": r.status_code, "bytes": len(body),
    }

    # Les erreurs les plus parlantes sont detectables sur le texte brut,
    # avant meme de parser : on les traite d'abord.
    if STALE_DOC_ID_RE.search(body):
        fail(f"doc_id PERIME — Facebook ne connait pas {doc_id}.")
        info(f"Extrait : {excerpt}")
        details["stale_doc_id"] = True
        return StepResult("graphql_search", "fail", f"doc_id {doc_id} perime", details)

    if RATE_LIMIT_RE.search(body):
        fail("RATE LIMIT — le doc_id est valide mais Facebook refuse de servir "
             "la requete a un client non authentifie depuis cette IP.")
        info(f"Extrait : {excerpt}")
        details["rate_limited"] = True
        return StepResult("graphql_search", "fail", "rate limit (doc_id valide)",
                          details)

    data = parse_fb_json(body)
    if data is None:
        if "<html" in body[:2000].lower():
            fail("Reponse HTML au lieu de JSON — requete rejetee avant GraphQL "
                 "(anti-bot, checkpoint ou endpoint deplace).")
            details["html_response"] = True
        else:
            fail("Reponse illisible (ni JSON ni HTML identifiable).")
        info(f"Extrait : {excerpt}")
        return StepResult("graphql_search", "fail", "reponse non-JSON", details)

    if not isinstance(data, dict):
        fail(f"JSON inattendu de type {type(data).__name__}.")
        return StepResult("graphql_search", "fail", "JSON inattendu", details)

    errors = data.get("errors") or []
    if not errors and data.get("errorSummary"):
        errors = [{"message": f"{data['errorSummary']} — "
                              f"{data.get('errorDescription', '')}"}]
    if errors:
        messages = [str(e.get("message") or e) if isinstance(e, dict) else str(e)
                    for e in (errors if isinstance(errors, list) else [errors])]
        joined = " | ".join(messages)
        details["graphql_errors"] = messages[:5]

        if AUTH_REQUIRED_RE.search(joined) or AUTH_REQUIRED_RE.search(body):
            fail(f"Authentification exigee — {joined[:280]}")
            details["auth_required"] = True
            return StepResult("graphql_search", "fail", "authentification exigee",
                              details)
        fail(f"GraphQL renvoie une erreur : {joined[:280]}")
        return StepResult("graphql_search", "fail", "erreur GraphQL", details)

    search = (data.get("data") or {}).get("marketplace_search")
    if search is None:
        keys = list((data.get("data") or {}).keys())
        fail(f"Pas de `data.marketplace_search` (cles : {keys or 'aucune'}).")
        details["data_keys"] = keys
        info(f"Extrait : {excerpt}")
        return StepResult("graphql_search", "fail", "marketplace_search absent",
                          details)

    edges = ((search.get("feed_units") or {}).get("edges")) or []
    listings = []
    for edge in edges:
        listing = ((edge or {}).get("node") or {}).get("listing") or {}
        title = listing.get("marketplace_listing_title")
        if title:
            listings.append({
                "title": title,
                "price": (listing.get("listing_price") or {}).get("formatted_amount"),
            })
    details.update({"edge_count": len(edges), "listing_count": len(listings),
                    "sample": listings[:5]})

    if not listings:
        warn(f"Reponse structuree recue mais 0 annonce ({len(edges)} edge(s)).")
        info("Soit la zone est vide, soit Facebook tronque la reponse hors session.")
        return StepResult("graphql_search", "warn", "0 annonce", details)

    ok(f"{len(listings)} annonce(s) recuperee(s) SANS authentification.")
    for l in listings[:5]:
        print(f"         - {l['title'][:56]:<56} {l['price'] or '?'}")
    return StepResult("graphql_search", "ok", f"{len(listings)} annonces", details)


# --------------------------------------------------------------------------
# Conclusion
# --------------------------------------------------------------------------

def _print_refresh_doc_id_howto() -> None:
    print("     1. Automatiquement : "
          f"{C.BOLD}probe_marketplace.py --discover{C.RESET}")
    print("     2. A la main, via l'onglet Reseau du navigateur :")
    print("        - ouvrir https://www.facebook.com/marketplace/ en navigation privee")
    print("        - DevTools > Reseau, filtrer sur `graphql`")
    print("        - lancer une recherche, reperer la requete dont")
    print("          `fb_api_req_friendly_name` vaut "
          "`CometMarketplaceSearchContentContainerQuery`")
    print("        - copier son `doc_id`, puis relancer avec --doc-id <id>")


def _print_fallbacks() -> None:
    print(f"  {C.BOLD}=> Basculer sur les fallbacks{C.RESET} "
          "(section 4.3 de ANALYSE_STRATEGIE.md) :")
    print("     1. Apify — Facebook Marketplace Scraper")
    print("     2. RapidAPI — Facebook Marketplace")
    print("     3. a defaut, pivot multi-sources (Leboncoin, Vinted, eBay)")
    print()
    print("  Ne pas automatiser un compte connecte : risque de bannissement,")
    print("  et donnees personnelles de tiers.")


def conclude(s1: StepResult, s2: StepResult, s3: StepResult, doc_id: str) -> int:
    header("CONCLUSION — quelle branche prendre")

    if s1.status == "fail":
        print(f"{C.RED}{C.BOLD}  facebook.com n'est pas joignable depuis cet "
              f"environnement.{C.RESET}")
        print("  Rien n'est conclu sur le postulat : relancer depuis un reseau "
              "non filtre.")
        return 2

    # --- mur de login complet a l'etape 2 --------------------------------
    if s2.status == "fail":
        print(f"{C.RED}{C.BOLD}  MUR DE LOGIN sur le Marketplace.{C.RESET}")
        print("  Le postulat central de ANALYSE_STRATEGIE.md ne tient plus :")
        print("  Facebook ne sert plus le Marketplace aux visiteurs deconnectes.")
        print()
        _print_fallbacks()
        return 3

    search_walled = bool(s2.details.get("search_walled"))
    ssr_count = s2.details.get("feed_ssr_listings", 0)

    # --- etape 3 en echec -------------------------------------------------
    if s3.status == "fail":
        if s3.details.get("stale_doc_id"):
            print(f"{C.YELLOW}{C.BOLD}  doc_id PERIME.{C.RESET}")
            print(f"  Facebook ne connait pas {doc_id}. Ces identifiants tournent")
            print("  a chaque deploiement : c'est attendu, ce n'est pas "
                  "l'architecture qui est en cause.")
            print()
            print(f"  {C.BOLD}=> Relever le doc_id a jour :{C.RESET}")
            _print_refresh_doc_id_howto()
            return 4

        if s3.details.get("rate_limited"):
            print(f"{C.RED}{C.BOLD}  RATE LIMIT ANONYME — le postulat ne tient "
                  f"qu'a moitie.{C.RESET}")
            print(f"  Le doc_id {doc_id} est VALIDE (pas d'erreur « not found »),")
            print("  mais Facebook refuse de servir MarketplaceSearch a un client")
            print("  non authentifie depuis cette IP — des la premiere requete.")
            print("  Ce n'est donc pas un quota qu'on epuise, c'est un quota nul.")
            if search_walled:
                print()
                print("  Coherent avec l'etape 2 : /marketplace/search/ redirige")
                print("  deja vers /login. La RECHERCHE est fermee aux deconnectes,")
                print("  meme si le feed d'accueil reste servi.")
            print()
            print(f"  {C.BOLD}=> La recherche GraphQL sans auth ne tient pas comme")
            print(f"     source primaire.{C.RESET}")
            _print_fallbacks()
            if ssr_count:
                print()
                print(f"  {C.BOLD}Piste secondaire relevee par l'etape 2 :{C.RESET} le HTML "
                      f"de /marketplace/")
                print(f"  embarque {ssr_count} annonce(s) rendues cote serveur, "
                      "sans authentification.")
                print("  C'est le feed d'accueil (geolocalise sur l'IP sortante), pas")
                print("  une recherche : utile pour du monitoring, insuffisant pour "
                      "le MVP.")
            return 5

        if s3.details.get("auth_required"):
            print(f"{C.RED}{C.BOLD}  MarketplaceSearch exige une "
                  f"authentification.{C.RESET}")
            print("  Il faudrait des cookies de session + un token fb_dtsg, donc")
            print("  automatiser un vrai compte. Hors perimetre (risque de ban).")
            print()
            _print_fallbacks()
            return 6

        print(f"{C.RED}{C.BOLD}  Etape 3 en erreur : {s3.summary}.{C.RESET}")
        print("  Cause non concluante (anti-bot, endpoint deplace, forme de requete).")
        print()
        print(f"  {C.BOLD}=> Rejouer la requete reelle du navigateur :{C.RESET}")
        _print_refresh_doc_id_howto()
        return 7

    if s3.status == "warn":
        print(f"{C.YELLOW}{C.BOLD}  Reponse GraphQL valide mais vide.{C.RESET}")
        print("  L'endpoint et le doc_id repondent, aucune annonce n'est renvoyee.")
        print("  Reessayer sur une zone dense (--lat 48.85 --lon 2.35) avec un")
        print("  terme large avant de conclure.")
        return 8

    # --- succes -----------------------------------------------------------
    print(f"{C.GREEN}{C.BOLD}  L'APPROCHE GRAPHQL TIENT — on continue.{C.RESET}")
    print(f"  Etape 3 : MarketplaceSearch (doc_id {doc_id}) repond sans auth, "
          f"{s3.details.get('listing_count', 0)} annonce(s).")
    if search_walled:
        print()
        print(f"  {C.YELLOW}Nuance :{C.RESET} /marketplace/search/ reste derriere un mur de")
        print("  login en navigation normale. L'API repond la ou la page ne repond pas ;")
        print("  ne pas compter sur cette asymetrie pour durer.")
    print()
    print("  => Phase 1 du MVP : scaffolding monorepo (apps/web + apps/api),")
    print("     endpoint de recherche, cache Redis, normalisation Zod.")
    print()
    print(f"  {C.BOLD}A cabler des le depart{C.RESET} : le doc_id est volatil. Le rendre")
    print("  configurable (variable d'environnement), et surveiller sa peremption")
    print("  avec ce probe en CI.")
    return 0


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Probe de l'acces aux donnees Facebook Marketplace.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"Defaut geographique : Papeete, Tahiti ({DEFAULT_LAT} / {DEFAULT_LON}).",
    )
    p.add_argument("--query", default=DEFAULT_QUERY, help="terme recherche")
    p.add_argument("--lat", type=float, default=DEFAULT_LAT, help="latitude")
    p.add_argument("--lon", type=float, default=DEFAULT_LON, help="longitude")
    p.add_argument("--radius", type=int, default=DEFAULT_RADIUS_KM,
                   help="rayon de recherche en km")
    p.add_argument("--doc-id", default=DOC_ID_SEARCH,
                   help=f"doc_id GraphQL a tester (defaut {DOC_ID_SEARCH})")
    p.add_argument("--discover", action="store_true",
                   help="relever le doc_id a jour dans les bundles JS du CDN "
                        "et l'utiliser pour l'etape 3")
    p.add_argument("--delay", type=float, default=REQUEST_DELAY_S,
                   help="secondes entre deux requetes")
    p.add_argument("--verbose", "-v", action="store_true", help="sortie detaillee")
    p.add_argument("--json", action="store_true",
                   help="ecrire un resume JSON sur stderr")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    print(f"{C.BOLD}probe_marketplace.py{C.RESET} — validation du postulat d'acces "
          "au Marketplace")
    print(f"{C.DIM}4 requetes vers facebook.com, espacees de {args.delay:.0f}s. "
          f"C'est un probe, pas un collecteur.{C.RESET}")

    session = build_session()
    doc_id = args.doc_id

    s1 = step1_reachability(session, args.verbose)
    if s1.status == "fail":
        s2 = StepResult("marketplace_public", "fail", "non teste (etape 1 en echec)")
        s3 = StepResult("graphql_search", "fail", "non teste (etape 1 en echec)")
    else:
        time.sleep(args.delay)
        s2, feed_page = step2_marketplace_public(session, args.query,
                                                 args.delay, args.verbose)
        tokens = extract_page_tokens(feed_page)

        if args.discover and feed_page:
            header("DECOUVERTE — relever le doc_id courant dans les bundles JS")
            ops = discover_doc_id(feed_page, args.verbose)
            if ops:
                for name, oid in sorted(ops.items()):
                    mark = "  <-- retenu" if name == PREFERRED_OP else ""
                    print(f"  {oid:>20}  {name}{mark}")
                if PREFERRED_OP in ops:
                    doc_id = ops[PREFERRED_OP]
                    ok(f"doc_id retenu : {doc_id}")
                    if doc_id != args.doc_id:
                        warn(f"different du defaut du script ({args.doc_id}) — "
                             "penser a mettre a jour DOC_ID_SEARCH.")
                else:
                    warn(f"{PREFERRED_OP} introuvable ; on garde {doc_id}.")
            else:
                warn("Aucun doc_id releve dans les bundles ; on garde le defaut.")

        if s2.status == "fail":
            info("")
            info("Etape 3 tentee malgre le mur de login : l'API repond parfois")
            info("la ou la page ne repond pas.")
        time.sleep(args.delay)
        s3 = step3_graphql(session, doc_id, args.query, args.lat, args.lon,
                           args.radius, tokens, args.verbose)

    header("RESUME")
    for step in (s1, s2, s3):
        mark = {"ok": f"{C.GREEN}OK  {C.RESET}",
                "warn": f"{C.YELLOW}WARN{C.RESET}",
                "fail": f"{C.RED}FAIL{C.RESET}"}[step.status]
        print(f"  [{mark}] {step.name:<20} {step.summary}")

    code = conclude(s1, s2, s3, doc_id)

    if args.json:
        print(json.dumps(
            {"exit_code": code, "doc_id": doc_id,
             "steps": [{"name": s.name, "status": s.status,
                        "summary": s.summary, "details": s.details}
                       for s in (s1, s2, s3)]},
            ensure_ascii=False, indent=2), file=sys.stderr)

    print()
    return code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrompu.", file=sys.stderr)
        sys.exit(130)
