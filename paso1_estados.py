#!/usr/bin/env python3
"""Paso 1 de DomApp: lee una liga NBA de Fleaflicker y muestra el estado de cada jugador.

Uso:
    python3 paso1_estados.py https://www.fleaflicker.com/nba/leagues/12345
    python3 paso1_estados.py 12345

Solo usa la libreria estandar de Python 3. Guarda la respuesta completa en
liga_<id>.json para revisar la estructura de los datos.
"""
import json
import sys

import fleaflicker


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    try:
        league_id = fleaflicker.league_id_from(sys.argv[1])
    except ValueError as e:
        sys.exit(str(e))
    data = fleaflicker.fetch_rosters(league_id)

    with open(f"liga_{league_id}.json", "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    rosters = data.get("rosters") or []
    if not rosters:
        print("La respuesta no trae 'rosters'. Revisa liga_%s.json" % league_id)
    for roster in rosters:
        team = roster.get("team") or {}
        print(f"\n== {team.get('name', 'Equipo sin nombre')} (id {team.get('id', '?')}) ==")
        for player in fleaflicker.find_players(roster):
            print(f"  {fleaflicker.player_name(player):<28} {fleaflicker.injury_label(player)}")


if __name__ == "__main__":
    main()
