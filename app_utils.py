# app_utils.py — utilidades de búsqueda y helpers
import os
import typing as t

import streamlit as st

# ---- Google Maps client ------------------------------------------------------
try:
    import googlemaps  # pip install googlemaps
except Exception:  # pragma: no cover
    googlemaps = None  # type: ignore

# Clave desde secrets o env
GOOGLE_PLACES_API_KEY = (
    st.secrets.get("GOOGLE_PLACES_API_KEY")
    or os.environ.get("GOOGLE_PLACES_API_KEY")
    or st.secrets.get("GOOGLE_API_KEY")             # por compatibilidad
    or os.environ.get("GOOGLE_API_KEY")
)

gmaps = None
if googlemaps and GOOGLE_PLACES_API_KEY:
    try:
        gmaps = googlemaps.Client(key=GOOGLE_PLACES_API_KEY)
    except Exception:
        gmaps = None


# ---- Helpers de sesgo de localización (stubs seguros) ------------------------
def set_location_bias(lat: float | None = None, lng: float | None = None, radius_m: int = 20000) -> dict:
    """
    Devuelve un dict con el string 'locationbias' como espera Places Autocomplete:
    'circle:{radius_m}@{lat},{lng}'. Si no hay lat/lng, devuelve {} (sin sesgo).
    """
    if lat is None or lng is None:
        return {}
    return {"locationbias": f"circle:{int(radius_m)}@{lat},{lng}"}


def _use_ip_bias(ip_address: str | None = None) -> bool:
    """Stub: por ahora no aplicamos sesgo por IP."""
    return False


# ---- Autocompletado con Google Places ----------------------------------------
def suggest_addresses(
    term: str,
    key_bucket: str = "prof_top",
    min_len: int = 3,
    bias: dict | None = None,
    max_results: int = 8,
) -> list[dict]:
    """
    Devuelve una lista de sugerencias: [{'description': str, 'place_id': str}, ...]
    Nunca devuelve None (si no hay resultados o error => lista vacía).
    """
    if not term or len(term.strip()) < min_len:
        return []

    if gmaps is None:
        # sin cliente configurado devolvemos vacío para no romper la UI
        return []

    params: dict[str, t.Any] = {"input": term, "types": "geocode"}
    # locationbias opcional
    if isinstance(bias, dict) and bias.get("locationbias"):
        params["locationbias"] = bias["locationbias"]

    try:
        resp = gmaps.places_autocomplete(**params) or []
        out: list[dict] = []
        for r in resp[:max_results]:
            out.append(
                {
                    "description": r.get("description", ""),
                    "place_id": r.get("place_id", ""),
                    # campos extra por si la UI los usa en el futuro
                    "structured_formatting": r.get("structured_formatting", {}),
                    "types": r.get("types", []),
                }
            )
        return out
    except Exception:
        # En caso de error de API, devolvemos lista vacía para evitar TypeError en la UI
        return []


# ---- Resolver selección (stub seguro) ----------------------------------------
def resolve_selection(term: str, place_id: str | None = None) -> dict:
    """
    Devuelve SIEMPRE un dict con al menos:
      {
        "address": str,            # nunca falta (si no hay datos -> term)
        "query": str,              # eco del término buscado
        "place_id": Optional[str],
        "lat": Optional[float],
        "lng": Optional[float],
    }
    """
    base = {"query": term, "place_id": place_id, "address": term, "lat": None, "lng": None}

    if gmaps is None or not place_id:
        return base

    try:
        detail = gmaps.place(place_id=place_id) or {}
        result = detail.get("result", {}) if isinstance(detail, dict) else {}
        addr = result.get("formatted_address") or result.get("name") or term

        lat = None
        lng = None
        geom = result.get("geometry") or {}
        loc = geom.get("location") if isinstance(geom, dict) else None
        if isinstance(loc, dict):
            lat = loc.get("lat")
            lng = loc.get("lng")

        base.update({"address": addr, "lat": lat, "lng": lng})
        return base
    except Exception:
        # A prueba de fallos: nunca rompemos la UI
        return base

# ---- Construcción de URLs (stubs por compatibilidad) -------------------------
from urllib.parse import quote_plus

from urllib.parse import quote_plus

