import streamlit as st
from app_utils import (
    suggest_addresses,
    resolve_selection, 
    build_gmaps_url,
    build_waze_url, 
    build_apple_maps_url, 
    set_location_bias,
    _use_ip_bias 
)
# from io import BytesIO

# -------------------------------
# INICIALIZACIÓN DEL ESTADO DE SESIÓN (CRUCIAL)
# -------------------------------

def initialize_session_state():
    """Asegura que todas las claves necesarias existan en st.session_state."""
    # Si alguna de estas claves falta, la aplicación falla con KeyError.
    if "prof_points" not in st.session_state:
        st.session_state["prof_points"] = []
    
    if "selected_point_index" not in st.session_state:
        st.session_state["selected_point_index"] = 0 
    if "is_editing_point" not in st.session_state:
        st.session_state["is_editing_point"] = False 
    if "edit_input_value" not in st.session_state:
        st.session_state["edit_input_value"] = "" 
    
    if "prof_text_input" not in st.session_state:
        st.session_state["prof_text_input"] = ""
    if "prof_top_suggestions" not in st.session_state:
        st.session_state["prof_top_suggestions"] = []
    if "prof_selection" not in st.session_state:
        st.session_state["prof_selection"] = ""
    if "prof_last_route_url" not in st.session_state:
        st.session_state["prof_last_route_url"] = None
    if "prof_use_loc_cb" not in st.session_state:
        st.session_state["prof_use_loc_cb"] = False
    if "_loc_bias" not in st.session_state:
        st.session_state["_loc_bias"] = None
    if "prof_mode" not in st.session_state:
        st.session_state["prof_mode"] = "Más rápido"
    if "prof_avoid" not in st.session_state:
        st.session_state["prof_avoid"] = "Ninguno"
        

# -------------------------------
# FUNCIONES DE MANEJO DE ESTADO Y LÓGICA
# -------------------------------

def _force_rerun_with_clear():
    """Fuerza el re-renderizado."""
    st.rerun()

def _reset_point_selection():
    """Reinicia el estado de selección/edición al añadir/limpiar/eliminar un punto."""
    st.session_state["is_editing_point"] = False
    st.session_state["edit_input_value"] = ""
    if st.session_state["prof_points"]:
        st.session_state["selected_point_index"] = max(0, min(st.session_state["selected_point_index"], len(st.session_state["prof_points"]) - 1))
    else:
        st.session_state["selected_point_index"] = 0
    _force_rerun_with_clear()

def _add_point_from_ui():
    """Añade la dirección seleccionada/escrita a la lista y limpia la barra."""
    value = ""
    # Si hay sugerencias, usa la seleccionada; si no, usa el texto de entrada
    if st.session_state.get("prof_top_suggestions"):
        value = st.session_state.get("prof_selection")
    else:
        value = st.session_state.get("prof_text_input")
        
    value = (value or "").strip()

    if not value:
        st.warning("Escribe o selecciona una dirección válida.")
        return

    st.session_state["prof_points"].append(value)
    st.success(f"Añadido: {value}")
    
    st.session_state["prof_text_input"] = ""
    st.session_state["prof_top_suggestions"] = []
    st.session_state["prof_selection"] = ""
    
    st.session_state["selected_point_index"] = len(st.session_state["prof_points"]) - 1
    _reset_point_selection()
    

def _clear_points():
    """Limpia la lista de puntos y el estado de la ruta."""
    st.session_state["prof_points"] = []
    st.session_state["prof_last_route_url"] = None
    st.session_state["prof_text_input"] = ""
    st.session_state["prof_top_suggestions"] = []
    st.session_state["prof_selection"] = ""
    st.session_state["selected_point_index"] = 0
    st.session_state["is_editing_point"] = False
    st.session_state["edit_input_value"] = ""

    _force_rerun_with_clear() 

# --- FUNCIONES DE MANEJO DE LA BARRA DE HERRAMIENTAS ---

def _select_point(index: int):
    """Establece el índice seleccionado para la edición/movimiento."""
    st.session_state["selected_point_index"] = index
    if st.session_state["is_editing_point"]:
        _reset_point_selection()
    else:
        _force_rerun_with_clear()

def _move_point(direction: str):
    """Mueve el punto seleccionado arriba o abajo."""
    i = st.session_state["selected_point_index"]
    pts = st.session_state["prof_points"]
    
    if direction == "up" and i > 0:
        pts.insert(i-1, pts.pop(i))
        st.session_state["selected_point_index"] = i - 1
    elif direction == "down" and i < len(pts) - 1:
        pts.insert(i+1, pts.pop(i))
        st.session_state["selected_point_index"] = i + 1
        
    _reset_point_selection()

def _delete_point():
    """Elimina el punto seleccionado."""
    i = st.session_state["selected_point_index"]
    if 0 <= i < len(st.session_state["prof_points"]):
        st.session_state["prof_points"].pop(i)
    _reset_point_selection()

