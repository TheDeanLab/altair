#!/usr/bin/env bash
set -euo pipefail

PROJECT_BLENDER="/project/bioinformatics/Danuser_lab/Dean/dean/blender/blender"
FFMPEG_MODULE="${FFMPEG_MODULE:-ffmpeg/7.1}"

die() {
  printf 'Error: %s\n' "$*" >&2
  exit 1
}

load_module_command() {
  if command -v module >/dev/null 2>&1; then
    return 0
  fi
  if [[ -r /etc/profile.d/modules.sh ]]; then
    # shellcheck disable=SC1091
    source /etc/profile.d/modules.sh
  elif [[ -r /usr/share/Modules/init/bash ]]; then
    # shellcheck disable=SC1091
    source /usr/share/Modules/init/bash
  fi
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

load_module_command
command -v module >/dev/null 2>&1 || die "Could not find environment modules."
module load "$FFMPEG_MODULE"

export BLENDER_BIN="${BLENDER_BIN:-$PROJECT_BLENDER}"
export CYCLES_DEVICE="${CYCLES_DEVICE:-CUDA}"

if [[ "${1:-}" == "--dry-run" || "${2:-}" == "--dry-run" ]]; then
  printf 'Linux defaults:\n'
  printf '  BLENDER_BIN=%s\n' "$BLENDER_BIN"
  printf '  CYCLES_DEVICE=%s\n' "$CYCLES_DEVICE"
  printf '  FFMPEG_MODULE=%s\n\n' "$FFMPEG_MODULE"
fi

exec "$script_dir/render_achromat_back_reflection.sh" "$@"
