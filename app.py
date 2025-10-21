import streamlit as st
import os
from google import genai
from google.genai.errors import APIError

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Generador de Nombres con Gemini",
    layout="centered"
)

st.title("Generador de Nombres para Apps de IA 🤖")
st.markdown("Describe tu aplicación y Gemini te sugerirá 5 nombres creativos.")
st.divider()

# --- Entrada del Usuario ---
# Crea un campo de texto donde el usuario puede escribir su descripción
descripcion_app = st.text_input(
    label="Descripción de tu App:",
    placeholder="Ej: Una app que ayuda a los estudiantes a resumir sus apuntes universitarios."
)

# Botón para activar la generación
if st.button("Generar Nombres con Gemini"):
    
    if not descripcion_app:
        st.error("Por favor, introduce una descripción de tu aplicación.")
        st.stop()

    try:
        # El cliente de genai busca automáticamente la clave en la variable de entorno GEMINI_API_KEY
        # Verificación de la Clave API
        if not os.getenv("GEMINI_API_KEY"):
            st.error("Error: La clave GEMINI_API_KEY no está configurada en el entorno.")
            st.stop()
            
        client = genai.Client()

        # Define el prompt
        model = "gemini-2.5-flash"
        
        # Construye el prompt final para la IA
        full_prompt = f"Dame 5 ideas creativas de nombre para la siguiente aplicación de IA, incluyendo una explicación y un eslogan para cada una. La descripción de la aplicación es: {descripcion_app}"

        st.info("Conectando y generando nombres con Gemini...")

        # Genera el contenido
        with st.spinner('Pensando en nombres...'):
            response = client.models.generate_content(
                model=model,
                contents=full_prompt
            )

        # Muestra la respuesta en formato Markdown
        st.success("¡Generación Completada!")
        st.markdown(response.text)

    except APIError as e:
        st.error(f"Error de la API: Asegúrate de que tu clave es válida. Detalle: {e}")
    except Exception as e:
        st.error(f"Ocurrió un error inesperado: {e}")

