from decimal import Decimal
from typing import List, Dict

from core.models import Portfolio, Position

# Requisito 4: Endpoint que retorna w_{i,t} y V_t
# Esta función usa el ORM de Django para obtener los datos y calcular los valores
def get_portfolio_weights_and_value(
    portfolio: Portfolio,
    start_date,
    end_date
) -> List[Dict]:
    """
    Retorna los pesos y el valor total del portafolio para un rango de fechas.
    Usa el ORM de Django como se pidió en el requerimiento.
    """
    # Primero obtengo todas las fechas en el rango usando el ORM
    dates = (
        Position.objects.filter(
            portfolio=portfolio,
            date__range=[start_date, end_date]
        )
        .values_list("date", flat=True)
        .distinct()
        .order_by("date")
    )

    result = []

    # Para cada fecha, calcular V_t y w_{i,t}
    for date in dates:
        # Obtener todas las posiciones del portafolio en esta fecha
        positions = Position.objects.filter(
            portfolio=portfolio,
            date=date
        ).select_related("asset")  # Optimización: evita queries adicionales

        # Calcular V_t = sum(x_{i,t}) - suma de todos los valores
        total_value = sum(
            (p.value_at_date for p in positions),
            Decimal("0")
        )

        # Calcular w_{i,t} = x_{i,t} / V_t para cada activo
        weights = []
        for position in positions:
            weight = (
                position.value_at_date / total_value
                if total_value > 0 else Decimal("0")
            )
            weights.append({
                "asset": position.asset.symbol,
                "weight": float(weight),  # Convertir para JSON
            })

        result.append({
            "date": date.isoformat(),
            "total_value": float(total_value),  # V_t
            "weights": weights,  # w_{i,t} para cada activo
        })

    return result
