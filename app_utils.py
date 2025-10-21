import streamlit as st # Necesario para usar st.secrets
import googlemaps
import os
# from qrcode import make as make_qr_code 
from io import BytesIO
from urllib.parse import quote
# import warnings 
import requests 


# Inicialización del cliente de Google Maps
# CORRECCIÓN DE SEGURIDAD: Lee la clave desde secrets.toml, cayendo a os.environ
API_KEY = st.secrets.get("GOOGLE_PLACES_API_KEY") or os.environ.get("GOOGLE_PLACES_API_KEY") 
gmaps = googlemaps.Client(key=API_KEY) if API_KEY else None


# --- LÓGICA DE GEOLOCALIZACIÓN Y SUGERENCIAS ---

# Asume que esta función existe en tu código, si no, es un placeholder para la lógica de sugestiones
def suggest_addresses(address_term, key_bucket, min_len=3, bias=None):
    """
    Usa la API de Google Places Autocomplete para obtener sugerencias.
    """
    if gmaps is None:
        st.error("No se pudo inicializar la API de Google Maps. Por favor, revisa la clave API en secrets.toml.")
        return []
    
    if len(address_term) < min_len:
        return []
        
    try:
        # Aquí puedes definir un 'components' como 'country:es' si solo quieres España
        # location_bias solo se usa si se proporciona (desde la ubicación IP)
        suggestions = gmaps.places_autocomplete(
            address_term,
            session_token=key_bucket,
            language="es",
            location_bias=bias
        )
        return [s['description'] for s in suggestions]
    except Exception as e:
        # warnings.warn(f"Error en Google Places Autocomplete: {e}")
        return []

def resolve_selection(address_label, key_bucket):
    """
    Usa la API de Geocoding para obtener la lat/lng de la dirección seleccionada.
    Retorna un diccionario con 'address' (normalizada) y 'lat_lng'.
    """
    if gmaps is None:
        return {"address": address_label, "lat_lng": None}
    
    try:
        results = gmaps.geocode(address_label, language="es")
        if results:
            first_result = results[0]
            lat_lng = first_result['geometry']['location']
            return {
                "address": first_result['formatted_address'],
                "lat_lng": f"{lat_lng['lat']},{lat_lng['lng']}"
            }
        else:
            return {"address": address_label, "lat_lng": None}
    except Exception as e:
        # warnings.warn(f"Error en Google Geocode: {e}")
        return {"address": address_label, "lat_lng": None}


def _use_ip_bias():
    """Obtiene la ubicación basada en la IP y la guarda en el estado de sesión."""
    # Intentamos obtener la IP y luego la ubicación
    try:
        # Usar un servicio externo simple para la IP (solo funciona en Streamlit Cloud)
        ip_data = requests.get('https://ipinfo.io/json').json()
        loc_str = ip_data.get('loc') # Formato "lat,lng"
        
        if loc_str:
            # location_bias para la API de Places: circular:radius@lat,lng
            st.session_state["_loc_bias"] = f"circle:20000@{loc_str}" # Radio de 20km
        else:
            st.warning("No se pudo obtener la ubicación IP. Usando búsqueda global.")
            st.session_state["_loc_bias"] = None

    except Exception as e:
        st.error("Error al obtener la ubicación IP para sesgo de búsqueda.")
        st.session_state["_loc_bias"] = None
        
def set_location_bias():
    """Retorna el sesgo de ubicación (si está activo) para las funciones de búsqueda."""
    return st.session_state.get("_loc_bias")


# --- CONSTRUCCIÓN DE ENLACES DE MAPAS ---

def build_gmaps_url(origin, destination, waypoints=None, mode="driving", avoid=None, optimize=False):
    """Construye la URL para Google Maps."""
    base_url = "https://www.google.com/maps/dir/?api=1"
    
    params = {
        'origin': quote(origin),
        'destination': quote(destination),
        'travelmode': mode,
    }
    
    if waypoints:
        waypoints_str = '|'.join([quote(wp) for wp in waypoints])
        params['waypoints'] = waypoints_str
        if optimize:
            params['dir_action'] = 'navigate' # A veces optimiza, otras no, pero es la mejor práctica
            
    if avoid:
        params['avoid'] = avoid
        
    url = base_url + "&" + "&".join([f"{key}={value}" for key, value in params.items()])
    return url

def build_waze_url(origin, destination, waypoints=None):
    """Construye la URL para Waze. Waze es muy limitado y solo soporta origen y destino."""
    # Waze no soporta paradas intermedias ni optimización, solo origen y destino.
    # Usaremos el destino final.
    base_url = "https://waze.com/ul"
    
    params = {
        'navigate': 'yes',
        'q': quote(destination)
    }
    
    # Opcional: Intentar añadir origen (Waze lo soporta con "from=")
    # Sin embargo, 'q' es la forma más compatible.
    
    url = base_url + "?" + "&".join([f"{key}={value}" for key, value in params.items()])
    return url

def build_apple_maps_url(origin, destination, waypoints=None):
    """Construye la URL para Apple Maps."""
    # Apple Maps soporta paradas intermedias
    base_url = "http://maps.apple.com/"
    
    # Formato: daddr=DESTINO&saddr=ORIGEN&dirflg=d&z=10
    
    params = {
        'daddr': quote(destination),
        'saddr': quote(origin),
        'dirflg': 'd' # d=driving
    }
    
    if waypoints:
        # Apple Maps usa 'via' para puntos intermedios, pero el soporte URL es variable.
        # Es más fiable concatenar los waypoints al destino en el formato: destino/parada1/parada2
        # Lo más fiable para Apple Maps es usar el formato de búsqueda concatenada:
        all_stops = [quote(destination)] + [quote(wp) for wp in waypoints]
        params['daddr'] = '@'.join(all_stops)
    
    url = base_url + "?" + "&".join([f"{key}={value}" for key, value in params.items()])
    return url