#!/bin/bash
# Uruchamia MV Studio (jesli jeszcze nie dziala) i otwiera je w przegladarce.
DIR="$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)"
PORT="${MV_STUDIO_PORT:-8777}"
URL="http://127.0.0.1:$PORT"
LOG="${XDG_CACHE_HOME:-$HOME/.cache}/mv-studio.log"

up() { python3 -c "import urllib.request,sys; urllib.request.urlopen('$URL/api/projects', timeout=1)" 2>/dev/null; }

if ! up; then
    mkdir -p "$(dirname "$LOG")"
    cd "$DIR" && setsid nohup python3 server.py "$PORT" >>"$LOG" 2>&1 &
    for _ in $(seq 1 40); do up && break; sleep 0.25; done
fi

if up; then
    xdg-open "$URL"
else
    command -v notify-send >/dev/null && notify-send -i mv-studio "MV Studio" "Nie udalo sie uruchomic. Zobacz $LOG"
    exit 1
fi
