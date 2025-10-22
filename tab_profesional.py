import streamlit as st
from app_utils import (
    suggest_addresses,
    build_gmaps_url,
    build_waze_url,
    build_apple_maps_url,
)
from datetime import datetime

def mostrar_profesional():
    st.title("🗺️ Planificador de Rutas")
    st.write("Crea rutas con paradas usando direcciones completas. "
             "La última parada puede ser el destino final.")

    tabs = st.tabs(["Profesional", "Viajero", "Turístico"])

    with tabs[0]:
        mostrar_tab_ruta(tipo="prof", label="Ruta de trabajo")

    with tabs[1]:
        mostrar_tab_ruta(tipo="viaj", label="Ruta de viaje")

    with tabs[2]:
        mostrar_tab_ruta(tipo="tur", label="Ruta turística")


def mostrar_tab_ruta(tipo="prof", label="Ruta personalizada"):
    st.subheader(label)
    modo = st.selectbox("Tipo de ruta", ["Más rápido", "Corta", "Económica"])
    evitar = st.selectbox("Evitar", ["Ninguno", "Peajes", "Autopistas", "Ferries"])
    st.markdown("---")

    # Entrada de direcciones
    direcciones = st.session_state.get(f"{tipo}_direcciones", [])
    nueva = st.text_input("Escribe la dirección (mín. 3 letras) y pulsa ENTER")

    if nueva:
        if len(nueva) >= 3:
            direcciones.append(nueva)
            st.session_state[f"{tipo}_direcciones"] = direcciones
        else:
            st.warning("Introduce al menos 3 caracteres.")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🧭 Añadir"):
            st.session_state[f"{tipo}_direcciones"] = direcciones
    with col2:
        if st.button("🧹 Limpiar"):
            st.session_state[f"{tipo}_direcciones"] = []
            direcciones = []

    st.markdown("### Puntos de la ruta (orden de viaje)")
    if direcciones:
        for i, d in enumerate(direcciones):
            st.write(f"{i+1}. {d}")
    else:
        st.info("Agregue al menos dos puntos (origen y destino) para generar la ruta.")
        return

    if len(direcciones) < 2:
        return

    st.markdown("---")
    st.write("🔍 Generar ruta con Google Maps / Waze / Apple Maps")

    if st.button("🚀 Generar ruta"):
        try:
            origen_meta = {"address": direcciones[0]}
            destino_meta = {"address": direcciones[-1]}
            waypoints_resolved = [
                {"address": d} for d in direcciones[1:-1]
            ] if len(direcciones) > 2 else []

            # Construir URLs seguras
            gmaps_url = build_gmaps_url(
                origin=origen_meta,
                destination=destino_meta,
                waypoints=waypoints_resolved,
                mode="driving",
                avoid=None,
                optimize=True,
            )

            waze_url = build_waze_url(origen_meta, destino_meta)
            apple_url = build_apple_maps_url(origen_meta, destino_meta)

            # Mostrar enlaces si existen
            if gmaps_url:
                st.link_button("🌍 Abrir en Google Maps", gmaps_url)
            else:
                st.warning("No se pudo generar la ruta en Google Maps.")

            if waze_url:
                st.link_button("🚗 Abrir en Waze", waze_url)
            else:
                st.info("Waze no admite múltiples paradas; solo se muestra destino.")

            if apple_url:
                st.link_button("🍎 Abrir en Apple Maps", apple_url)

            # Guardar última ruta
            st.session_state[f"{tipo}_last_route_url"] = gmaps_url
            st.success("✅ Ruta generada correctamente.")

        except Exception as e:
            st.error(f"Ocurrió un error al generar la ruta: {e}")


# --- Función auxiliar para mostrar sugerencias en campo de texto ---
def buscar_sugerencias(termino):
    """
    Devuelve lista de direcciones sugeridas por la API de Google Places
    o SerpAPI. Se usa para autocompletado.
    """
    try:
        sugerencias = suggest_addresses(termino, key_bucket="prof_top", min_len=3)
        return [s["description"] for s in sugerencias]
    except Exception:
        return []
