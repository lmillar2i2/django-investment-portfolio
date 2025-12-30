from rest_framework import serializers
from core.models import Portfolio

class DateRangeSerializer(serializers.Serializer):
    """
    Validador para el payload del endpoint de evolución.
    No usamos ModelSerializer porque estos datos no se guardan, 
    solo sirven como input para el cálculo del servicio.
    """
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    
#Serializador para listar portafolios    
class PortfolioListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ['id', 'name']  