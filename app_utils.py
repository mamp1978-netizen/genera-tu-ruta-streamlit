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
# --- Función vacía temporal para evitar error de importación ---
def suggest_addresses(query: str, max_results: int = 5):
    """Versión temporal vacía de suggest_addresses (devuelve lista vacía)."""
    return []
# --- Fin del parche temporal ---
# --- Función vacía temporal para evitar error de importación ---
def resolve_selection(selection):
    """Versión temporal vacía de resolve_selection (retorna None)."""
    return None
# --- Fin del parche temporal ---
# --- Función vacía temporal para evitar error de importación ---
def build_gmaps_url(origin=None, destination=None, waypoints=None):
    """Versión temporal vacía de build_gmaps_url (retorna cadena vacía)."""
    return ""
# --- Fin del parche temporal ---
