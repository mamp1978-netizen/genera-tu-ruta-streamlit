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
    Dado un 'place_id' opcional, intenta obtener detalles.
    Si no hay gmaps o place_id, devuelve {'query': term}.
    """
    if gmaps is None or not place_id:
        return {"query": term}

    try:
        detail = gmaps.place(place_id=place_id)
        result = (detail or {}).get("result", {})
        return {
            "query": term,
            "place_id": place_id,
            "geometry": result.get("geometry"),
            "formatted_address": result.get("formatted_address"),
        }
    except Exception:
        return {"query": term, "place_id": place_id}


# ---- Construcción de URLs (stubs por compatibilidad) -------------------------
def build_gmaps_url() -> str:
    """Stub: no se usaba en la rama estable; devolvemos string vacío."""
    return ""


def build_waze_url() -> str:
    """Stub: no se usaba en la rama estable; devolvemos string vacío."""
    return ""


def build_apple_maps_url() -> str:
    """Stub: no se usaba en la rama estable; devolvemos string vacío."""
    return ""
