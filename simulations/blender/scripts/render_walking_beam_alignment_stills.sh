#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Render one-frame PNG stills for the walking-beam alignment scene.

Usage:
  simulations/blender/scripts/render_walking_beam_alignment_stills.sh [--draft|--preview|--final] [--frame N] [--dry-run] [OUTPUT_DIR]
  simulations/blender/scripts/render_walking_beam_alignment_stills.sh --help

Artifacts:
  OUTPUT_DIR/walking_beam_alignment.blend
  OUTPUT_DIR/wide.png
  OUTPUT_DIR/iris_closeup.png
  OUTPUT_DIR/hero.png
  OUTPUT_DIR/stacked.png

Environment overrides:
  BLENDER_BIN    Blender executable. Defaults to blender on PATH, then
                 /Applications/Blender.app/Contents/MacOS/Blender.
  FFMPEG_BIN     ffmpeg executable. Defaults to ffmpeg on PATH.
  RENDER_MODE    Render preset: draft, preview, or final. Defaults to preview.
  FRAME          Timeline frame to render. Defaults to 168.
  RESOLUTION_X   Render width. Defaults to 1280.
  RESOLUTION_Y   Render height. Defaults to 720.
EOF
}

die() {
  printf 'Error: %s\n' "$*" >&2
  exit 1
}

find_blender() {
  if [[ -n "${BLENDER_BIN:-}" ]]; then
    printf '%s\n' "$BLENDER_BIN"
    return 0
  fi
  if command -v blender >/dev/null 2>&1; then
    command -v blender
    return 0
  fi
  local mac_blender="/Applications/Blender.app/Contents/MacOS/Blender"
  if [[ -x "$mac_blender" ]]; then
    printf '%s\n' "$mac_blender"
    return 0
  fi
  return 1
}

find_ffmpeg() {
  if [[ -n "${FFMPEG_BIN:-}" ]]; then
    printf '%s\n' "$FFMPEG_BIN"
    return 0
  fi
  command -v ffmpeg
}

dry_run=0
render_mode="${RENDER_MODE:-preview}"
frame="${FRAME:-168}"
output_dir=""

while (($#)); do
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    --dry-run)
      dry_run=1
      ;;
    --draft)
      render_mode="draft"
      ;;
    --preview)
      render_mode="preview"
      ;;
    --final)
      render_mode="final"
      ;;
    --frame)
      shift
      (($#)) || die "--frame requires a frame number."
      frame="$1"
      ;;
    -*)
      die "Unknown option: $1"
      ;;
    *)
      if [[ -n "$output_dir" ]]; then
        die "Expected one output directory, got both '$output_dir' and '$1'."
      fi
      output_dir="$1"
      ;;
  esac
  shift
done

case "$render_mode" in
  draft|preview|final) ;;
  *) die "RENDER_MODE must be 'draft', 'preview', or 'final', got '$render_mode'." ;;
esac
[[ "$frame" =~ ^[0-9]+$ ]] || die "Frame must be an integer, got '$frame'."

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../../.." && pwd)"
scene_script="$repo_root/simulations/blender/scenes/walking_beam_alignment.py"

output_dir="${output_dir:-output/walking_beam_alignment_stills}"
case "$output_dir" in
  /*) ;;
  *) output_dir="$PWD/$output_dir" ;;
esac

resolution_x="${RESOLUTION_X:-1280}"
resolution_y="${RESOLUTION_Y:-720}"
blend_path="$output_dir/walking_beam_alignment.blend"
wide_png="$output_dir/wide.png"
iris_png="$output_dir/iris_closeup.png"
hero_png="$output_dir/hero.png"
stacked_png="$output_dir/stacked.png"

if (( dry_run )); then
  blender_display="${BLENDER_BIN:-$(command -v blender || printf '/Applications/Blender.app/Contents/MacOS/Blender')}"
  ffmpeg_display="${FFMPEG_BIN:-$(command -v ffmpeg || printf 'ffmpeg')}"
  cat <<EOF
Would create:
  Render mode: $render_mode
  Frame: $frame
  Resolution: ${resolution_x}x${resolution_y}
  $blend_path
  $wide_png
  $iris_png
  $hero_png
  $stacked_png

Would run:
  RENDER_MODE=$render_mode $blender_display --background --python $scene_script -- $blend_path
  Render Wide Setup Camera still to $wide_png
  Render Iris Close-Up Camera still to $iris_png
  Render Hero Camera still to $hero_png
  $ffmpeg_display -filter_complex vstack=inputs=2 $stacked_png
EOF
  exit 0
fi

blender_bin="$(find_blender)" || die "Could not find Blender. Set BLENDER_BIN."
ffmpeg_bin="$(find_ffmpeg)" || die "Could not find ffmpeg. Set FFMPEG_BIN."
[[ -x "$blender_bin" ]] || die "Blender is not executable: $blender_bin"
[[ -x "$ffmpeg_bin" ]] || die "ffmpeg is not executable: $ffmpeg_bin"

mkdir -p "$output_dir"

printf 'Output directory: %s\n' "$output_dir"
printf 'Render mode: %s\n' "$render_mode"
printf 'Frame: %s\n' "$frame"
printf 'Resolution: %sx%s\n' "$resolution_x" "$resolution_y"

printf '\n==> Creating Blender scene file %s\n' "$blend_path"
RENDER_MODE="$render_mode" "$blender_bin" --background --python "$scene_script" -- "$blend_path"

render_expr='
import os
import sys
import bpy

repo_root = os.environ["REPO_ROOT"]
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from simulations.blender.altair_blender.scene import apply_render_preset

scene = bpy.context.scene
apply_render_preset(os.environ["RENDER_MODE"])
scene.frame_set(int(os.environ["FRAME"]))
scene.render.resolution_x = int(os.environ["RESOLUTION_X"])
scene.render.resolution_y = int(os.environ["RESOLUTION_Y"])
scene.render.image_settings.file_format = "PNG"

for camera_name, output_path in (
    ("Wide Setup Camera", os.environ["WIDE_PNG"]),
    ("Iris Close-Up Camera", os.environ["IRIS_PNG"]),
    ("Hero Camera", os.environ["HERO_PNG"]),
):
    scene.camera = bpy.data.objects[camera_name]
    scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)
'

printf '\n==> Rendering still perspectives\n'
REPO_ROOT="$repo_root" \
  RENDER_MODE="$render_mode" \
  FRAME="$frame" \
  RESOLUTION_X="$resolution_x" \
  RESOLUTION_Y="$resolution_y" \
  WIDE_PNG="$wide_png" \
  IRIS_PNG="$iris_png" \
  HERO_PNG="$hero_png" \
  "$blender_bin" --background "$blend_path" --python-expr "$render_expr"

printf '\n==> Stacking wide and iris close-up stills\n'
"$ffmpeg_bin" -y \
  -i "$wide_png" \
  -i "$iris_png" \
  -filter_complex "vstack=inputs=2" \
  -frames:v 1 \
  -update 1 \
  "$stacked_png"

cat <<EOF

Done.
  Wide still:        $wide_png
  Iris close-up:    $iris_png
  Hero still:       $hero_png
  Stacked still:    $stacked_png
EOF
