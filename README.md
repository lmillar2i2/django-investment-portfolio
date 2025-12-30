# Portafolio de Inversión - Django

Sistema para modelar y analizar portafolios de inversión. Permite cargar datos desde Excel, calcular posiciones históricas y visualizar la evolución de pesos y valores del portafolio.

## Requisitos

- Docker y Docker Compose
- WSL2 (si estás en Windows)
- Archivo Excel `datos.xlsx` con las hojas "Weights" y "Precios"

## Setup

### 1. Variables de entorno

Crea un archivo `.env` en la raíz del proyecto con:

```env
POSTGRES_DB=portfolio_db
POSTGRES_USER=portfolio_user
POSTGRES_PASSWORD=portfolio_pass
POSTGRES_HOST=db
POSTGRES_PORT=5432
SECRET_KEY=dev-secret-key
DEBUG=1
```

### 2. Construir y levantar contenedores

```bash
docker-compose up --build
```

Esto levanta:
- PostgreSQL en el puerto 5433
- Django en el puerto 8000

### 3. Migraciones

En otra terminal (o después de que los contenedores estén corriendo):

```bash
docker-compose exec web python manage.py migrate
```

### 4. Cargar datos

Tienes dos opciones:

**Opción A: Desde la web desde el template (recomendado)**
1. Abre http://localhost:8000
2. Sube el archivo "datos.xlsx" usando el formulario
3. Espera el mensaje de confirmación

**Opción B: Desde comando**
```bash
docker-compose exec web python manage.py load_excel /app/datos.xlsx

```

## Uso

### Web Interface

1. Ve a http://localhost:8000
2. **Cargar Excel**: Sube el archivo `datos.xlsx` para procesar los datos
3. **Ver gráficos**: Selecciona un portafolio y rango de fechas para ver:
   - Evolución del valor total (V_t) - gráfico de línea
   - Evolución de pesos por activo (w_{i,t}) - gráfico stacked area

### API REST

#### Endpoint principal


### 1. Listar Portafolios Disponibles
Obtiene una lista de todos los portafolios con su ID y nombre. Útil para identificar qué `<id>` usar en la consulta de evolución.

* **URL:** `/api/portfolios/`
* **Método:** `GET`

**Ejemplo de Respuesta:**
```json
[
  {
    "id": 1,
    "name": "Portfolio Conservative"
  },
  {
    "id": 2,
    "name": "Portfolio Risky"
  }
]


```bash
### 2. Consultar Evolución de Portafolio
Este endpoint encapsula la lógica principal del sistema: permite consultar la evolución temporal del valor total del portafolio y la composición por activo en un rango de fechas.

**Endpoint:** POST /api/portfolios/<id>/evolution/
Content-Type: application/json
**Body (JSON):**
{
  "start_date": "2022-02-15",
  "end_date": "2023-02-16"
}
**Ejemplo de Uso (CURL)**
curl -X POST http://localhost:8000/api/portfolios/1/evolution/ \
-H "Content-Type: application/json" \
-d '{
    "start_date": "2022-02-15",
    "end_date": "2023-02-15"
}'
```



**Respuesta:**
```json
{
  "portfolio": "Portfolio 1",
  "start_date": "2022-02-15",
  "end_date": "2023-02-16",
  "data": [
    {
      "date": "2022-02-15",
      "total_value": 1000000000.0,
      "weights": [
        {"asset": "AAPL", "weight": 0.15},
        {"asset": "MSFT", "weight": 0.12},
        ...
      ]
    },
    ...
  ]
}
```

## Estructura del Proyecto

```
backend/
  core/
    models.py          # Modelos: Asset, Portfolio, Price, Weight, Position
    services.py        # Lógica de negocio: ETL, cálculos de posiciones
    selectors.py       # Consultas: obtener w_{i,t} y V_t
    api/
      views.py         # Endpoint REST principal
      serializers.py   # Validación de datos
    views.py           # Vista web con gráficos
    templates/
      core/
        portfolio_charts.html  # Template con Chart.js
    management/
      commands/
        load_excel.py  # Comando para cargar Excel
```

## Modelos

- **Asset**: Los 17 activos invertibles
- **Portfolio**: Portafolios con valor inicial V_0
- **Price**: Precios históricos p_{i,t}
- **Weight**: Pesos estratégicos w_{i,t} del Excel
- **Position**: Posiciones reales con cantidades c_{i,t} y valores x_{i,t}

## Funcionalidades Implementadas

**Requisito 1**: Modelos Django para todos los elementos del portafolio  
**Requisito 2**: Función ETL que carga datos del Excel  
**Requisito 3**: Cálculo de cantidades iniciales c_{i,0} = (w_{i,0} * V_0) / p_{i,0}  
**Requisito 4**: Endpoint API REST que retorna w_{i,t} y V_t usando ORM de Django 
** Endpoint API REST que lista portafolios
**Bonus 1**: Vista web con gráficos interactivos usando Chart.js
**Bonus **: Estructura siguiendo buenas prácticas de Django

## Notas Técnicas

- Usa `Decimal` para todos los cálculos financieros (precisión)
- Transacciones atómicas para garantizar consistencia de datos
- ORM de Django para todas las consultas (como se pidió)
- Separación de responsabilidades: services (lógica), selectors (consultas), views (presentación)

## Comandos Útiles

```bash
# Ver logs
docker-compose logs -f web

# Acceder al shell de Django
docker-compose exec web python manage.py shell

# Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Reiniciar contenedores
docker-compose restart
```

## Troubleshooting

**Error de conexión a la base de datos:**
- Verifica que el contenedor `db` esté corriendo: `docker-compose ps`
- Revisa las variables de entorno en `.env`

**Error al cargar Excel:**
- Verifica que el archivo tenga las hojas "weights" y "Precios"
- Revisa los logs: `docker-compose logs web`

**Puerto 8000 ocupado:**
- Cambia el puerto en `docker-compose.yml`

## Desarrollo
- Debug mode activado
- Volúmenes montados para editar código sin reconstruir



## Comentarios finales

Este proyecto fue desarrollado priorizando claridad, consistencia de datos y separación de responsabilidades.
La lógica financiera se encuentra desacoplada de la capa de presentación, lo que permite reutilizarla tanto desde la API como desde la interfaz web.

El objetivo principal fue construir una solución simple, correcta y fácil de revisar, más que optimizar para datos masivos.