import os
import streamlit as st
import googlemaps

# Leer la clave API (segura desde secrets o variable de entorno)
API_KEY = (
    st.secrets.get("GOOGLE_PLACES_API_KEY")
    or os.environ.get("GOOGLE_PLACES_API_KEY")
)

gmaps = googlemaps.Client(key=API_KEY) if API_KEY else None


def suggest_addresses(query: str, key_bucket="default", min_len: int = 3):
    """Sugerencias de direcciones usando Google Places."""
    if not API_KEY or not gmaps:
        return []

    if not query or len(query) < min_len:
        return []

    try:
        results = gmaps.places_autocomplete(input_text=query)
        return [{"description": r["description"]} for r in results]
    except Exception as e:
        print(f"[suggest_addresses] Error: {e}")
        return []


def build_gmaps_url(origin=None, destination=None, waypoints=None,
                    mode="driving", avoid=None, optimize=True):
    """Construye una URL de Google Maps con múltiples paradas."""
    try:
        def addr(x):
            if not x:
                return ""
            if isinstance(x, dict):
                return x.get("address", "")
            return str(x)

        o = addr(origin)
        d = addr(destination)
        w = "|".join([addr(p) for p in waypoints]) if waypoints else ""

        url = "https://www.google.com/maps/dir/?api=1"
        if o:
            url += f"&origin={o}"
        if d:
            url += f"&destination={d}"
        if w:
            url += f"&waypoints={w}"
        if mode:
            url += f"&travelmode={mode}"
        if avoid:
            url += f"&avoid={avoid}"
        if optimize:
            url += "&optimizeWaypoints=true"

        return url
    except Exception as e:
        print(f"[build_gmaps_url] Error: {e}")
        return None


def build_waze_url(origin=None, destination=None):
    """Construye una URL para Waze con origen y destino."""
    try:
        def addr(x):
            if not x:
                return ""
            if isinstance(x, dict):
                return x.get("address", "")
            return str(x)

        o = addr(origin)
        d = addr(destination)
        if not d:
            return None

        # Solo origen/destino (Waze no admite paradas múltiples)
        if o:
            return f"https://waze.com/ul?from={o}&to={d}&navigate=yes"
        else:
            return f"https://waze.com/ul?to={d}&navigate=yes"
    except Exception as e:
        print(f"[build_waze_url] Error: {e}")
        return None


def build_apple_maps_url(origin=None, destination=None):
    """Construye una URL para Apple Maps."""
    try:
        def addr(x):
            if not x:
                return ""
            if isinstance(x, dict):
                return x.get("address", "")
            return str(x)

        o = addr(origin)
        d = addr(destination)

        base = "http://maps.apple.com/?"
        if o:
            base += f"saddr={o}&"
        if d:
            base += f"daddr={d}&"
        return base + "dirflg=d"
    except Exception as e:
        print(f"[build_apple_maps_url] Error: {e}")
        return None
