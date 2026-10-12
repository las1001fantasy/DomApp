"""Lectura de ligas NBA de Fleaflicker mediante su API publica."""
import json
import re
import urllib.request

API = "https://www.fleaflicker.com/api/FetchLeagueRosters?sport=NBA&league_id={}"


def league_id_from(arg):
    """Acepta el enlace de la liga o directamente su ID."""
    match = re.search(r"leagues/(\d+)", str(arg)) or re.fullmatch(r"\d+", str(arg).strip())
    if not match:
        raise ValueError("No encuentro el ID de la liga en: %s" % arg)
    return match.group(1) if match.re.groups else match.group(0)


def fetch_rosters(league_id):
    req = urllib.request.Request(API.format(league_id), headers={"User-Agent": "DomApp/0.1"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def find_players(node):
    """Busca recursivamente todos los objetos proPlayer, sin depender de la forma exacta."""
    if isinstance(node, dict):
        if "proPlayer" in node:
            yield node["proPlayer"]
        for value in node.values():
            yield from find_players(value)
    elif isinstance(node, list):
        for item in node:
            yield from find_players(item)


def player_name(player):
    return player.get("nameFull") or player.get("nameShort") or "?"


def injury_code(player):
    """Codigo corto de la lesion (OUT, DTD, IR...) o None si esta sano."""
    injury = player.get("injury") or {}
    if not injury:
        return None
    return injury.get("typeAbbreviaition") or injury.get("typeAbbreviation") or injury.get("severity") or "?"


def injury_label(player):
    """Texto legible del estado, p. ej. 'OUT / Hamstring' o 'Sano'."""
    injury = player.get("injury") or {}
    if not injury:
        return "Sano"
    parts = [injury_code(player), injury.get("severity"), injury.get("description") or injury.get("typeFull")]
    unique = []
    for part in parts:
        if part and part not in unique:
            unique.append(part)
    return " / ".join(unique)
