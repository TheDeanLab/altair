from __future__ import annotations

import os
from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "simulations/blender/scripts/render_achromat_back_reflection.sh"


def test_render_script_is_executable() -> None:
    assert SCRIPT.exists()
    assert os.access(SCRIPT, os.X_OK)


def test_render_script_help_documents_artifacts_and_overrides() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--help"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    help_text = result.stdout
    for expected in (
        "achromat_back_reflection.blend",
        "achromat_back_reflection_wide.mp4",
        "achromat_back_reflection_card_closeup.mp4",
        "achromat_back_reflection_stacked.mp4",
        "BLENDER_BIN",
        "FFMPEG_BIN",
        "FRAME_START",
        "FRAME_END",
        "RESOLUTION_X",
        "RESOLUTION_Y",
    ):
        assert expected in help_text


def test_render_script_dry_run_lists_full_movie_pipeline(tmp_path: Path) -> None:
    output_dir = tmp_path / "movie"
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", str(output_dir)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    dry_run = result.stdout
    for expected in (
        str(output_dir / "achromat_back_reflection.blend"),
        str(output_dir / "frames/wide/frame_"),
        str(output_dir / "frames/card_closeup/frame_"),
        str(output_dir / "frames/stacked/frame_%04d.png"),
        str(output_dir / "achromat_back_reflection_wide.mp4"),
        str(output_dir / "achromat_back_reflection_card_closeup.mp4"),
        str(output_dir / "achromat_back_reflection_stacked.mp4"),
        "Wide Setup Camera",
        "Card Close-Up Camera",
        "vstack=inputs=2",
    ):
        assert expected in dry_run
