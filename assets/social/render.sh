#!/bin/bash
# Render every asset in manifest.csv to png/ at exact pixel size via headless Chrome.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
mkdir -p "$DIR/png"
n=0
while IFS=, read -r name w h; do
  [ -z "$name" ] && continue
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --no-sandbox \
    --force-device-scale-factor=1 --window-size="$w,$h" \
    --run-all-compositor-stages-before-draw --virtual-time-budget=2500 \
    --default-background-color=00000000 \
    --screenshot="$DIR/png/$name.png" "file://$DIR/html/$name.html" >/dev/null 2>&1
  n=$((n+1))
  printf '  [%2d] %-28s %sx%s\n' "$n" "$name" "$w" "$h"
done < "$DIR/manifest.csv"
echo "rendered $n png(s) -> $DIR/png"
