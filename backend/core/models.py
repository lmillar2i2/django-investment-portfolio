from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

# Requisito 1: Modelar la definición del portafolio
# Estos modelos representan todos los elementos mencionados en la prueba


class Asset(models.Model):
    """
    Representa cada uno de los 17 activos invertibles.
    En la prueba: activo i donde i = 1,...,17
    """
    name = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=20, unique=True)
    
    class Meta:
        verbose_name = 'Activo'
        verbose_name_plural = 'Activos'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.symbol})"


class Portfolio(models.Model):
    """
    Representa un portafolio de inversión con su valor inicial V_0.
    Cada portafolio tiene un valor inicial y fecha de inicio.
    """
    name = models.CharField(max_length=100, unique=True)
    initial_value = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Valor inicial del portafolio (V_0)"
    )  # V_0 del requerimiento
    start_date = models.DateField(help_text="Fecha inicial (t=0)")  # t=0, en este caso 15/02/22
    
    class Meta:
        verbose_name = 'Portafolio'
        verbose_name_plural = 'Portafolios'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Price(models.Model):
    """
    Almacena los precios históricos p_{i,t} de cada activo.
    Cada fila es un precio en una fecha específica.
    """
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name="prices"
    )
    date = models.DateField()
    price = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("0.000001"))]
    )  # p_{i,t}

    class Meta:
        unique_together = ("asset", "date")
        ordering = ["date"]

    def __str__(self):
        return f"{self.asset.symbol} - {self.date}: {self.price}"


class Weight(models.Model):
    """
    Almacena los pesos estratégicos w_{i,t} definidos en el Excel.
    Estos son los pesos iniciales que vienen de la hoja "Weights".
    """
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="weights"
    )
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE
    )
    date = models.DateField()
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        validators=[
            MinValueValidator(Decimal("0")),
            MaxValueValidator(Decimal("1"))
        ]
    )  # w_{i,t} del requerimiento

    class Meta:
        unique_together = ("portfolio", "asset", "date")

    def __str__(self):
        return (
            f"{self.portfolio.name} - {self.asset.symbol} "
            f"({self.date}): {self.weight}"
        )


class Position(models.Model):
    """
    Representa la posición real del portafolio en cada fecha.
    Guarda c_{i,t} (cantidad) y x_{i,t} (valor en dólares).
    Cumple: x_{i,t} = p_{i,t} * c_{i,t}
    """
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="positions"
    )
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE
    )
    date = models.DateField()
    quantity = models.DecimalField(
        max_digits=25,
        decimal_places=10,
        validators=[MinValueValidator(Decimal("0"))]
    )  # c_{i,t}
    value_at_date = models.DecimalField(
        max_digits=25,
        decimal_places=4,
        validators=[MinValueValidator(Decimal("0"))]
    )  # x_{i,t}

    class Meta:
        unique_together = ("portfolio", "asset", "date")
        ordering = ["date"]

    def __str__(self):
        return (
            f"{self.portfolio.name} - {self.asset.symbol} "
            f"@ {self.date}"
        )
