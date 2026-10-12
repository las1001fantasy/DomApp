#!/usr/bin/env python3
"""Paso 2 de DomApp: vigila los equipos de config.json y avisa de nuevas lesiones.

Cada pocos minutos lee la liga, compara el estado de cada jugador con el de la
revision anterior (guardado en estado.json) y genera un aviso cuando un jugador
de un equipo vigilado pasa de sano a lesionado (Day-to-Day, Out, IR...) o
cambia de un tipo de lesion a otro.

Uso:
    python3 vigilante.py            # se queda vigilando sin parar
    python3 vigilante.py --una-vez  # hace una sola revision y termina
"""
import json
import os
import sys
import time
from datetime import datetime

import fleaflicker

CARPETA = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(CARPETA, "config.json")
ESTADO = os.path.join(CARPETA, "estado.json")


def cargar(ruta, por_defecto):
    try:
        with open(ruta) as f:
            return json.load(f)
    except FileNotFoundError:
        return por_defecto


def guardar(ruta, datos):
    tmp = ruta + ".tmp"
    with open(tmp, "w") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)
    os.replace(tmp, ruta)


def estados_actuales(datos, equipos_vigilados):
    """Devuelve {clave_jugador: {nombre, equipo_id, codigo, texto}} de los equipos vigilados."""
    actuales = {}
    for roster in datos.get("rosters") or []:
        equipo_id = (roster.get("team") or {}).get("id")
        if equipo_id not in equipos_vigilados:
            continue
        for jugador in fleaflicker.find_players(roster):
            nombre = fleaflicker.player_name(jugador)
            clave = str(jugador.get("id") or nombre)
            actuales[clave] = {
                "nombre": nombre,
                "equipo_id": equipo_id,
                "codigo": fleaflicker.injury_code(jugador),
                "texto": fleaflicker.injury_label(jugador),
            }
    return actuales


def detectar_cambios(anteriores, actuales):
    """Avisos para jugadores que pasan a un estado de lesion nuevo.

    Un jugador que no estaba en la revision anterior (primera vez o recien
    fichado) no genera aviso: solo se guarda su estado.
    """
    avisos = []
    for clave, ahora in actuales.items():
        antes = anteriores.get(clave)
        if antes is None:
            continue
        if ahora["codigo"] and ahora["codigo"] != antes.get("codigo"):
            avisos.append(ahora)
    return avisos


def avisar(persona, jugador):
    """De momento escribe el aviso por pantalla. En el paso 3 enviara la notificacion push."""
    hora = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[{hora}] AVISO para {persona['nombre']}: {jugador['nombre']} -> {jugador['texto']}", flush=True)


def revisar(config):
    personas_por_equipo = {p["equipo_id"]: p for p in config["personas"]}
    datos = fleaflicker.fetch_rosters(config["liga"])
    actuales = estados_actuales(datos, set(personas_por_equipo))
    anteriores = cargar(ESTADO, {})

    for jugador in detectar_cambios(anteriores, actuales):
        avisar(personas_por_equipo[jugador["equipo_id"]], jugador)

    guardar(ESTADO, actuales)
    return actuales


def main():
    config = cargar(CONFIG, None)
    if not config:
        sys.exit("Falta config.json junto a vigilante.py")
    una_vez = "--una-vez" in sys.argv
    espera = int(config.get("minutos_entre_revisiones", 5)) * 60

    while True:
        try:
            actuales = revisar(config)
            lesionados = sum(1 for j in actuales.values() if j["codigo"])
            hora = datetime.now().strftime("%H:%M")
            print(f"[{hora}] Revisados {len(actuales)} jugadores, {lesionados} lesionados.", flush=True)
        except Exception as e:  # un fallo de red no debe parar el vigilante
            print(f"Error en la revision: {e}", file=sys.stderr, flush=True)
            if una_vez:
                sys.exit(1)
        if una_vez:
            break
        time.sleep(espera)


if __name__ == "__main__":
    main()
