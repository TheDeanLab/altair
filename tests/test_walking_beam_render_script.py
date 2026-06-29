from __future__ import annotations

import os
from pathlib import Path
import subprocess

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "simulations/blender/scripts/render_walking_beam_alignment.sh"
LINUX_SCRIPT = (
    REPO_ROOT / "simulations/blender/scripts/render_walking_beam_alignment_linux.sh"
)
STILL_SCRIPT = (
    REPO_ROOT / "simulations/blender/scripts/render_walking_beam_alignment_stills.sh"
)
PROJECT_BLENDER = "/project/bioinformatics/Danuser_lab/Dean/dean/blender/blender"


def test_render_script_is_executable() -> None:
    assert SCRIPT.exists()
    assert os.access(SCRIPT, os.X_OK)


def test_linux_render_script_is_executable() -> None:
    assert LINUX_SCRIPT.exists()
    assert os.access(LINUX_SCRIPT, os.X_OK)


def test_still_render_script_is_executable() -> None:
    assert STILL_SCRIPT.exists()
    assert os.access(STILL_SCRIPT, os.X_OK)


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
        "walking_beam_alignment.blend",
        "walking_beam_alignment_wide.mp4",
        "walking_beam_alignment_iris_closeup.mp4",
        "walking_beam_alignment_stacked.mp4",
        "walking_beam_alignment_hero.mp4",
        "walking_beam_alignment_draft_iris_closeup.mp4",
        "--draft",
        "--preview",
        "--final",
        "BLENDER_BIN",
        "FFMPEG_BIN",
        "CYCLES_DEVICE",
        "RENDER_MODE",
        "FRAME_START",
        "FRAME_END",
        "FRAME_STEP",
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
        str(output_dir / "walking_beam_alignment.blend"),
        str(output_dir / "frames/wide/frame_"),
        str(output_dir / "frames/iris_closeup/frame_"),
        str(output_dir / "frames/hero/frame_"),
        str(output_dir / "frames/stacked/frame_%04d.png"),
        str(output_dir / "walking_beam_alignment_wide.mp4"),
        str(output_dir / "walking_beam_alignment_iris_closeup.mp4"),
        str(output_dir / "walking_beam_alignment_stacked.mp4"),
        str(output_dir / "walking_beam_alignment_hero.mp4"),
        "Render mode: final",
        "Cycles device: default",
        "Wide Setup Camera",
        "Iris Close-Up Camera",
        "Hero Camera",
        "vstack=inputs=2",
    ):
        assert expected in dry_run


def test_render_script_preview_flag_overrides_default_render_mode(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "movie"
    result = subprocess.run(
        ["bash", str(SCRIPT), "--preview", "--dry-run", str(output_dir)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Render mode: preview" in result.stdout


def test_render_script_draft_mode_uses_fast_iris_closeup_pipeline(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "movie"
    result = subprocess.run(
        ["bash", str(SCRIPT), "--draft", "--dry-run", str(output_dir)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    dry_run = result.stdout
    assert "Render mode: draft" in dry_run
    assert "Frame step: 4" in dry_run
    assert "Resolution: 960x540" in dry_run
    assert str(output_dir / "frames/draft_iris_closeup/frame_") in dry_run
    assert str(output_dir / "walking_beam_alignment_draft_iris_closeup.mp4") in dry_run
    assert "Iris Close-Up Camera" in dry_run
    assert "Wide Setup Camera" not in dry_run
    assert "Hero Camera" not in dry_run
    assert "vstack=inputs=2" not in dry_run


def test_render_script_dry_run_lists_cycles_device_override(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "movie"
    env = os.environ.copy()
    env["CYCLES_DEVICE"] = "CUDA"
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", str(output_dir)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )

    assert result.returncode == 0
    assert "Cycles device: CUDA" in result.stdout


def test_linux_render_script_dry_run_sets_hpc_defaults(tmp_path: Path) -> None:
    output_dir = tmp_path / "movie"
    result = subprocess.run(
        ["bash", str(LINUX_SCRIPT), "--dry-run", str(output_dir)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert f"BLENDER_BIN={PROJECT_BLENDER}" in result.stdout
    assert "CYCLES_DEVICE=CUDA" in result.stdout
    assert "FFMPEG_MODULE=ffmpeg/7.1" in result.stdout
    assert f"{PROJECT_BLENDER} --background" in result.stdout
    assert "Cycles device: CUDA" in result.stdout


def test_still_render_script_dry_run_lists_four_png_perspectives(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "stills"
    result = subprocess.run(
        ["bash", str(STILL_SCRIPT), "--dry-run", str(output_dir)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    dry_run = result.stdout
    for expected in (
        str(output_dir / "walking_beam_alignment.blend"),
        str(output_dir / "wide.png"),
        str(output_dir / "iris_closeup.png"),
        str(output_dir / "hero.png"),
        str(output_dir / "stacked.png"),
        "Frame: 168",
        "Wide Setup Camera",
        "Iris Close-Up Camera",
        "Hero Camera",
        "vstack=inputs=2",
    ):
        assert expected in dry_run
