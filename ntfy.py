"""Envio de notificaciones push con ntfy (https://ntfy.sh)."""
import json
import os
import secrets
import urllib.request

SERVIDOR = "https://ntfy.sh"


def cargar_canales(ruta, personas):
    """Lee canales.json y crea un canal secreto para cada persona que no lo tenga.

    Los canales de ntfy son publicos para quien conozca el nombre, por eso se
    generan al azar y se guardan solo en la VM (canales.json no se sube a GitHub).
    """
    try:
        with open(ruta) as f:
            canales = json.load(f)
    except FileNotFoundError:
        canales = {}
    nuevos = False
    for persona in personas:
        if persona not in canales:
            canales[persona] = "domapp-%s-%s" % (persona.lower().replace(" ", ""), secrets.token_hex(6))
            nuevos = True
    if nuevos:
        with open(ruta, "w") as f:
            json.dump(canales, f, indent=2, ensure_ascii=False)
        os.chmod(ruta, 0o600)
    return canales


def enviar(canal, titulo, mensaje, prioridad=4, etiquetas=("basketball",)):
    """Publica un mensaje en un canal. Usa JSON para que los acentos lleguen bien."""
    cuerpo = json.dumps({
        "topic": canal,
        "title": titulo,
        "message": mensaje,
        "priority": prioridad,
        "tags": list(etiquetas),
    }).encode("utf-8")
    req = urllib.request.Request(SERVIDOR, data=cuerpo, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        resp.read()