def _enter_edit_mode():
    """Entra en modo edición, cargando el valor del punto seleccionado."""
    i = st.session_state["selected_point_index"]
    if 0 <= i < len(st.session_state["prof_points"]):
        st.session_state["is_editing_point"] = True
        st.session_state["edit_input_value"] = st.session_state["prof_points"][i]
    _force_rerun_with_clear()
    
def _save_point_from_toolbar():
    """Guarda el valor editado."""
    new_value = st.session_state["edit_input_value"].strip()
    i = st.session_state["selected_point_index"]
    
    if new_value and len(new_value) >= 3:
        st.session_state["prof_points"][i] = new_value
        st.success(f"Punto actualizado a: {new_value}")
        _reset_point_selection()
    else:
        st.warning("La dirección no puede estar vacía y debe tener al menos 3 letras.")


def _run_search():
    """Ejecuta la búsqueda de sugerencias (se llama on_change en el input)."""
    term = st.session_state.get("prof_text_input", "").strip()
    
    # Obtenemos el sesgo de ubicación si está activo
    bias = set_location_bias()
    
    if len(term) >= 3:
        suggestions = suggest_addresses(term, key_bucket="prof_top", min_len=3, bias=bias) 
        st.session_state["prof_top_suggestions"] = suggestions
        
        if not suggestions:
            st.warning(f"No se encontraron sugerencias para '{term}'.")
            st.session_state["prof_selection"] = ""
        else:
            st.session_state["prof_selection"] = suggestions[0]
    else:
        st.session_state["prof_top_suggestions"] = []
        st.session_state["prof_selection"] = ""


# -------------------------------
# Componente de búsqueda y lógica de ubicación
# -------------------------------

def _search_box():
    st.markdown("---")
    
    # 1. ENTRADA DE TEXTO
    st.text_input(
        "Buscar dirección...",
        key="prof_text_input",
        label_visibility="collapsed",
        placeholder="Escribe la dirección (mín. 3 letras) y pulsa ENTER",
        on_change=_run_search 
    )
    
    # 2. SELECTBOX CON SUGERENCIAS
    suggestions = st.session_state.get("prof_top_suggestions", [])
    
    # CORRECCIÓN: Solo renderiza el selectbox si hay sugerencias para evitar el error.
    if suggestions:
        st.selectbox(
            "Selecciona la sugerencia más precisa:",
            options=suggestions,
            key="prof_selection",
            label_visibility="visible"
        )
    
    # 3. Botones de acción y ubicación (Compactación de botones)
    col_add, col_clear, col_loc = st.columns([1.5, 1, 1]) 

    with col_add:
        st.button(
            "Añadir", 
            on_click=_add_point_from_ui, 
            type="primary",
            key="prof_add_btn",
            use_container_width=True
        )

    with col_clear:
        st.button("Limpiar", on_click=_clear_points, key="prof_clear_btn", use_container_width=True)

    with col_loc:
        # Aseguramos que la caja de ubicación mantenga su estado
        is_loc_active = st.checkbox(
            "📍 Usar mi ubicación", 
            key="prof_use_loc_cb", 
            value=st.session_state.get("_loc_bias") is not None,
            help="Si está activado, la búsqueda se sesga a tu ubicación IP."
        )
        
        # Lógica para activar/desactivar el sesgo de ubicación
        if is_loc_active:
             if st.session_state.get("_loc_bias") is None:
                 _use_ip_bias()
                 _force_rerun_with_clear() # Forzar rerun para cargar el bias
        else:
             if st.session_state.get("_loc_bias") is not None:
                 del st.session_state["_loc_bias"]
                 _force_rerun_with_clear() # Forzar rerun para eliminar el bias
                 
    st.markdown("---")

# -------------------------------
# Función principal de la pestaña
# -------------------------------
def mostrar_profesional():
    
    # ⭐️ CORRECCIÓN CRÍTICA: La llamada DEBE ir aquí para evitar NameError/KeyError.
    initialize_session_state() 

    st.header("Ruta de trabajo")
    
    # 1. Opciones de ruta (Tipo y Evitar)
    col_mode, col_avoid = st.columns([1, 1])
    with col_mode:
        st.selectbox("Tipo de ruta", ["Más rápido", "Más corto"], key="prof_mode", label_visibility="visible")
    with col_avoid:
        st.selectbox("Evitar", ["Ninguno", "Peajes", "Ferries"], key="prof_avoid", label_visibility="visible")


    # 2. Barra de búsqueda
    _search_box()

    # 3. Lista de puntos y herramientas
    pts = st.session_state["prof_points"] 
    st.subheader("Puntos de la ruta (orden de viaje)")
    
    if not pts:
        st.info("Agregue al menos dos puntos (origen y destino) para generar la ruta.")
        return 

    current_index = st.session_state["selected_point_index"]
    is_editing = st.session_state["is_editing_point"]

