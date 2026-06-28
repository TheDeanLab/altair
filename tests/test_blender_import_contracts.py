import importlib
import inspect

import pytest


def test_core_modules_import_without_blender():
    scene = importlib.import_module("simulations.blender.altair_blender.scene")
    materials = importlib.import_module("simulations.blender.altair_blender.materials")
    geometry = importlib.import_module("simulations.blender.altair_blender.geometry")
    cameras = importlib.import_module("simulations.blender.altair_blender.cameras")
    animation = importlib.import_module("simulations.blender.altair_blender.animation")
    optics = importlib.import_module("simulations.blender.altair_blender.optics")

    assert callable(scene.get_bpy)
    assert callable(scene.reset_scene)
    assert callable(scene.configure_scene)
    assert callable(scene.ensure_collection)
    assert callable(materials.create_materials)
    assert callable(geometry.create_optical_table)
    assert callable(geometry.create_business_card)
    assert callable(geometry.create_achromat)
    assert callable(geometry.create_lens_mount)
    assert callable(cameras.create_wide_camera)
    assert callable(cameras.create_card_closeup_camera)
    assert callable(animation.keyframe_transform)
    assert callable(animation.set_linear_interpolation)
    assert callable(optics.create_beam_between)
    assert callable(optics.create_return_spot)


def test_get_bpy_reports_clear_error_outside_blender():
    scene = importlib.import_module("simulations.blender.altair_blender.scene")

    with pytest.raises(RuntimeError, match="Blender"):
        scene.get_bpy()


def test_wide_camera_exposes_target_and_distance_controls():
    cameras = importlib.import_module("simulations.blender.altair_blender.cameras")

    signature = inspect.signature(cameras.create_wide_camera)

    assert "target" in signature.parameters
    assert "distance_mm" in signature.parameters
    assert signature.parameters["target"].kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.parameters["distance_mm"].kind is inspect.Parameter.KEYWORD_ONLY
