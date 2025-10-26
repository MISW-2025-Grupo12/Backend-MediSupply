import os
from datetime import datetime

def get_version_info():
    """
    Retorna la información de versión del servicio.
    
    Returns:
        dict: Diccionario con version, build_date, commit_hash y environment
    """
    return {
        "version": os.getenv("VERSION", "1.0.0-dev"),
        "build_date": os.getenv("BUILD_DATE", datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")),
        "commit_hash": os.getenv("COMMIT_HASH", "unknown"),
        "environment": os.getenv("ENVIRONMENT", "development")
    }

