#!/usr/bin/env bash
# Paso 4 de DomApp: instala el vigilante como servicio para que funcione 24/7.
# Arranca solo al encender la VM, se reinicia si falla y guarda un registro.
#
# Uso (desde la carpeta DomApp, con tu usuario normal):
#     bash instalar_servicio.sh
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
USUARIO="${SUDO_USER:-$(id -un)}"
PY="$(command -v python3)"

sudo tee /etc/systemd/system/domapp.service >/dev/null <<EOF
[Unit]
Description=DomApp: avisos de lesiones de Fleaflicker
After=network-online.target
Wants=network-online.target

[Service]
User=$USUARIO
WorkingDirectory=$DIR
ExecStart=$PY $DIR/vigilante.py
Restart=always
RestartSec=30
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now domapp
sleep 3
systemctl status domapp --no-pager --lines=5 || true
echo
echo "Listo. DomApp queda vigilando 24/7."
echo "Ver el registro en directo:  journalctl -u domapp -f"
echo "Reiniciar tras un git pull:  sudo systemctl restart domapp"
