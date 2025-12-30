from decimal import Decimal
from django.db import transaction
import pandas as pd
from datetime import datetime

from core.models import Portfolio, Price, Weight, Position, Asset


# Requisito 3: Calcular cantidades iniciales c_{i,0}
# Esta función implementa la fórmula: c_{i,0} = (w_{i,0} * V_0) / p_{i,0}
@transaction.atomic
def calculate_initial_positions(portfolio: Portfolio):
    """
    Calcula cuántas unidades de cada activo comprar al inicio.
    Usa los weights del Excel y el valor inicial del portafolio.
    """
    start_date = portfolio.start_date
    initial_value = portfolio.initial_value  # V_0 = $1,000,000,000

    # Obtener los weights iniciales del portafolio
    weights = Weight.objects.filter(portfolio=portfolio,date=start_date).select_related("asset")

    # Para cada activo, calcular cuántas unidades comprar
    for weight in weights:
        # Necesito el precio del activo en la fecha inicial
        price = Price.objects.get(asset=weight.asset,date=start_date
        )

        # Aplicar la fórmula: cantidad = (peso * valor_total) / precio
        quantity = (weight.weight * initial_value) / price.price
        value = quantity * price.price  # x_{i,0} = c_{i,0} * p_{i,0}

        # Guardar la posición inicial
        Position.objects.update_or_create(
            portfolio=portfolio,
            asset=weight.asset,
            date=start_date,
            defaults={
                "quantity": quantity,  # c_{i,0}
                "value_at_date": value,  # x_{i,0}
            },
        )


# Requisito 4: Calcular evolución histórica
@transaction.atomic
def calculate_historical_positions(portfolio: Portfolio):
    """
    Calcula las posiciones para todas las fechas históricas.
    Como las cantidades se mantienen constantes, solo actualizo los valores
    según los nuevos precios: x_{i,t} = p_{i,t} * c_{i,0}
    """
    # Primero obtengo las cantidades iniciales que ya calculé
    initial_positions = Position.objects.filter(portfolio=portfolio,date=portfolio.start_date).select_related("asset")

    if not initial_positions.exists():
        return

    # Obtener todas las fechas para las que tengo precios, todas las fechas únicas de precios
    assets = [pos.asset for pos in initial_positions]
    all_dates = (
        Price.objects
        .values_list("date", flat=True)
        .distinct()
        .order_by("date")
    )
    positions_created = 0
    # Para cada fecha, recalcular el valor usando los precios actuales
    for date in all_dates:
        if date == portfolio.start_date:
            continue  # Ya está calculado

        for initial_pos in initial_positions:
            try:
                # Obtener el precio del activo en esta fecha
                price = Price.objects.get(
                    asset=initial_pos.asset,
                    date=date
                )
                # El valor cambia porque el precio cambió, pero la cantidad no
                value = initial_pos.quantity * price.price

                Position.objects.update_or_create(
                    portfolio=portfolio,
                    asset=initial_pos.asset,
                    date=date,
                    defaults={
                        "quantity": initial_pos.quantity,  # c_{i,t} = c_{i,0}
                        "value_at_date": value,  # x_{i,t} = p_{i,t} * c_{i,0}
                    },
                )
                positions_created += 1
            except Price.DoesNotExist:
                continue
    print(f" {positions_created} posiciones históricas creadas para {portfolio.name}")

# Requisito 2: Función ETL para cargar datos del Excel
# Esta función lee el Excel y carga todo a la base de datos
@transaction.atomic
def load_excel_data(excel_file):
    """
    ETL
    Procesa el archivo Excel y carga todos los datos.
    Se puede llamar desde la web (upload) o desde un comando de management.
    """
    print("INICIANDO CARGA DE DATOS")
    # Leer las dos hojas del Excel
    weights_df = pd.read_excel(excel_file, sheet_name="weights")
    prices_df = pd.read_excel(excel_file, sheet_name="Precios")
    
    # Valores fijos según el requerimiento
    start_date = datetime(2022, 2, 15).date()  # t=0
    initial_value = Decimal("1000000000")  # V_0 = $1,000,000,000

    # Paso 1: Crear los 17 activos
    # Los nombres vienen de la primera columna de la hoja Weights
    asset_names = weights_df['activos'].dropna().astype(str).tolist()
    assets = {}
    for name in asset_names:
        name_clean = str(name).strip()
        symbol = name_clean[:20]
        
        asset, created = Asset.objects.get_or_create(
            name=name_clean,
            defaults={"symbol": symbol}
        )
        assets[name_clean] = asset
        if created:
            print(f"  Ok {name_clean}")
    
    print(f"  TOTAL: {len(assets)} activos")

    # Paso 2: Crear los dos portafolios con valor inicial
    portfolio1, _ = Portfolio.objects.get_or_create(
        name="Portfolio 1",
        defaults={
            "initial_value": initial_value,
            "start_date": start_date
        }
    )
    portfolio2, _ = Portfolio.objects.get_or_create(
        name="Portfolio 2",
        defaults={
            "initial_value": initial_value,
            "start_date": start_date
        }
    )

    # Paso 3: Cargar los weights iniciales
    # Columna C = Portfolio 1, Columna D = Portfolio 2
    Weight.objects.filter(portfolio__in=[portfolio1, portfolio2], date=start_date).delete()
    weights_created = 0
    
    
    for _, row in weights_df.iterrows():
        asset_name = str(row['activos']).strip()
        asset = assets[asset_name]
        
        weight1 = Decimal(str(row['portafolio 1']))
        weight2 = Decimal(str(row['portafolio 2']))
        
        
        # Leer weights de cada columna
        Weight.objects.update_or_create(
            portfolio=portfolio1,
            asset=asset,
            date=start_date,
            weight=weight1
        )
        
        Weight.objects.update_or_create(
            portfolio=portfolio2,
            asset=asset,
            date=start_date,
            weight=weight2
        )
        weights_created += 2
        print(f" {weights_created} pesos creados")

    # Paso 4: Cargar todos los precios históricos
    # Primera columna son fechas, columnas 1-17 son precios de cada activo
    Price.objects.all().delete()
    
    prices_created = 0
    dates_processed = 0
        
    for idx, row in prices_df.iterrows():
        date_val = row['Dates']
        
        if pd.isna(date_val):
            continue
        
        # Convertir fecha
        if isinstance(date_val, (datetime, pd.Timestamp)):
            date = date_val.date()
        else:
            try:
                date = pd.to_datetime(date_val).date()
            except:
                continue
        
        dates_processed += 1
        
        # Para cada activo (columna)
        for asset_name, asset in assets.items():
            # Buscar el precio en la columna correspondiente
            if asset_name not in row.index:
                continue
            
            price_val = row[asset_name]
            
            if pd.isna(price_val):
                continue
            
            Price.objects.create(
                asset=asset,
                date=date,
                price=Decimal(str(price_val))
            )
            prices_created += 1
    
    print(f" {prices_created} precios creados")
    print(f" {dates_processed} fechas procesadas")

    # Paso 5: Calcular cantidades iniciales (Requisito 3)
    # Esto calcula c_{i,0} para cada activo en cada portafolio
    calculate_initial_positions(portfolio1)
    calculate_initial_positions(portfolio2)

    # Paso 6: Calcular posiciones históricas (Requisito 4)
    # Esto calcula x_{i,t} y w_{i,t} para todas las fechas
    calculate_historical_positions(portfolio1)
    calculate_historical_positions(portfolio2)
    
    return True
