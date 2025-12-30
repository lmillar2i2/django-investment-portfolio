from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
import json
from datetime import datetime

from core.models import Portfolio
from core.selectors import get_portfolio_weights_and_value
from core.services import load_excel_data

# Bonus 1: Vista con gráficos comparativos
# Muestra gráficos de w_{i,t} (stacked area) y V_t (línea)
def portfolio_charts(request):
    """
    Vista principal que permite cargar el Excel y ver gráficos.
    Combina el ETL (upload) con la visualización de datos.
    """
    portfolios = Portfolio.objects.all()
    
    # Si viene un POST, es porque están subiendo el Excel
    if request.method == 'POST' and 'excel_file' in request.FILES:
        excel_file = request.FILES['excel_file']
        
        # Validar que sea Excel
        if not excel_file.name.endswith(('.xlsx', '.xls')):
            messages.error(request, 'Por favor sube un archivo Excel (.xlsx o .xls)')
        else:
            try:
                # Llamar a la función ETL para procesar el archivo
                load_excel_data(excel_file)
                messages.success(request, '✓ Excel cargado exitosamente. Datos procesados.')
            except Exception as e:
                messages.error(request, f'Error al procesar el Excel: {str(e)}')
    
    # Si viene un GET con parámetros, mostrar los gráficos
    portfolio_id = request.GET.get('portfolio_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    data = None
    data_json = None
    selected_portfolio = None
    
    if portfolio_id and start_date and end_date:
        selected_portfolio = get_object_or_404(Portfolio, pk=portfolio_id)
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # Obtener los datos usando la misma función del API
            data = get_portfolio_weights_and_value(
                selected_portfolio,
                start,
                end
            )
            data_json = json.dumps(data)  # Convertir a JSON para Chart.js
        except (ValueError, Exception) as e:
            data = None
            data_json = None
    
    context = {
        'portfolios': portfolios,
        'selected_portfolio': selected_portfolio,
        'data': data,
        'data_json': data_json,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'core/portfolio_charts.html', context)
