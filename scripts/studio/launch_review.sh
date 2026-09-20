#!/usr/bin/env bash
set -euo pipefail
runtime="$HOME/.local/share/lazyedit-studio/review"
mkdir -p "$runtime"
# One project-owned desktop. Reuse the live endpoint.
if curl -fsS --max-time 2 http://127.0.0.1:9496/json/version >/dev/null 2>&1; then
 echo 'Studio review is already running: http://127.0.0.1:6296/vnc.html?autoconnect=1&resize=scale&shared=0'
 exit 0
fi
for port in 9496 6296 6096; do
 if ss -ltnH | awk '{print $4}' | grep -q ":$port$"; then echo "Port $port already owned; refusing a collision" >&2;exit 1;fi
done
export DISPLAY=:196
Xvfb :196 -screen 0 1440x1000x24 -nolisten tcp >"$runtime/xvfb.log" 2>&1 & echo $! >"$runtime/xvfb.pid"
sleep 1
x11vnc -display :196 -rfbport 6096 -localhost -nopw -nevershared -forever >"$runtime/vnc.log" 2>&1 & echo $! >"$runtime/vnc.pid"
websockify --web /usr/share/novnc 127.0.0.1:6296 127.0.0.1:6096 >"$runtime/novnc.log" 2>&1 & echo $! >"$runtime/novnc.pid"
google-chrome --user-data-dir="$runtime/chrome" --remote-debugging-address=127.0.0.1 --remote-debugging-port=9496 --no-first-run --disable-session-crashed-bubble --window-size=1440,1000 --window-position=0,0 https://edit.lazying.art >"$runtime/chrome.log" 2>&1 & echo $! >"$runtime/chrome.pid"
while kill -0 "$(cat "$runtime/chrome.pid")" 2>/dev/null; do
 for win in $(xdotool search --onlyvisible --class Google-chrome 2>/dev/null || true); do xdotool windowmove "$win" 0 0 windowsize "$win" 1440 1000 2>/dev/null || true;done
 sleep 5
done
