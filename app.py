# Launcher para Streamlit en staging
# 1) Si photo_agent_app.py define main(), la ejecutamos.
# 2) Si no define main(), el import ejecutará el top-level (st.*).
try:
    from photo_agent_app import main  # type: ignore
    if callable(main):
        main()
    else:
        # Si no es callable, forzamos un import completo
        import importlib
        importlib.import_module("photo_agent_app")
except (ImportError, AttributeError):
    # Fallback: import simple (ejecuta top-level si existe)
    from photo_agent_app import *  # noqa
