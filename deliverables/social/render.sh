#!/usr/bin/env bash
# Render Showmax Global launch post graphics (SHO-14) to PNG via headless Chrome.
# Reads manifest.txt (name w h). Run from deliverables/social/.
set -euo pipefail
cd "$(dirname "$0")"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
mkdir -p out
n=0
while read -r name w h; do
  [ -z "$name" ] && continue
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars \
    --allow-file-access-from-files --virtual-time-budget=3000 \
    --default-background-color=00000000 \
    --window-size="${w},${h}" --force-device-scale-factor=2 \
    --screenshot="out/${name}.png" "src/${name}.html" >/dev/null 2>&1
  n=$((n+1))
done < manifest.txt
echo "Rendered $n PNGs to out/ (2x = sharper)."
