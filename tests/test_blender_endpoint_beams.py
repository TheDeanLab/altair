from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import textwrap

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
MACOS_BLENDER = Path("/Applications/Blender.app/Contents/MacOS/Blender")
BLENDER = shutil.which("blender") or (
    str(MACOS_BLENDER) if MACOS_BLENDER.exists() else None
)


@pytest.mark.skipif(BLENDER is None, reason="Blender executable is not available")
def test_endpoint_keyframed_beam_curve_interpolates_traced_endpoints_without_rotation_wrap():
    assert BLENDER is not None
    script = textwrap.dedent(
        """
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path.cwd()))

        import bpy

        from simulations.blender.altair_blender.animation import set_linear_interpolation
        from simulations.blender.altair_blender.optics import (
            beam_curve_endpoints,
            create_beam_curve_between,
            keyframe_beam_curve_between,
        )

        def assert_close_tuple(actual, expected, tolerance=1e-5):
            for actual_value, expected_value in zip(actual, expected, strict=True):
                assert abs(actual_value - expected_value) <= tolerance, (
                    actual,
                    expected,
                )

        material = bpy.data.materials.new("laser")
        start_13 = (-50.8, -50.8, 45.8)
        end_13 = (-50.37, 0.4, 46.77)
        start_19 = (-50.8, -50.8, 45.8)
        end_19 = (-50.86, -0.08, 46.64)
        beam = create_beam_curve_between(
            name="M1 to M2 endpoint beam",
            start_xyz=start_13,
            end_xyz=end_13,
            radius_mm=0.7,
            material=material,
            collection=bpy.context.scene.collection,
        )
        keyframe_beam_curve_between(
            beam=beam,
            start_xyz=start_13,
            end_xyz=end_13,
            frame=13,
        )
        keyframe_beam_curve_between(
            beam=beam,
            start_xyz=start_19,
            end_xyz=end_19,
            frame=19,
        )
        set_linear_interpolation(beam)

        bpy.context.scene.frame_set(16)
        start_16, end_16 = beam_curve_endpoints(beam)

        expected_start = (-50.8, -50.8, 45.8)
        expected_end = (
            (end_13[0] + end_19[0]) / 2.0,
            (end_13[1] + end_19[1]) / 2.0,
            (end_13[2] + end_19[2]) / 2.0,
        )
        assert_close_tuple(start_16, expected_start)
        assert_close_tuple(end_16, expected_end)
        assert_close_tuple(tuple(beam.rotation_euler), (0.0, 0.0, 0.0))
        assert_close_tuple(tuple(beam.scale), (1.0, 1.0, 1.0))
        print("endpoint-beam-ok")
        """
    )

    result = subprocess.run(
        [BLENDER, "--background", "--python-expr", f"exec({script!r})"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "endpoint-beam-ok" in result.stdout
