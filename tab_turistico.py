# tab_turistico.py
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

def _ip_guess_bias():
    try:
        ip = requests.get("https://ipapi.co/json/", timeout=6).json()
        lat = ip.get("latitude")
        lng = ip.get("longitude")
        if lat and lng:
            set_location_bias(float(lat), float(lng), radius_m=50000)
            return True
    except Exception:
        pass
    return False

def _init_state():
    ss = st.session_state
    ss.setdefault("tour_q_from", "")
    ss.setdefault("tour_q_to", "")
    ss.setdefault("tour_sel_from", None)
    ss.setdefault("tour_sel_to", None)
    ss.setdefault("tour_last_url", None)

def _search_box(label, key_q: str, key_bucket: str, key_sel: str):
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

def mostrar_turistico(t: dict):
    _init_state()

    st.subheader(t.get("tour_header", "Turístico"))
    st.caption(t.get("tour_caption", "Crea una ruta turística con varias paradas."))

    # Origen y destino con autocompletado
    st.markdown("**Origen**")
    labels_from = _search_box(
        t.get("tour_start", "Punto de inicio"),
        key_q="tour_q_from",
        key_bucket="tour_from",
        key_sel="tour_sel_from",
    )

    st.markdown("**Destino**")
    labels_to = _search_box(
        t.get("tour_end", "Punto final"),
        key_q="tour_q_to",
        key_bucket="tour_to",
        key_sel="tour_sel_to",
    )

    st.markdown(f"**{t.get('tour_spots', 'Lugares a visitar (uno por línea)')}**")
    spots_text = st.text_area("", height=140, placeholder="Sagrada Familia, Barcelona\nParc Güell, Barcelona\nCasa Batlló, Barcelona…")
    stops = [s.strip() for s in spots_text.splitlines() if s.strip()]

    if st.button(t.get("generate_tour", "Generar ruta turística"), type="primary"):
        q_from = st.session_state["tour_q_from"].strip()
        q_to   = st.session_state["tour_q_to"].strip()
        if not q_from or not q_to:
            st.error(t.get("need_start_end", "Necesitas indicar inicio y fin."))
            return

        # Si hay selección, usarla; si no, el texto
        def _pick(q, labels, key_sel):
            sel = st.session_state.get(key_sel)
            if labels and sel is not None and 0 <= sel < len(labels):
                return labels[sel]
            return q

        from_label = _pick(q_from, labels_from, "tour_sel_from")
        to_label   = _pick(q_to, labels_to, "tour_sel_to")

        o = resolve_selection(from_label, "tour_from")
        d = resolve_selection(to_label, "tour_to")

        # Paradas (no llevan autocompletado por líneas; se resuelven como texto directo)
        url = build_gmaps_url(o["address"], d["address"], stops if stops else None)
        st.session_state["tour_last_url"] = url

        st.success(t.get("tour_ready", "¡Ruta turística lista!"))
        st.write(url)
        st.image(make_qr(url), caption=t.get("tour_qr", "QR de la ruta"))

    if st.session_state["tour_last_url"]:
        with st.expander(t.get("last_route", "Última ruta generada"), expanded=False):
            st.write(st.session_state["tour_last_url"])
            st.image(make_qr(st.session_state["tour_last_url"]), caption=t.get("tour_qr", "QR de la ruta"))