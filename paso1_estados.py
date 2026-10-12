#!/usr/bin/env python3
"""Paso 1 de DomApp: lee una liga NBA de Fleaflicker y muestra el estado de cada jugador.

Uso:
    python3 paso1_estados.py https://www.fleaflicker.com/nba/leagues/12345
    python3 paso1_estados.py 12345

Solo usa la libreria estandar de Python 3. Guarda la respuesta completa en
liga_<id>.json para revisar la estructura de los datos.
"""
import json
import re
import sys
import urllib.request

API = "https://www.fleaflicker.com/api/FetchLeagueRosters?sport=NBA&league_id={}"


def league_id_from(arg):
    match = re.search(r"leagues/(\d+)", arg) or re.fullmatch(r"\d+", arg.strip())
    if not match:
        sys.exit("No encuentro el ID de la liga en: " + arg)
    return match.group(1) if match.re.groups else match.group(0)


def fetch(league_id):
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


def status_of(player):
    injury = player.get("injury") or {}
    if not injury:
        return "Sano"
    abbr = injury.get("typeAbbreviaition") or injury.get("typeAbbreviation") or "?"
    detail = injury.get("description") or injury.get("typeFull") or ""
    severity = injury.get("severity") or ""
    return " / ".join(x for x in (abbr, severity, detail) if x)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    league_id = league_id_from(sys.argv[1])
    data = fetch(league_id)

    with open(f"liga_{league_id}.json", "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    rosters = data.get("rosters") or []
    if not rosters:
        print("La respuesta no trae 'rosters'. Revisa liga_%s.json" % league_id)
    for roster in rosters:
        team = (roster.get("team") or {}).get("name", "Equipo sin nombre")
        print(f"\n== {team} ==")
        for player in find_players(roster):
            name = player.get("nameFull") or player.get("nameShort") or "?"
            print(f"  {name:<28} {status_of(player)}")


if __name__ == "__main__":
    main()
