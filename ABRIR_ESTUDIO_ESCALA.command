#!/bin/zsh
set -eu
PROJECT_DIR="${0:A:h}"
GODOT_BIN="${BOGOTA_GODOT_BIN:-$PROJECT_DIR/../../work/tools/Godot.app/Contents/MacOS/Godot}"
if [[ ! -x "$GODOT_BIN" ]]; then
  print 'No se encuentra Godot. Abre game/project.godot con Godot 4.7.2 o configura BOGOTA_GODOT_BIN.'
  exit 1
fi
"$GODOT_BIN" --headless --path "$PROJECT_DIR/game" --editor --import --quit
exec "$GODOT_BIN" --path "$PROJECT_DIR/game" res://scenes/scale_study.tscn
