import streamlit as st
from datetime import datetime

from app_utils import (
    suggest_addresses,
    build_gmaps_url,
    build_waze_url,
    build_apple_maps_url,
)

def mostrar_profesional():
    st.title("🗺️ Planificador de Rutas")
    st.write(
        "Crea rutas con paradas usando direcciones completas. "
        "La última parada puede ser el destino final."
    )

    tabs = st.tabs(["Profesional", "Viajero", "Turístico"])

    with tabs[0]:
        mostrar_tab_ruta(tipo="prof", label="Ruta de trabajo")

    with tabs[1]:
        mostrar_tab_ruta(tipo="viaj", label="Ruta de viaje")

    with tabs[2]:
        mostrar_tab_ruta(tipo="tur", label="Ruta turística")


def mostrar_tab_ruta(tipo="prof", label="Ruta personalizada"):
    st.subheader(label)

    # keys únicos por pestaña
    modo = st.selectbox(
        "Tipo de ruta",
        ["Más rápido", "Corta", "Económica"],
        key=f"{tipo}_modo",
    )
    evitar = st.selectbox(
        "Evitar",
        ["Ninguno", "Peajes", "Autopistas", "Ferries"],
        key=f"{tipo}_evitar",
    )
    st.markdown("---")

    # Lista de direcciones en estado
    direcciones = st.session_state.get(f"{tipo}_direcciones", [])

    nueva = st.text_input(
        "Escribe la dirección (mín. 3 letras) y pulsa ENTER",
        key=f"{tipo}_nueva",
    )

    # Al escribir, si tiene 3+ caracteres, guardamos provisionalmente
    if nueva and len(nueva) >= 3:
        if (not direcciones) or (direcciones and direcciones[-1] != nueva):
            # evitamos duplicados consecutivos
            direcciones.append(nueva)
            st.session_state[f"{tipo}_direcciones"] = direcciones

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🧭 Añadir", key=f"{tipo}_add"):
            # ya se añadió al escribir; aquí solo reafirmamos
            st.session_state[f"{tipo}_direcciones"] = direcciones
    with col2:
        if st.button("🧹 Limpiar", key=f"{tipo}_clear"):
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

    if st.button("🚀 Generar ruta", key=f"{tipo}_generar"):
        try:
            origen_meta = {"address": direcciones[0]}
            destino_meta = {"address": direcciones[-1]}
            waypoints_resolved = (
                [{"address": d} for d in direcciones[1:-1]]
                if len(direcciones) > 2
                else []
            )

            # Construir URLs (las funciones aceptan dicts con "address")
            gmaps_url = build_gmaps_url(
                origin=origen_meta,
                destination=destino_meta,
                waypoints=waypoints_resolved,
                mode="driving",
                avoid=None if evitar == "Ninguno" else evitar.lower(),
                optimize=True,
            )

            waze_url = build_waze_url(origen_meta, destino_meta)
            apple_url = build_apple_maps_url(origen_meta, destino_meta)

            if gmaps_url:
                st.link_button("🌍 Abrir en Google Maps", gmaps_url, key=f"{tipo}_gmaps_btn")
                st.session_state[f"{tipo}_last_route_url"] = gmaps_url
            else:
                st.warning("No se pudo generar la ruta en Google Maps.")

            if waze_url:
                st.link_button("🚗 Abrir en Waze", waze_url, key=f"{tipo}_waze_btn")
            else:
                st.info("Waze no admite múltiples paradas; se usa solo origen/destino.")

            if apple_url:
                st.link_button("🍎 Abrir en Apple Maps", apple_url, key=f"{tipo}_apple_btn")

            st.success("✅ Ruta generada correctamente.")

        except Exception as e:
            st.error(f"Ocurrió un error al generar la ruta: {e}")


def buscar_sugerencias(termino: str):
    """Autocompletado con Google Places / SerpAPI."""
    try:
        sugs = suggest_addresses(termino, key_bucket="prof_top", min_len=3)
        return [s.get("description") or s.get("address") or "" for s in sugs]
    except Exception:
        return []
