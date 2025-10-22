# tab_profesional.py
import streamlit as st
from app_utils import (
    suggest_addresses,
    build_gmaps_url,
    build_waze_url,
    build_apple_maps_url,
)

def _k(tipo: str, name: str) -> str:
    """Genera claves únicas y estables por pestaña."""
    return f"tabprof::{tipo}::{name}"

def mostrar_profesional():
    st.title("🗺️ Planificador de Rutas")
    st.write(
        "Crea rutas con paradas usando direcciones completas. "
        "La última parada puede ser el destino final."
    )

    tab_prof, tab_viaj, tab_tur = st.tabs(["Profesional", "Viajero", "Turístico"])

    with tab_prof:
        mostrar_tab_ruta(tipo="prof", label="Ruta de trabajo")
    with tab_viaj:
        mostrar_tab_ruta(tipo="viaj", label="Ruta de viaje")
    with tab_tur:
        mostrar_tab_ruta(tipo="tur", label="Ruta turística")

def mostrar_tab_ruta(tipo: str, label: str):
    # Hago el label de cada control único por tab (añado el alias del tab)
    st.subheader(f"{label} — {tipo}")

    modo = st.selectbox(
        f"Tipo de ruta — {tipo}",
        ["Más rápido", "Corta", "Económica"],
        key=_k(tipo, "modo"),
    )

    evitar = st.selectbox(
        f"Evitar — {tipo}",
        ["Ninguno", "Peajes", "Autopistas", "Ferries"],
        key=_k(tipo, "evitar"),
    )

    st.markdown("---")

    # Estado: lista de direcciones por pestaña
    direcciones = st.session_state.get(_k(tipo, "direcciones"), [])

    nueva = st.text_input(
        f"Escribe la dirección (mín. 3 letras) y pulsa ENTER — {tipo}",
        key=_k(tipo, "nueva"),
    )

    if nueva and len(nueva) >= 3:
        if not direcciones or direcciones[-1] != nueva:
            direcciones.append(nueva)
            st.session_state[_k(tipo, "direcciones")] = direcciones

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🧭 Añadir", key=_k(tipo, "btn_add")):
            st.session_state[_k(tipo, "direcciones")] = direcciones
    with c2:
        if st.button("🧹 Limpiar", key=_k(tipo, "btn_clear")):
            st.session_state[_k(tipo, "direcciones")] = []
            direcciones = []

    st.markdown("### Puntos de la ruta (orden de viaje)")
    if direcciones:
        for i, d in enumerate(direcciones, start=1):
            st.write(f"{i}. {d}")
    else:
        st.info("Agregue al menos dos puntos (origen y destino) para generar la ruta.")
        return
    if len(direcciones) < 2:
        return

    st.markdown("---")
    st.write("🔍 Generar ruta con Google Maps / Waze / Apple Maps")

    if st.button("🚀 Generar ruta", key=_k(tipo, "btn_generar")):
        try:
            origen_meta = {"address": direcciones[0]}
            destino_meta = {"address": direcciones[-1]}
            waypoints_resolved = (
                [{"address": d} for d in direcciones[1:-1]] if len(direcciones) > 2 else []
            )

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
                st.link_button("🌍 Abrir en Google Maps", gmaps_url, key=_k(tipo, "btn_gmaps"))
                st.session_state[_k(tipo, "last_route_url")] = gmaps_url
            else:
                st.warning("No se pudo generar la ruta en Google Maps.")

            if waze_url:
                st.link_button("🚗 Abrir en Waze", waze_url, key=_k(tipo, "btn_waze"))
            else:
                st.info("Waze no admite múltiples paradas; se usa solo origen/destino.")

            if apple_url:
                st.link_button("🍎 Abrir en Apple Maps", apple_url, key=_k(tipo, "btn_apple"))

            st.success("✅ Ruta generada correctamente.")
        except Exception as e:
            st.error(f"Ocurrió un error al generar la ruta: {e}")
