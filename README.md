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

Muestra cada equipo (con su id) y el estado de sus jugadores, y guarda la respuesta completa en `liga_<id>.json`.

## Paso 2: el vigilante

En `config.json` van la liga, cada cuántos minutos revisar y qué equipo vigila cada persona (por su id, que sale en el paso 1).

```
python3 vigilante.py --una-vez   # una sola revisión, para probar
python3 vigilante.py             # se queda vigilando sin parar
```

La primera revisión solo guarda el estado de cada jugador en `estado.json`. A partir de ahí escribe un aviso cuando un jugador de un equipo vigilado pasa de sano a lesionado (DTD, OUT, IR...) o cambia de un tipo de lesión a otro. Las recuperaciones y los fichajes nuevos no generan aviso. En el paso 3 esos avisos se convertirán en notificaciones push.
