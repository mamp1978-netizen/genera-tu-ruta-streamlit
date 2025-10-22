import streamlit as st
from app_utils import GOOGLE_KEY, SERPAPI_KEY, ENV, show_diagnostics, init_google_client, search_serpapi

# =========================================================
# 🧭 CONFIGURACIÓN DE LA PÁGINA
# =========================================================
st.set_page_config(
    page_title="Genera tu Ruta 🚗",
    layout="centered",
)

st.title("🗺️ Generador de Rutas Inteligente")
st.caption("Aplicación conectada a Google Maps y SerpAPI — versión segura por entorno.")

# =========================================================
# 🔍 DETECCIÓN DE CLAVES Y ENTORNO
# =========================================================
show_diagnostics()

if not GOOGLE_KEY:
    st.error("❌ No se encontró la clave de Google API. Revisa `.streamlit/secrets.toml`.")
    st.stop()

if not SERPAPI_KEY:
    st.warning("⚠️ No se encontró la clave de SerpAPI. Algunas funciones pueden no estar disponibles.")

# =========================================================
# 🚗 INTERFAZ PRINCIPAL
# =========================================================
st.divider()
st.subheader("Buscar direcciones o lugares")

# Campo de entrada para direcciones
direccion = st.text_input("Introduce una dirección o lugar:")

# Botón para buscar información
if st.button("Buscar información"):
    try:
        # Cliente de Google Maps
        gmaps = init_google_client()
        resultados = gmaps.places(direccion)

        st.success(f"Resultados para '{direccion}'")
        for lugar in resultados.get("results", []):
            st.write(f"📍 **{lugar.get('name', 'Sin nombre')}**")
            st.caption(lugar.get("formatted_address", ""))

        # Extra opcional: búsqueda con SerpAPI
        st.divider()
        st.caption("🧠 Búsqueda complementaria con SerpAPI:")
        serp = search_serpapi(direccion)
        st.json(serp)

    except Exception as e:
        st.error(f"Error durante la búsqueda: {e}")
