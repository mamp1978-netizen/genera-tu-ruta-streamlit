import streamlit as st
from app_utils import (
    suggest_addresses,
    build_gmaps_url,
    build_waze_url,
    build_apple_maps_url,
)


def _k(tipo, nombre):
    """Genera claves únicas para los widgets de Streamlit."""
    return f"{tipo}_{nombre}"


def mostrar_tab_ruta(tipo="prof", label="Ruta profesional"):
    """Muestra la interfaz para generar rutas."""
    st.header(label)

    try:
        # Entradas
        origen = st.text_input("Origen", key=_k(tipo, "origen"))
        destino = st.text_input("Destino", key=_k(tipo, "destino"))
        paradas = st.text_area(
            "Paradas intermedias (una por línea)",
            key=_k(tipo, "paradas"),
            placeholder="Ejemplo:\nCalle Mayor 10, Madrid\nPlaza España, Zaragoza",
        )

        modo = st.selectbox(
            "Tipo de ruta",
            ["Más rápido", "Corta", "Económica"],
            key=_k(tipo, "modo"),
        )

        # Botón principal
        if st.button("🚀 Generar ruta", key=_k(tipo, "btn_generar")):
            if not origen or not destino:
                st.warning("Por favor, introduce al menos origen y destino.")
                return

            waypoints = [
                p.strip() for p in paradas.split("\n") if p.strip()
            ] if paradas else []

            # Crear URLs
            gmaps_url = build_gmaps_url(
                origin=origen,
                destination=destino,
                waypoints=waypoints,
            )
            waze_url = build_waze_url(origen, destino)
            apple_url = build_apple_maps_url(origen, destino)

            # Mostrar resultados
            st.subheader("📍 Resultados de la ruta")

            if gmaps_url:
                st.markdown(
                    f"[🌍 **Abrir en Google Maps**]({gmaps_url})",
                    unsafe_allow_html=True,
                )
                st.session_state[_k(tipo, "last_route_url")] = gmaps_url
            else:
                st.warning("No se pudo generar la ruta en Google Maps.")

            if waze_url:
                st.markdown(
                    f"[🚗 **Abrir en Waze**]({waze_url})",
                    unsafe_allow_html=True,
                )
            else:
                st.info("Waze no admite múltiples paradas; se usa solo origen/destino.")

            if apple_url:
                st.markdown(
                    f"[🍎 **Abrir en Apple Maps**]({apple_url})",
                    unsafe_allow_html=True,
                )

    except Exception as e:
        st.error(f"Ocurrió un error al generar la ruta: {e}")


def mostrar_profesional():
    """Muestra la pestaña principal para rutas profesionales."""
    mostrar_tab_ruta(tipo="prof", label="Ruta de trabajo")
