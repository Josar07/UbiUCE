# Backend de Navegación del Campus

Este es el servidor Flask que procesa archivos OSM y calcula rutas para la aplicación Android.

## Instalación

1. Instalar Python 3.8 o superior
2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Configuración

1. Coloca tu archivo OSM del campus en el directorio `backend/` con el nombre `campus.osm`
2. O usa el endpoint `/load-osm` para cargar un archivo específico

## Ejecución

```bash
python app.py
```

El servidor se ejecutará en `http://localhost:5000`

## Endpoints

### POST /load-osm
Carga un archivo OSM específico:
```json
{
    "osm_file_path": "/ruta/al/archivo.osm"
}
```

### POST /calculate-route
Calcula la ruta entre dos puntos:
```json
{
    "startPoint": {
        "latitude": -0.1807,
        "longitude": -78.4678
    },
    "endPoint": {
        "latitude": -0.1808,
        "longitude": -78.4679
    },
    "algorithm": "dijkstra"
}
```

### GET /graph-info
Obtiene información sobre el grafo cargado.

### GET /health
Verifica el estado del servidor.

## Algoritmos

- **Dijkstra**: Algoritmo clásico de camino más corto
- **A***: Algoritmo A* con heurística de distancia euclidiana

## Estructura del Proyecto

```
backend/
├── app.py              # Servidor Flask principal
├── requirements.txt    # Dependencias de Python
├── README.md          # Este archivo
└── campus.osm         # Archivo OSM del campus (agregar manualmente)
``` 