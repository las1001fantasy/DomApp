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

## Paso 2 y 3: el vigilante con avisos al móvil

En `config.json` van cada cuántos minutos revisar y las ligas, cada una con su nombre (el que saldrá en el aviso) y qué equipo vigila cada persona (por su id, que sale en el paso 1). Para añadir otra liga basta con añadir otro bloque a la lista `ligas`.

```
python3 vigilante.py --canales   # muestra el canal de ntfy de cada persona
python3 vigilante.py --prueba    # envía un aviso de prueba a cada persona
python3 vigilante.py --una-vez   # una sola revisión
python3 vigilante.py             # se queda vigilando sin parar
```

La primera vez se crea `canales.json` con un canal secreto de ntfy para cada persona. No se sube a GitHub, porque en ntfy cualquiera que conozca el nombre del canal puede leerlo. Cada persona instala la app **ntfy** (Android o iPhone), pulsa **+** y se suscribe a su canal.

La primera revisión solo guarda el estado de cada jugador en `estado.json`. A partir de ahí, cuando un jugador de un equipo vigilado pasa de sano a lesionado (DTD, OUT, IR...) o cambia de un tipo de lesión a otro, su dueño recibe una notificación con el jugador, el estado, la liga, el equipo y la lesión. Las recuperaciones y los fichajes nuevos no generan aviso.

## Paso 4: funcionando 24/7

En la VM, desde la carpeta DomApp y con tu usuario normal:

```
bash instalar_servicio.sh
```

Instala el vigilante como servicio del sistema: arranca solo al encender la VM, se reinicia si falla y guarda un registro.

```
journalctl -u domapp -f            # ver el registro en directo (Ctrl+C para salir)
systemctl status domapp            # ver si está funcionando
sudo systemctl restart domapp      # aplicar cambios después de un git pull o de editar config.json
```
