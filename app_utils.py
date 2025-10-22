import os
import streamlit as st

# =========================================================
# 🔐 GESTIÓN SEGURA DE CLAVES API PARA GOOGLE Y SERPAPI
# =========================================================

def get_secret(*names: str) -> str | None:
    """
    Busca un secreto en st.secrets o variables de entorno.
    Devuelve el primero encontrado.
    """
    for n in names:
        v = (st.secrets.get(n) if hasattr(st, "secrets") else None) or os.getenv(n)
        if v:
            return v
    return None


def get_environment() -> str:
    """
    Determina si la app está en entorno de pruebas (STAGE) o producción (PRO).
    Por defecto usa PRO, salvo que detecte variables o dominios de prueba.
    """
    # Detectar dominio de pruebas (streamlit.app o test)
    stage_domains = ["genera-tu-ruta-app", "localhost", "127.0.0.1"]
    current_url = os.getenv("STREAMLIT_SERVER_URL", "")

    if any(dom in current_url for dom in stage_domains):
        return "STAGE"
    # También se puede forzar manualmente con variable de entorno:
    if os.getenv("APP_ENV", "").upper() == "STAGE":
        return "STAGE"
    return "PRO"


ENV = get_environment()

# =========================================================
# 🔑 CARGA DE CLAVES SEGÚN ENTORNO
# =========================================================

if ENV == "STAGE":
    GOOGLE_KEY = get_secret("GOOGLE_API_KEY_STAGE", "GOOGLE_API_KEY")
    SERPAPI_KEY = get_secret("SERPAPI_KEY_STAGE", "SERPAPI_KEY")
else:
    GOOGLE_KEY = get_secret("GOOGLE_API_KEY_PRO", "GOOGLE_API_KEY")
    SERPAPI_KEY = get_secret("SERPAPI_KEY_PRO", "SERPAPI_KEY")

# =========================================================
# 🧩 FUNCIONES DE DIAGNÓSTICO
# =========================================================

def show_diagnostics():
    """Muestra en la app las claves detectadas (solo durante pruebas)."""
    st.caption("🔎 Diagnóstico de configuración")
    st.write(f"**Entorno actual:** {ENV}")
    st.write(f"**Google API Key:** {'✅ Detectada' if GOOGLE_KEY else '❌ No encontrada'}")
    st.write(f"**SerpAPI Key:** {'✅ Detectada' if SERPAPI_KEY else '❌ No encontrada'}")


# =========================================================
# 🧭 FUNCIONES DE ACCESO A LAS APIS
# =========================================================

def init_google_client():
    """Inicializa cliente de Google Maps/Places con la clave actual."""
    import googlemaps
    if not GOOGLE_KEY:
        raise ValueError("No se encontró la clave de Google API")
    return googlemaps.Client(key=GOOGLE_KEY)


def search_serpapi(query: str):
    """Ejemplo de búsqueda con SerpAPI (básica)."""
    import requests
    if not SERPAPI_KEY:
        raise ValueError("No se encontró la clave de SerpAPI")
    url = "https://serpapi.com/search"
    params = {"q": query, "api_key": SERPAPI_KEY}
    response = requests.get(url, params=params)
    return response.json()
# ============================================================
# PARCHE SUAVE: proveer funciones que tab_profesional importa.
# Si ya existen, no las sobrescribimos.
# ============================================================
from urllib.parse import quote

# 1) Sugerencias de direcciones (mínimo viable: lista vacía)
if "suggest_addresses" not in globals():
    def suggest_addresses(query: str):
        """
        Devuelve una lista de sugerencias de direcciones.
        Implementación mínima para evitar ImportError.
        Si quieres usarlo de verdad, podemos conectarlo a Places API.
        """
        return []

# 2) Resolver selección (identidad por defecto)
if "resolve_selection" not in globals():
    def resolve_selection(selection):
        """
        Dado el valor seleccionado en el UI, devuelve el texto final.
        Implementación mínima: devuelve tal cual.
        """
        return selection

# 3) Construir URL de Google Maps (funciona con direcciones en texto)
if "build_gmaps_url" not in globals():
    def build_gmaps_url(points):
        """
        Construye una URL de Google Maps Directions a partir de una lista
        de direcciones (strings). Ej.: ["Barcelona", "Madrid"]
        """
        if not points:
            return None
        path = "/".join(quote(str(p)) for p in points if str(p).strip())
        return f"https://www.google.com/maps/dir/{path}"

# 4) Construir URL de Waze (fallback sencillo a Google Maps si no hay coords)
if "build_waze_url" not in globals():
    def build_waze_url(points):
        """
        Placeholder: si no trabajamos con coordenadas, devolvemos la URL de GMaps.
        Podemos implementar Waze con coords (lat,lng) cuando lo necesites.
        """
        return build_gmaps_url(points)