def _addr_from_any(x):
    """
    x: str o dict ({address}|{formatted_address}|{lat,lng}|{latlng:{lat,lng}}|{geometry:{location:{lat,lng}}})
    -> devuelve una cadena utilizable (dirección o 'lat,lng'), o None
    """
    if x is None:
        return None
    if isinstance(x, str):
        x = x.strip()
        return x if x else None
    if isinstance(x, dict):
        addr = x.get("address") or x.get("formatted_address")
        if isinstance(addr, str) and addr.strip():
            return addr.strip()
        lat = x.get("lat"); lng = x.get("lng")
        if isinstance(lat, (int, float)) and isinstance(lng, (int, float)):
            return f"{lat},{lng}"
        latlng = (x.get("latlng") or x.get("location")
                  or x.get("geometry", {}).get("location"))
        if isinstance(latlng, dict):
            lat = latlng.get("lat"); lng = latlng.get("lng")
            if isinstance(lat, (int, float)) and isinstance(lng, (int, float)):
                return f"{lat},{lng}"
    return None


def build_waze_url(origin, destination, waypoints=None):
    """
    Waze no soporta múltiples paradas por URL. Solo destino (y arranca desde ubicación actual).
    - Si proporcionas lat,lng -> usa ?ll=LAT,LNG&navigate=yes
    - Si proporcionas address -> usa ?q=ADDRESS&navigate=yes
    """
    dest = _addr_from_any(destination)
    if not dest:
        return None

    # ¿es lat,lng?
    if "," in dest and all(part.replace(".", "", 1).replace("-", "", 1).isdigit() for part in dest.split(",", 1)):
        return f"https://waze.com/ul?ll={quote_plus(dest)}&navigate=yes"
    # por texto (address)
    return f"https://waze.com/ul?q={quote_plus(dest)}&navigate=yes"


def build_apple_maps_url(origin, destination):
    """
    Apple Maps en web soporta origen/destino, no multiples waypoints.
    Acepta str o dicts en origin/destination.
    """
    o = _addr_from_any(origin)
    d = _addr_from_any(destination)
    if not d:
        return None
    parts = ["https://maps.apple.com/?dirflg=d"]
    if o:
        # si son coords 'lat,lng', van tal cual. Si es address, va como texto.
        parts.append(f"saddr={quote_plus(o)}")
    parts.append(f"daddr={quote_plus(d)}")
    return "&".join(parts)

def build_gmaps_url(
    origin,
    destination,
    waypoints=None,
    mode="driving",
    avoid=None,
    optimize=False,
):
    """
    Construye una URL de Google Maps Directions:
    https://www.google.com/maps/dir/?api=1&origin=...&destination=...&travelmode=...
    - origin, destination: str o dict ({address} o {lat,lng} o {latlng:{lat,lng}})
    - waypoints: lista de str o dicts como arriba
    - mode: 'driving' | 'walking' | 'bicycling' | 'transit'
    - avoid: None o lista/str con: 'tolls','highways','ferries','indoor'
    - optimize: bool -> añade 'optimize:true' en waypoints
    """
    o = _addr_from_any(origin)
    d = _addr_from_any(destination)
    if not o or not d:
        # Devuelve None para que el caller pueda decidir qué hacer (evitamos TypeError)
        return None

    parts = [
        "https://www.google.com/maps/dir/?api=1",
        f"origin={quote_plus(o)}",
        f"destination={quote_plus(d)}",
    ]

    # travel mode
    mode = (mode or "driving").lower().strip()
    if mode not in {"driving", "walking", "bicycling", "transit"}:
        mode = "driving"
    parts.append(f"travelmode={quote_plus(mode)}")

    # avoid
    if avoid:
        if isinstance(avoid, str):
            avoid_vals = [a.strip().lower() for a in avoid.split(",") if a.strip()]
        else:
            avoid_vals = [str(a).strip().lower() for a in avoid if str(a).strip()]
        # filtra a los permitidos
        allowed = {"tolls", "highways", "ferries", "indoor"}
        avoid_vals = [a for a in avoid_vals if a in allowed]
        if avoid_vals:
            parts.append(f"avoid={quote_plus(','.join(avoid_vals))}")

    # waypoints
    wp = []
    if waypoints:
        if not isinstance(waypoints, (list, tuple)):
            waypoints = [waypoints]
        for w in waypoints:
            s = _addr_from_any(w)
            if s:
                wp.append(s)
    if wp:
        # 'optimize:true|addr1|addr2|...'
        if optimize:
            wp_str = "optimize:true|" + "|".join(quote_plus(x) for x in wp)
        else:
            wp_str = "|".join(quote_plus(x) for x in wp)
        parts.append(f"waypoints={wp_str}")

    return "&".join(parts)

def build_waze_url() -> str:
    """Stub: no se usaba en la rama estable; devolvemos string vacío."""
    return ""


def build_apple_maps_url() -> str:
    """Stub: no se usaba en la rama estable; devolvemos string vacío."""
    return ""
