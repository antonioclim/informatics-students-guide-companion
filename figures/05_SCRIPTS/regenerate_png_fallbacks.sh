#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SVG_DIR="$ROOT/01_SVG_AUTHORITATIVE"
PNG_DIR="$ROOT/02_PNG_TECHNICAL_FALLBACK"
mkdir -p "$PNG_DIR"
for svg in "$SVG_DIR"/*.svg; do
  stem="$(basename "$svg" .svg)"
  inkscape "$svg" --export-type=png --export-filename="$PNG_DIR/$stem.png" --export-width=2400 --export-background='#ffffff' --export-background-opacity=255
  echo "rendered $stem"
done
