#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Render the achromat back-reflection Blender scene as teaching movies.

Usage:
  simulations/blender/scripts/render_achromat_back_reflection.sh [--dry-run] [OUTPUT_DIR]
  simulations/blender/scripts/render_achromat_back_reflection.sh --help

Artifacts:
  OUTPUT_DIR/achromat_back_reflection.blend
  OUTPUT_DIR/frames/wide/frame_0001.png ...
  OUTPUT_DIR/frames/card_closeup/frame_0001.png ...
  OUTPUT_DIR/frames/stacked/frame_0001.png ...
  OUTPUT_DIR/achromat_back_reflection_wide.mp4
  OUTPUT_DIR/achromat_back_reflection_card_closeup.mp4
  OUTPUT_DIR/achromat_back_reflection_stacked.mp4

Environment overrides:
  BLENDER_BIN    Blender executable. Defaults to blender on PATH, then
                 /Applications/Blender.app/Contents/MacOS/Blender.
  FFMPEG_BIN     ffmpeg executable. Defaults to ffmpeg on PATH.
  FRAME_START    Optional first frame to render.
  FRAME_END      Optional last frame to render.
  FPS            Movie framerate. Defaults to 24.
  RESOLUTION_X   Render width. Defaults to the scene setting, currently 1920.
  RESOLUTION_Y   Render height. Defaults to the scene setting, currently 1080.
  CRF            H.264 quality for ffmpeg. Defaults to 18.

Examples:
  simulations/blender/scripts/render_achromat_back_reflection.sh
  FRAME_START=1 FRAME_END=24 RESOLUTION_X=960 RESOLUTION_Y=540 \
    simulations/blender/scripts/render_achromat_back_reflection.sh output/smoke
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
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi
if [[ "${1:-}" == "--dry-run" ]]; then
  dry_run=1
  shift
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../../.." && pwd)"
scene_script="$repo_root/simulations/blender/scenes/achromat_back_reflection.py"

output_dir="${1:-output/achromat_back_reflection}"
case "$output_dir" in
  /*) ;;
  *) output_dir="$PWD/$output_dir" ;;
esac

fps="${FPS:-24}"
crf="${CRF:-18}"
frame_number_start="${FRAME_START:-1}"

blend_path="$output_dir/achromat_back_reflection.blend"
wide_frame_dir="$output_dir/frames/wide"
card_frame_dir="$output_dir/frames/card_closeup"
stacked_frame_dir="$output_dir/frames/stacked"
wide_frame_prefix="$wide_frame_dir/frame_"
card_frame_prefix="$card_frame_dir/frame_"
wide_movie="$output_dir/achromat_back_reflection_wide.mp4"
card_movie="$output_dir/achromat_back_reflection_card_closeup.mp4"
stacked_movie="$output_dir/achromat_back_reflection_stacked.mp4"

if (( dry_run )); then
  blender_display="${BLENDER_BIN:-$(command -v blender || printf '/Applications/Blender.app/Contents/MacOS/Blender')}"
  ffmpeg_display="${FFMPEG_BIN:-$(command -v ffmpeg || printf 'ffmpeg')}"
  cat <<EOF
Would create:
  $blend_path
  $wide_frame_prefix
  $card_frame_prefix
  $stacked_frame_dir/frame_%04d.png
  $wide_movie
  $card_movie
  $stacked_movie

Would run:
  $blender_display --background --python $scene_script -- $blend_path
  Render Wide Setup Camera frames to $wide_frame_prefix
  Render Card Close-Up Camera frames to $card_frame_prefix
  $ffmpeg_display -filter_complex vstack=inputs=2 $stacked_frame_dir/frame_%04d.png
  $ffmpeg_display encode $wide_movie
  $ffmpeg_display encode $card_movie
  $ffmpeg_display encode $stacked_movie
EOF
  exit 0
fi

blender_bin="$(find_blender)" || die "Could not find Blender. Set BLENDER_BIN."
ffmpeg_bin="$(find_ffmpeg)" || die "Could not find ffmpeg. Set FFMPEG_BIN."
[[ -x "$blender_bin" ]] || die "Blender is not executable: $blender_bin"
[[ -x "$ffmpeg_bin" ]] || die "ffmpeg is not executable: $ffmpeg_bin"

render_expr='
import os
import bpy

scene = bpy.context.scene
scene.camera = bpy.data.objects[os.environ["CAMERA_NAME"]]

frame_start = os.environ.get("FRAME_START")
frame_end = os.environ.get("FRAME_END")
resolution_x = os.environ.get("RESOLUTION_X")
resolution_y = os.environ.get("RESOLUTION_Y")

if frame_start:
    scene.frame_start = int(frame_start)
    scene.frame_set(scene.frame_start)
if frame_end:
    scene.frame_end = int(frame_end)
if resolution_x:
    scene.render.resolution_x = int(resolution_x)
if resolution_y:
    scene.render.resolution_y = int(resolution_y)

scene.render.fps = int(os.environ["FPS"])
scene.render.filepath = os.environ["FRAME_PREFIX"]
scene.render.image_settings.file_format = "PNG"
bpy.ops.render.render(animation=True)
'

render_view() {
  local camera_name="$1"
  local frame_prefix="$2"

  printf '\n==> Rendering %s frames to %s%%04d.png\n' "$camera_name" "$frame_prefix"
  CAMERA_NAME="$camera_name" \
    FRAME_PREFIX="$frame_prefix" \
    FRAME_START="${FRAME_START:-}" \
    FRAME_END="${FRAME_END:-}" \
    FPS="$fps" \
    RESOLUTION_X="${RESOLUTION_X:-}" \
    RESOLUTION_Y="${RESOLUTION_Y:-}" \
    "$blender_bin" --background --python "$scene_script" --python-expr "$render_expr"
}

encode_movie() {
  local frame_dir="$1"
  local movie_path="$2"

  printf '\n==> Encoding %s\n' "$movie_path"
  "$ffmpeg_bin" -y \
    -framerate "$fps" \
    -start_number "$frame_number_start" \
    -i "$frame_dir/frame_%04d.png" \
    -c:v libx264 \
    -pix_fmt yuv420p \
    -crf "$crf" \
    "$movie_path"
}

printf 'Output directory: %s\n' "$output_dir"
mkdir -p "$output_dir"
rm -rf "$wide_frame_dir" "$card_frame_dir" "$stacked_frame_dir"
mkdir -p "$wide_frame_dir" "$card_frame_dir" "$stacked_frame_dir"

printf '\n==> Creating Blender scene file %s\n' "$blend_path"
"$blender_bin" --background --python "$scene_script" -- "$blend_path"

render_view "Wide Setup Camera" "$wide_frame_prefix"
render_view "Card Close-Up Camera" "$card_frame_prefix"

printf '\n==> Stacking wide and card frames\n'
"$ffmpeg_bin" -y \
  -framerate "$fps" \
  -start_number "$frame_number_start" \
  -i "$wide_frame_dir/frame_%04d.png" \
  -framerate "$fps" \
  -start_number "$frame_number_start" \
  -i "$card_frame_dir/frame_%04d.png" \
  -filter_complex "vstack=inputs=2" \
  -start_number "$frame_number_start" \
  "$stacked_frame_dir/frame_%04d.png"

encode_movie "$wide_frame_dir" "$wide_movie"
encode_movie "$card_frame_dir" "$card_movie"
encode_movie "$stacked_frame_dir" "$stacked_movie"

cat <<EOF

Done.
  Blend file:     $blend_path
  Wide movie:     $wide_movie
  Card movie:     $card_movie
  Stacked movie:  $stacked_movie
EOF
