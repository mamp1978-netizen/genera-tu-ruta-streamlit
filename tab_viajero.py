# tab_viajero.py
import requests
import streamlit as st
from streamlit_searchbox import st_searchbox 
# --- EN tab_profesional.py, tab_viajero.py, y tab_turistico.py ---

from app_utils import (
    suggest_addresses,
    resolve_selection, 
    build_gmaps_url,
    make_qr, # <--- ¡Asegúrate de que ESTÉ aquí!
    set_location_bias,
    _get_key,
    _use_ip_bias 
)

# ... el resto del código ...
# ----------------------------
# Helpers
# ----------------------------
def _ip_guess_bias():
    """Intenta ubicar por IP y fija el sesgo de ubicación para autocompletar."""
    try:
        ip = requests.get("https://ipapi.co/json/", timeout=6).json()
        lat = ip.get("latitude")
        lng = ip.get("longitude")
        if lat and lng:
            # 50 km por defecto. Puedes subir/bajar este radio.
            set_location_bias(float(lat), float(lng), radius_m=50000)
            return True
    except Exception:
        pass
    return False

def _init_state():
    ss = st.session_state
    ss.setdefault("trav_q_from", "")
    ss.setdefault("trav_q_to", "")
    ss.setdefault("trav_q_mid", "")
    ss.setdefault("trav_sel_from", None)
    ss.setdefault("trav_sel_to", None)
    ss.setdefault("trav_sel_mid", None)
    ss.setdefault("trav_last_url", None)

def _search_box(label, key_q: str, key_bucket: str, key_sel: str):
    """Caja con texto + sugerencias + select."""
    q = st.text_input(label, key=key_q, placeholder="Calle, número, ciudad… / Street, number, city…")
    labels = suggest_addresses(q, key_bucket) if q and len(q) >= 2 else []
    if labels:
        st.caption("Sugerencias:")
        idx = st.selectbox(
            "Elige una sugerencia",
            options=list(range(len(labels))),
            format_func=lambda i: labels[i],
            key=key_sel,
        )
    else:
        st.caption("Sin sugerencias todavía")

    cols = st.columns([0.33, 0.33, 0.34])
    with cols[0]:
        if st.button("Limpiar", key=f"btn_clear_{key_q}"):
            st.session_state[key_q] = ""
            st.session_state[key_sel] = None
            st.rerun()
    with cols[1]:
        if st.button("Usar mi ubicación", key=f"btn_loc_{key_q}"):
            ok = _ip_guess_bias()
            if ok:
                st.success("Sesgo de ubicación fijado ✅ (cerca de tu IP).")
            else:
                st.warning("No se pudo obtener tu ubicación aproximada.")
    return labels

# ----------------------------
# Main
# ----------------------------
def mostrar_viajero(t: dict):
    _init_state()

    st.subheader(t.get("trav_header", "Viajero"))
    st.caption(t.get("trav_caption", "Calcula tu ruta entre dos puntos con opción de una parada."))

    # ORIGEN
    st.markdown("**Origen**")
    labels_from = _search_box(
        t.get("input_origin", "Origen"),
        key_q="trav_q_from",
        key_bucket="trav_from",
        key_sel="trav_sel_from",
    )

    # DESTINO
    st.markdown("**Destino**")
    labels_to = _search_box(
        t.get("input_dest", "Destino"),
        key_q="trav_q_to",
        key_bucket="trav_to",
        key_sel="trav_sel_to",
    )

    # PARADA (opcional)
    st.markdown("**Parada intermedia (opcional)**")
    labels_mid = _search_box(
        t.get("input_mid", "Parada"),
        key_q="trav_q_mid",
        key_bucket="trav_mid",
        key_sel="trav_sel_mid",
    )

    if st.button(t.get("generate_trav", "Generar ruta"), type="primary"):
        q_from = st.session_state["trav_q_from"].strip()
        q_to   = st.session_state["trav_q_to"].strip()
        if not q_from or not q_to:
            st.error(t.get("missing_o_d", "Falta origen y/o destino."))
            return

        # Si hay selección, usa la etiqueta elegida; si no, usa lo que escribió el usuario.
        def _pick(q, labels, key_sel):
            sel = st.session_state.get(key_sel)
            if labels and sel is not None and 0 <= sel < len(labels):
                return labels[sel]
            return q

        from_label = _pick(q_from, labels_from, "trav_sel_from")
        to_label   = _pick(q_to, labels_to, "trav_sel_to")
        mid_label  = _pick(st.session_state["trav_q_mid"].strip(), labels_mid, "trav_sel_mid") if st.session_state["trav_q_mid"].strip() else None

        o = resolve_selection(from_label, "trav_from")
        d = resolve_selection(to_label, "trav_to")
        wps = []
        if mid_label:
            wps.append(resolve_selection(mid_label, "trav_mid")["address"])

        url = build_gmaps_url(o["address"], d["address"], wps if wps else None)
        st.session_state["trav_last_url"] = url
        st.success(t.get("route_ready", "¡Ruta lista!"))
        st.write(url)
        st.image(make_qr(url), caption=t.get("qr_route", "QR de la ruta"))

    if st.session_state["trav_last_url"]:
        with st.expander(t.get("last_route", "Última ruta generada"), expanded=False):
            st.write(st.session_state["trav_last_url"])
            st.image(make_qr(st.session_state["trav_last_url"]), caption=t.get("qr_route", "QR de la ruta"))