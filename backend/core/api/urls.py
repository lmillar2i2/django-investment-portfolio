from django.urls import path
from core.api.views import PortfolioEvolutionView,PortfolioListView

urlpatterns = [
    path("portfolios/<int:pk>/evolution/", PortfolioEvolutionView.as_view()),
    path("portfolios/", PortfolioListView.as_view(), name="portfolio-list"), #Para listar GET
]