# 3.1. LISTADO DE PUNTOS CON DESCRIPCIONES Y BOTONES (Optimizados para móvil)
    st.markdown("---")
    
    for i, p in enumerate(pts):
        
        prefix = "Origen" if i == 0 else ("Destino" if i == len(pts) - 1 else f"Parada #{i}:")
        display_text = f"**{prefix}** {p}"
        
        # CORRECCIÓN DE DISEÑO MÓVIL: Ajuste de columnas para el botón compacto
        col_select, col_text = st.columns([0.5, 4]) 
        
        is_selected = (i == current_index)
        
        with col_select:
            btn_label = "📍" if is_selected else " " 
            btn_type = "primary" if is_selected else "secondary"
            
            st.button(
                btn_label,
                key=f"select_point_{i}",
                on_click=_select_point,
                args=(i,),
                use_container_width=True,
                type=btn_type,
                help="Selecciona este punto para moverlo, editarlo o eliminarlo."
            )
            
        with col_text:
            bg_color = "#E6F7FF" if is_selected else "transparent"
            
            st.markdown(
                f"""
                <div style='background-color: {bg_color}; padding: 10px; border-radius: 5px; margin-left: -15px;'>
                    {display_text}
                </div>
                """,
                unsafe_allow_html=True
            )
            
    st.markdown("---")

# --- 3.2. BARRA DE HERRAMIENTAS COMPACTA DE ICONOS ---
    st.markdown(f"**Punto Activo:** {current_index + 1} de {len(pts)}")
    
    # CORRECCIÓN DE DISEÑO MÓVIL: 4 columnas de igual tamaño
    col_up, col_down, col_edit, col_del = st.columns(4) 
    
    with col_up:
        if current_index > 0 and not is_editing:
            st.button("⬆️", key="btn_up", on_click=_move_point, args=("up",), use_container_width=True, help="Mover punto seleccionado hacia arriba.")
            
    with col_down:
        if current_index < len(pts) - 1 and not is_editing:
            st.button("⬇️", key="btn_down", on_click=_move_point, args=("down",), use_container_width=True, help="Mover punto seleccionado hacia abajo.")
            
    with col_edit:
        if is_editing:
            st.button("💾", key="btn_save", on_click=_save_point_from_toolbar, use_container_width=True, type="primary", help="Guardar el texto editado.")
        else:
            st.button("✏️", key="btn_edit", on_click=_enter_edit_mode, use_container_width=True, help="Editar la dirección del punto seleccionado.")
            
    with col_del:
        if not is_editing:
            st.button("🗑️", key="btn_delete", on_click=_delete_point, use_container_width=True, help="Eliminar el punto seleccionado.")
        else:
            st.button("❌", key="btn_cancel", on_click=_reset_point_selection, use_container_width=True, help="Cancelar la edición.")


# --- 3.3. CAMPO DE EDICIÓN ---
    if is_editing:
        st.text_input(
            f"Modificar punto seleccionado (Índice {current_index + 1}):",
            value=st.session_state["edit_input_value"],
            key="edit_input_value",
            label_visibility="visible",
            on_change=_save_point_from_toolbar 
        )
        st.markdown("---") 


    # 4. Botón Generar Ruta
    st.markdown("---")
    
    if st.button("Generar ruta profesional", type="primary", key="prof_generate_btn"):
        if len(pts) < 2:
            st.warning("Deben haber dos o más puntos (origen y destino).")
            return 
        
        # --- 4.1 Resolución de Puntos ---
        # Si la clave API no se cargó, advertimos
        from app_utils import gmaps
        if gmaps is None:
            st.error("ERROR CRÍTICO: No se pudo conectar con la API de Google Maps. Revisa tu clave en secrets.toml.")
            return

        origen_label = pts[0]
        destino_label = pts[-1]
        waypoints_labels = pts[1:-1]
        
        # Resolvemos las etiquetas a direcciones formateadas
        origen_meta = resolve_selection(origen_label, "prof_top")
        destino_meta = resolve_selection(destino_label, "prof_top")
        
        waypoints_resolved = [
            resolve_selection(label, "prof_top")["address"]
            for label in waypoints_labels
        ]
        
        # --- 4.2 Generación de URLs ---
        avoid_map = {
            "Peajes": "tolls",
            "Ferries": "ferries",
            "Ninguno": None
        }
        
        gmaps_url = build_gmaps_url(
            origin=origen_meta["address"],
            destination=destino_meta["address"],
            waypoints=waypoints_resolved,
            mode="driving", 
            avoid=avoid_map.get(st.session_state["prof_avoid"]),
            optimize=True 
        )
        
        waze_url = build_waze_url(origen_meta["address"], destino_meta["address"], waypoints_resolved)
        apple_url = build_apple_maps_url(origen_meta["address"], destino_meta["address"], waypoints_resolved)
        
        # --- 4.3 Mostrar Resultados ---
        st.session_state.prof_last_route_url = gmaps_url 
        
        st.success("¡Ruta generada correctamente! 👇")
        
        col_gmaps, col_waze, col_apple = st.columns([1, 1, 1])
        
        with col_gmaps:
            st.markdown(f"**[🗺️ Google Maps]({gmaps_url})**")
        with col_waze:
            st.markdown(f"**[🚗 Waze]({waze_url})**")
        with col_apple:
            st.markdown(f"**[🍎 Apple Maps]({apple_url})**")