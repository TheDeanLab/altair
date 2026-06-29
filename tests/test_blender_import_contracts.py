import importlib
import inspect
from types import SimpleNamespace

import pytest  # pyright: ignore[reportMissingImports]


def test_core_modules_import_without_blender():
    scene = importlib.import_module("simulations.blender.altair_blender.scene")
    materials = importlib.import_module("simulations.blender.altair_blender.materials")
    geometry = importlib.import_module("simulations.blender.altair_blender.geometry")
    cameras = importlib.import_module("simulations.blender.altair_blender.cameras")
    animation = importlib.import_module("simulations.blender.altair_blender.animation")
    optics = importlib.import_module("simulations.blender.altair_blender.optics")
    beam_walking = importlib.import_module(
        "simulations.blender.altair_blender.beam_walking"
    )

    assert callable(scene.get_bpy)
    assert callable(scene.reset_scene)
    assert callable(scene.configure_scene)
    assert callable(scene.apply_render_preset)
    assert callable(scene.ensure_collection)
    assert callable(materials.create_materials)
    assert callable(geometry.create_optical_table)
    assert callable(geometry.create_business_card)
    assert callable(geometry.create_achromat)
    assert callable(geometry.create_lens_mount)
    assert callable(geometry.create_post_holder)
    assert callable(geometry.create_optical_post)
    assert callable(geometry.create_post_mounted_iris)
    assert callable(geometry.create_kinematic_mirror_mount)
    assert callable(geometry.create_scene_label)
    assert callable(cameras.create_wide_camera)
    assert callable(cameras.create_card_closeup_camera)
    assert callable(cameras.create_hero_camera)
    assert callable(animation.keyframe_transform)
    assert callable(animation.set_linear_interpolation)
    assert callable(optics.create_beam_between)
    assert callable(optics.create_return_spot)
    assert callable(optics.trace_ray_branches_through_surfaces)
    assert callable(beam_walking.compute_beam_intercepts)
    assert callable(beam_walking.iterative_alignment_sequence)


def test_optical_table_hole_grid_uses_one_inch_spacing():
    geometry = importlib.import_module("simulations.blender.altair_blender.geometry")

    centers = geometry.optical_table_hole_centers(
        length_mm=76.2,
        width_mm=50.8,
        spacing_mm=25.4,
        border_mm=12.7,
    )

    assert centers == ((-25.4, 0.0), (0.0, 0.0), (25.4, 0.0))


def test_optical_table_hole_geometry_recesses_wells_below_tabletop():
    geometry = importlib.import_module("simulations.blender.altair_blender.geometry")

    spec = geometry.optical_table_hole_geometry(
        table_z_mm=-8.0,
        table_thickness_mm=6.0,
        well_recess_mm=0.28,
    )

    assert spec["table_top_z_mm"] == -5.0
    assert spec["cutter_depth_mm"] > 6.0
    assert spec["well_top_z_mm"] < spec["table_top_z_mm"]


def test_scene_palette_uses_lighter_table_and_backdrop_constants():
    materials = importlib.import_module("simulations.blender.altair_blender.materials")
    scene = importlib.import_module("simulations.blender.altair_blender.scene")

    assert materials.TABLE_STAINLESS_COLOR[0] > 0.78
    assert materials.TABLE_BRUSH_HIGH_COLOR[0] > materials.TABLE_STAINLESS_COLOR[0]
    assert materials.BACKDROP_NEUTRAL_COLOR[0] > 0.50
    assert materials.TABLE_HOLE_COLOR[0] < materials.TABLE_STAINLESS_COLOR[0]
    assert scene.WORLD_BACKGROUND_COLOR[0] > 0.20


def test_scene_palette_exposes_high_contrast_optics_constants():
    materials = importlib.import_module("simulations.blender.altair_blender.materials")

    assert materials.LASER_COLOR[1] > 0.95
    assert materials.LASER_COLOR[3] >= 0.80
    assert materials.MIRROR_COLOR[2] > materials.MIRROR_COLOR[0]
    assert materials.SPOT_B_COLOR[2] > materials.SPOT_B_COLOR[1]
    assert materials.ALIGNMENT_REFERENCE_COLOR[0] > 0.90
    assert materials.ALIGNMENT_REFERENCE_COLOR[1] > 0.70
    assert min(materials.LABEL_COLOR[:3]) > 0.95


def test_get_bpy_reports_clear_error_outside_blender():
    scene = importlib.import_module("simulations.blender.altair_blender.scene")

    with pytest.raises(RuntimeError, match="Blender"):
        scene.get_bpy()


def test_wide_camera_exposes_target_and_distance_controls():
    cameras = importlib.import_module("simulations.blender.altair_blender.cameras")

    signature = inspect.signature(cameras.create_wide_camera)

    assert "target" in signature.parameters
    assert "distance_mm" in signature.parameters
    assert "frame_start" in signature.parameters
    assert "frame_end" in signature.parameters
    assert signature.parameters["target"].kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.parameters["distance_mm"].kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.parameters["frame_start"].kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.parameters["frame_end"].kind is inspect.Parameter.KEYWORD_ONLY


def test_hero_camera_exposes_animation_and_focus_controls():
    cameras = importlib.import_module("simulations.blender.altair_blender.cameras")

    signature = inspect.signature(cameras.create_hero_camera)

    for parameter in (
        "target",
        "frame_start",
        "frame_end",
        "focus_distance_mm",
    ):
        assert parameter in signature.parameters
        assert signature.parameters[parameter].kind is inspect.Parameter.KEYWORD_ONLY


def test_hardware_builders_expose_keyword_only_geometry_controls():
    geometry = importlib.import_module("simulations.blender.altair_blender.geometry")

    for function_name, required_parameters in {
        "create_post_holder": (
            "collection",
            "materials",
            "x_mm",
            "y_mm",
            "table_top_z_mm",
            "holder",
        ),
        "create_optical_post": (
            "collection",
            "materials",
            "x_mm",
            "y_mm",
            "table_top_z_mm",
            "post",
        ),
        "create_post_mounted_iris": (
            "collection",
            "materials",
            "x_mm",
            "y_mm",
            "optical_axis_z_mm",
            "iris",
            "display_aperture_mm",
            "show_alignment_reticle",
            "reticle_radius_mm",
            "support_visual_top_z_mm",
        ),
        "create_kinematic_mirror_mount": (
            "collection",
            "materials",
            "x_mm",
            "y_mm",
            "optical_axis_z_mm",
            "yaw_deg",
            "mount",
            "support_x_offset_mm",
            "support_visual_top_z_mm",
        ),
    }.items():
        signature = inspect.signature(getattr(geometry, function_name))
        for parameter in required_parameters:
            assert parameter in signature.parameters
            assert (
                signature.parameters[parameter].kind is inspect.Parameter.KEYWORD_ONLY
            )


def test_render_engine_setter_does_not_depend_on_stale_enum_listing():
    scene = importlib.import_module("simulations.blender.altair_blender.scene")
    fake_scene = SimpleNamespace(
        render=SimpleNamespace(
            engine="BLENDER_EEVEE",
        ),
    )

    actual = scene._set_render_engine(  # noqa: SLF001
        fake_scene,
        "CYCLES",
        ("BLENDER_EEVEE",),
    )

    assert actual == "CYCLES"
    assert fake_scene.render.engine == "CYCLES"
