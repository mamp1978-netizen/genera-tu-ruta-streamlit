git add README.md
git commit -m "docs: add full README with setup & usage"
git push
# Planificador de Rutas (Streamlit)

Aplicación web para crear rutas con varias paradas usando Google Maps, con:
- Autocompletado de direcciones (Google Places / SerpAPI / Nominatim).
- Una sola barra para añadir puntos y lista con **reordenar (↑/↓)** y **eliminar**.
- Generación de URL de Google Maps y **QR**.
- Modos de ruta: *Más rápido, Más corto, Evitar autopistas, Evitar peajes, Ruta panorámica*.
- Pestañas: **Profesional**, **Viajero**, **Turístico**.

> **Última actualización:** 2025-10-17  
> **© 2025 Miguel Ángel Molinero Palacios. Todos los derechos reservados.**

---

## ▶️ Demo / Despliegue
- Local: ver sección **Ejecución local**.
- Streamlit Cloud: ver **Despliegue en Streamlit Cloud** (más abajo).

---

## 📁 Estructura del proyecto
---

---

## ✅ Requisitos

- Python **3.10+** (recomendado 3.11 o 3.12)
- Una cuenta de **Google Cloud** con **Places API** habilitada  
  (para autocompletado de direcciones).  
- **SerpAPI** opcional (puede ayudar con resultados de Maps).
- Conexión a internet desde el servidor donde corre la app.

---

## 🔑 Variables de entorno

Crea un archivo `.env` (usa como guía `.env.example`):
> En despliegues tipo Streamlit Cloud puedes usar **Secrets** en lugar de `.env`:
> `Settings → Secrets → Add new secret` con las mismas claves.

---

## 🧪 Instalación

```bash
# Clonar
git clone https://github.com/mamp1978-netizen/Apprutas.git
cd Apprutas

# (opcional) Crear entorno virtual
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt