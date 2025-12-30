from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from core.models import Portfolio
from core.api.serializers import DateRangeSerializer, PortfolioListSerializer
from core.selectors import get_portfolio_weights_and_value

# Requisito 4: Endpoint API REST
# Recibe fecha_inicio y fecha_fin, retorna w_{i,t} y V_t
class PortfolioEvolutionView(APIView):
    """
    Endpoint principal de la prueba.
    Recibe un rango de fechas y retorna la evolución del portafolio.
    """
    def post(self, request, pk):
        # Validar que vengan las fechas correctamente
        serializer = DateRangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Obtener el portafolio
        portfolio = get_object_or_404(Portfolio, pk=pk)

        # Usar el selector que hace los cálculos con el ORM
        data = get_portfolio_weights_and_value(
            portfolio,
            serializer.validated_data["start_date"],
            serializer.validated_data["end_date"],
        )

        # Retornar los datos en formato JSON
        return Response({
            "portfolio": portfolio.name,
            "start_date": serializer.validated_data["start_date"].isoformat(),
            "end_date": serializer.validated_data["end_date"].isoformat(),
            "data": data,  # Contiene w_{i,t} y V_t para cada fecha
        })


class PortfolioListView(ListAPIView):
    """
    Retorna la lista de portafolios disponibles con sus IDs.
    Método: GET
    """
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioListSerializer