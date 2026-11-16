#!/bin/bash
# Dodaje MV Studio do menu aplikacji (ikona + skrot). Uruchom raz: bash launcher/install.sh
set -e
HERE="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
ICONS="$HOME/.local/share/icons/hicolor/scalable/apps"
APPS="$HOME/.local/share/applications"
mkdir -p "$ICONS" "$APPS"
chmod +x "$HERE/start.sh"
cp "$HERE/mv-studio.svg" "$ICONS/mv-studio.svg"
cat > "$APPS/mv-studio.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=MV Studio
Comment=Teledyski z ComfyUI (MiniMax H3)
Comment[en]=Music videos with ComfyUI (MiniMax H3)
Exec="$HERE/start.sh"
Icon=mv-studio
Terminal=false
Categories=AudioVideo;Video;
StartupNotify=false
DESKTOP
gtk-update-icon-cache -q -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
update-desktop-database "$APPS" 2>/dev/null || true
echo "Gotowe. Szukaj 'MV Studio' w menu aplikacji."
