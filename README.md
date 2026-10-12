# DomApp

Avisos push al móvil cuando un jugador de tus ligas NBA de Fleaflicker pasa de sano a Day-to-Day, Out o IR.

## Plan

1. **Comprobar Fleaflicker**: leer una liga y ver el estado de cada jugador (`paso1_estados.py`).
2. **El vigilante**: revisar las plantillas cada pocos minutos y detectar cambios de estado.
3. **Notificaciones**: avisos push con la app ntfy (Android e iPhone).
4. **Puesta en marcha**: cada persona en un archivo de configuración, funcionando 24/7 en una VM de Google Cloud.

## Paso 1

Solo necesita Python 3, sin dependencias:

```
python3 paso1_estados.py https://www.fleaflicker.com/nba/leagues/30332
```

Muestra cada equipo con sus jugadores y su estado, y guarda la respuesta completa en `liga_<id>.json`.
