#!/usr/bin/env python3
"""DomApp: vigila los equipos de config.json y avisa al movil de nuevas lesiones.

Cada pocos minutos lee cada liga, compara el estado de cada jugador con el de la
revision anterior (guardado en estado.json) y envia una notificacion push cuando
un jugador de un equipo vigilado pasa de sano a lesionado (Day-to-Day, Out,
IR...) o cambia de un tipo de lesion a otro.

Uso:
    python3 vigilante.py            # se queda vigilando sin parar
    python3 vigilante.py --una-vez  # hace una sola revision y termina
    python3 vigilante.py --canales  # muestra el canal de ntfy de cada persona
    python3 vigilante.py --prueba   # envia un aviso de prueba a cada persona
"""
import json
import os
import sys
import time
from datetime import datetime

import fleaflicker
import ntfy

CARPETA = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(CARPETA, "config.json")
ESTADO = os.path.join(CARPETA, "estado.json")
CANALES = os.path.join(CARPETA, "canales.json")


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


def personas_de(config):
    return sorted({e["persona"] for liga in config["ligas"] for e in liga["equipos"]})


def estados_actuales(datos, liga):
    """Devuelve {clave: info del jugador} para los equipos vigilados de una liga.

    La clave incluye la liga, porque un mismo jugador puede estar en varias.
    """
    persona_por_equipo = {e["equipo_id"]: e["persona"] for e in liga["equipos"]}
    actuales = {}
    for roster in datos.get("rosters") or []:
        equipo = roster.get("team") or {}
        persona = persona_por_equipo.get(equipo.get("id"))
        if persona is None:
            continue
        for jugador in fleaflicker.find_players(roster):
            nombre = fleaflicker.player_name(jugador)
            clave = "%s:%s" % (liga["id"], jugador.get("id") or nombre)
            actuales[clave] = {
                "nombre": nombre,
                "persona": persona,
                "liga": liga.get("nombre") or "Liga %s" % liga["id"],
                "equipo": equipo.get("name", ""),
                "codigo": fleaflicker.injury_code(jugador),
                "texto": fleaflicker.injury_label(jugador),
                "detalle": (jugador.get("injury") or {}).get("description", ""),
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


def avisar(canales, jugador):
    """Escribe el aviso por pantalla y lo envia al movil de su persona."""
    hora = datetime.now().strftime("%Y-%m-%d %H:%M")
    titulo = "%s: %s" % (jugador["nombre"], jugador["codigo"])
    lineas = ["Liga: %s" % jugador["liga"], "Equipo: %s" % jugador["equipo"]]
    if jugador["detalle"]:
        lineas.append("Lesión: %s" % jugador["detalle"])
    print(f"[{hora}] AVISO para {jugador['persona']}: {jugador['nombre']} -> {jugador['texto']} ({jugador['liga']})", flush=True)
    try:
        ntfy.enviar(canales[jugador["persona"]], titulo, "\n".join(lineas))
    except Exception as e:
        print(f"  No se pudo enviar la notificacion: {e}", file=sys.stderr, flush=True)


def revisar(config, canales):
    anteriores = cargar(ESTADO, {})
    actuales = {}
    for liga in config["ligas"]:
        try:
            datos = fleaflicker.fetch_rosters(liga["id"])
        except Exception as e:
            # si una liga falla, conservamos su estado anterior y seguimos con las demas
            print(f"Error leyendo la liga {liga['id']}: {e}", file=sys.stderr, flush=True)
            prefijo = "%s:" % liga["id"]
            actuales.update({k: v for k, v in anteriores.items() if k.startswith(prefijo)})
            continue
        actuales.update(estados_actuales(datos, liga))

    for jugador in detectar_cambios(anteriores, actuales):
        avisar(canales, jugador)

    guardar(ESTADO, actuales)
    return actuales


def mostrar_canales(canales):
    print("Cada persona instala la app ntfy y se suscribe a su canal:")
    for persona, canal in canales.items():
        print(f"  {persona:<10} {canal}")


def enviar_prueba(canales):
    for persona, canal in canales.items():
        ntfy.enviar(canal, "DomApp funciona", "Hola %s, así te llegarán los avisos de lesiones." % persona)
        print(f"Aviso de prueba enviado a {persona} ({canal})")


def main():
    config = cargar(CONFIG, None)
    if not config:
        sys.exit("Falta config.json junto a vigilante.py")
    canales = ntfy.cargar_canales(CANALES, personas_de(config))

    if "--canales" in sys.argv:
        return mostrar_canales(canales)
    if "--prueba" in sys.argv:
        return enviar_prueba(canales)

    una_vez = "--una-vez" in sys.argv
    espera = int(config.get("minutos_entre_revisiones", 5)) * 60
    while True:
        try:
            actuales = revisar(config, canales)
            lesionados = sum(1 for j in actuales.values() if j["codigo"])
            hora = datetime.now().strftime("%H:%M")
            print(f"[{hora}] Revisados {len(actuales)} jugadores, {lesionados} lesionados.", flush=True)
        except Exception as e:  # un fallo inesperado no debe parar el vigilante
            print(f"Error en la revision: {e}", file=sys.stderr, flush=True)
            if una_vez:
                sys.exit(1)
        if una_vez:
            break
        time.sleep(espera)


if __name__ == "__main__":
    main()
