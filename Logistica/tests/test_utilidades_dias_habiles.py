from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from aplicacion.utilidades.dias_habiles import calcular_dia_habil_siguiente


class ColombiaHolidaysMock(dict):
    def __init__(self, years):
        super().__init__()
        self.years = set(years if isinstance(years, list) else [years])

    def __contains__(self, item):
        return dict.__contains__(self, item)


def test_calcular_dia_habil_siguiente_en_dia_habil():
    fecha = datetime(2025, 11, 10)  # lunes

    festivos = ColombiaHolidaysMock([2025])

    with patch('aplicacion.utilidades.dias_habiles.holidays.Colombia', return_value=festivos):
        siguiente = calcular_dia_habil_siguiente(fecha)

    assert siguiente.date() == (fecha + timedelta(days=1)).date()


def test_calcular_dia_habil_saltea_fin_de_semana():
    fecha = datetime(2025, 11, 14)  # viernes

    festivos = ColombiaHolidaysMock([2025])

    with patch('aplicacion.utilidades.dias_habiles.holidays.Colombia', return_value=festivos):
        siguiente = calcular_dia_habil_siguiente(fecha)

    assert siguiente.weekday() == 0  # lunes
    assert (siguiente - fecha).days == 3


def test_calcular_dia_habil_saltea_festivo():
    fecha = datetime(2025, 11, 10)  # lunes

    festivos = ColombiaHolidaysMock([2025])
    festivos[fecha.date() + timedelta(days=1)] = 'Festivo'

    with patch('aplicacion.utilidades.dias_habiles.holidays.Colombia', return_value=festivos):
        siguiente = calcular_dia_habil_siguiente(fecha)

    assert (siguiente - fecha).days == 2

