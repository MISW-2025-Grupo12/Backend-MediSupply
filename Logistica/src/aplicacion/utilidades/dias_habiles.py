"""
Utilidad para calcular días hábiles en Colombia.
Excluye sábados, domingos y festivos colombianos.
Utiliza la librería 'holidays' para calcular automáticamente festivos móviles.
"""
from datetime import datetime, timedelta
import holidays

def _es_fin_de_semana(fecha: datetime) -> bool:
    # Verifica si una fecha es sábado o domingo.
    # weekday() retorna 0=Lunes, 6=Domingo
    # Sábado = 5, Domingo = 6
    return fecha.weekday() >= 5

def _es_dia_habil(fecha: datetime, festivos_colombia: holidays.Colombia) -> bool:
    # Verifica si una fecha es un día hábil (no es fin de semana ni festivo).
    if _es_fin_de_semana(fecha):
        return False
    if fecha.date() in festivos_colombia:
        return False
    return True

def calcular_dia_habil_siguiente(fecha: datetime) -> datetime:
    """
    Calcula el siguiente día hábil a partir de una fecha dada.
    Excluye sábados, domingos y festivos colombianos.
    Utiliza la librería 'holidays' que calcula automáticamente festivos móviles
    (como semana santa, Jueves Santo, Viernes Santo, etc.) para cualquier año.
    """
    # Crear objeto holidays para Colombia
    # Se inicializa con el año de la fecha para optimizar
    festivos_colombia = holidays.Colombia(years=fecha.year)

    # Si la fecha es muy cerca del fin de año, incluir el año siguiente también
    if fecha.month == 12 and fecha.day >= 25:
        festivos_colombia = holidays.Colombia(years=[fecha.year, fecha.year + 1])

    fecha_siguiente = fecha + timedelta(days=1)

    # Avanzar hasta encontrar un día hábil
    max_intentos = 30  # Límite de seguridad para evitar loops infinitos
    intentos = 0

    while not _es_dia_habil(fecha_siguiente, festivos_colombia) and intentos < max_intentos:
        fecha_siguiente += timedelta(days=1)
        intentos += 1

        # Si cambiamos de año, actualizar el objeto holidays
        if fecha_siguiente.year != fecha.year and fecha_siguiente.year not in festivos_colombia.years:
            festivos_colombia = holidays.Colombia(years=[fecha.year, fecha_siguiente.year])

    if intentos >= max_intentos:
        # Si no encontramos un día hábil en 30 días, retornar la fecha siguiente
        # (esto no debería pasar en condiciones normales)
        return fecha + timedelta(days=1)

    return fecha_siguiente
