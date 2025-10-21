# i18n.py
from __future__ import annotations

# Diccionario de textos. Añade más idiomas/entradas cuando quieras.
TEXTS = {
    "es": {
        # App
        "app_title": "Planificador de Rutas",
        "app_subtitle": "Crea rutas con paradas usando direcciones completas. La última parada puede ser el destino final.",
        "tabs": ["💼 Profesional", "🧳 Viajero", "🌴 Turístico"],
        "footer_a": "Autocompletado: Google Places / SerpAPI / Nominatim (OSM).",
        "footer_b": "Añade tus claves en .env o en st.secrets (`GOOGLE_PLACES_API_KEY`, `SERPAPI_API_KEY`).",

        # Sidebar
        "lang_label": "Idioma / Language",
        "lang_es": "Español",
        "lang_en": "Inglés",

        # Comunes
        "origin": "Origen",
        "destination": "Destino",
        "stop_num": "Parada #{i}",
        "open_now_check": "Comprobar si los lugares están abiertos ahora (si hay datos de Google)",
        "route_generated": "✅ Ruta generada ({pref})",
        "scan_qr": "Escanea para abrir la ruta en el móvil",
        "last_route": "Última ruta generada (esta sesión)",
        "open_status_now": "Estado de apertura (ahora)",
        "open": "✅ Abierto",
        "closed": "⛔ Cerrado",
        "nodata": "ℹ️ Sin datos",
        "need_two_points": "Debes tener al menos **2 puntos** (origen y destino).",
        "add_at_least_two": "Añade al menos dos puntos (origen y destino) para generar la ruta.",
        "removed": "🗑️ Eliminado: {x}",
        "added": "➕ Añadido: {x}",

        # Tipos de ruta
        "route_type_label": "🧭 Tipo de ruta",
        "route_types": ["Más rápido", "Más corto", "Evitar autopistas", "Evitar peajes", "Ruta panorámica"],

        # Profesional
        "prof_header": "Ruta de trabajo",
        "prof_caption": "Añade puntos con la barra de arriba. El **primero** es **origen**, el **último** es **destino**; los demás son **paradas intermedias**. Puedes reordenar con las flechas y eliminar cualquier punto.",
        "search_label": "Buscar dirección… (pulsa ENTER para añadir)",
        "suggestions": "Sugerencias:",
        "add_enter": "Añadir (ENTER)",
        "use_my_location": "📍 Usar mi ubicación",
        "list_title": "Puntos de la ruta (orden de viaje)",
        "btn_up": "↑",
        "btn_down": "↓",
        "btn_del": "🗑️",
        "generate_prof": "Generar ruta profesional",
        "no_suggestions": "Sin sugerencias todavía",

        # Viajero
        "trav_header": "Plan rápido (viajero)",
        "trav_caption": "Indica inicio y final. (Puedes añadir una parada opcional).",
        "input_origin": "Origen",
        "input_dest": "Destino",
        "input_mid": "Parada intermedia (opcional)",
        "generate_trav": "Crear ruta (viajero)",
        "route_ready": "Ruta generada",
        "qr_route": "QR de la ruta",
        "missing_o_d": "Falta origen o destino.",

        # Turístico
        "tour_header": "Ruta turística con varias paradas",
        "tour_caption": "La última parada se toma como destino final.",
        "tour_start": "Punto de inicio",
        "tour_end": "Punto final",
        "tour_spots": "Lugares a visitar (uno por línea)",
        "generate_tour": "Crear itinerario turístico",
        "tour_ready": "Itinerario listo",
        "tour_qr": "QR del itinerario",
        "need_start_end": "Indica inicio y final.",

        # Form helpers
        "type_or_select": "Escribe o selecciona una dirección antes de añadir.",
        "loc_added": "📍 Añadido por ubicación (aprox.): {x}",
        "loc_failed": "No se pudo obtener tu ubicación. Inténtalo de nuevo o escribe manualmente.",
    },
    "en": {
        # App
        "app_title": "Route Planner",
        "app_subtitle": "Create routes with multiple stops using full addresses. The last stop becomes the final destination.",
        "tabs": ["💼 Professional", "🧳 Traveler", "🌴 Tourist"],
        "footer_a": "Autocomplete: Google Places / SerpAPI / Nominatim (OSM).",
        "footer_b": "Add your keys in .env or st.secrets (`GOOGLE_PLACES_API_KEY`, `SERPAPI_API_KEY`).",

        # Sidebar
        "lang_label": "Idioma / Language",
        "lang_es": "Spanish",
        "lang_en": "English",

        # Common
        "origin": "Origin",
        "destination": "Destination",
        "stop_num": "Stop #{i}",
        "open_now_check": "Check if places are open now (when Google data exists)",
        "route_generated": "✅ Route generated ({pref})",
        "scan_qr": "Scan to open the route on your phone",
        "last_route": "Last route generated (this session)",
        "open_status_now": "Open status (now)",
        "open": "✅ Open",
        "closed": "⛔ Closed",
        "nodata": "ℹ️ No data",
        "need_two_points": "You must have at least **2 points** (origin and destination).",
        "add_at_least_two": "Add at least two points (origin & destination) to generate the route.",
        "removed": "🗑️ Removed: {x}",
        "added": "➕ Added: {x}",

        # Route types
        "route_type_label": "🧭 Route preference",
        "route_types": ["Fastest", "Shortest", "Avoid highways", "Avoid tolls", "Scenic route"],

        # Professional
        "prof_header": "Work route",
        "prof_caption": "Add points with the top bar. The **first** is **origin**, the **last** is **destination**; others are **intermediate stops**. Reorder with arrows and remove any point.",
        "search_label": "Search address… (press ENTER to add)",
        "suggestions": "Suggestions:",
        "add_enter": "Add (ENTER)",
        "use_my_location": "📍 Use my location",
        "list_title": "Route points (travel order)",
        "btn_up": "↑",
        "btn_down": "↓",
        "btn_del": "🗑️",
        "generate_prof": "Generate work route",
        "no_suggestions": "No suggestions yet",

        # Traveler
        "trav_header": "Quick plan (traveler)",
        "trav_caption": "Set start and end. (You can add an optional stop.)",
        "input_origin": "Origin",
        "input_dest": "Destination",
        "input_mid": "Intermediate stop (optional)",
        "generate_trav": "Create route (traveler)",
        "route_ready": "Route ready",
        "qr_route": "Route QR",
        "missing_o_d": "Missing origin or destination.",

        # Tourist
        "tour_header": "Tourist route with multiple stops",
        "tour_caption": "The last stop is taken as final destination.",
        "tour_start": "Start point",
        "tour_end": "End point",
        "tour_spots": "Places to visit (one per line)",
        "generate_tour": "Create tourist itinerary",
        "tour_ready": "Itinerary ready",
        "tour_qr": "Itinerary QR",
        "need_start_end": "Please set start and end.",

        # Form helpers
        "type_or_select": "Type or pick an address before adding.",
        "loc_added": "📍 Added by location (approx.): {x}",
        "loc_failed": "Could not get your location. Try again or type manually.",
    }
}

def get_texts(lang_code: str) -> dict:
    lang = (lang_code or "es").lower()
    if lang not in TEXTS:
        lang = "es"
    return TEXTS[lang]
