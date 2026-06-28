"""Camera helpers for Blender optics alignment scenes."""

from __future__ import annotations

import math

from .scene import get_bpy


def _look_at(camera, target: tuple[float, float, float]) -> float:
    from mathutils import Vector

    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return direction.length


def create_wide_camera(
    *,
    target: tuple[float, float, float] = (70.0, 0.0, 15.0),
    distance_mm: float = 280.0,
    elevation_mm: float = 90.0,
):
    bpy = get_bpy()
    bpy.ops.object.camera_add(
        location=(
            target[0],
            target[1] - distance_mm,
            target[2] + elevation_mm,
        ),
    )
    camera = bpy.context.object
    camera.name = "Wide Setup Camera"
    camera.data.lens = 35
    camera.data.dof.use_dof = True
    camera.data.dof.focus_distance = _look_at(camera, target)
    bpy.context.scene.camera = camera
    return camera


def create_card_closeup_camera(*, card_x_mm: float, optical_axis_z_mm: float = 15.0):
    bpy = get_bpy()
    bpy.ops.object.camera_add(
        location=(card_x_mm - 24.0, -28.0, optical_axis_z_mm + 5.0),
        rotation=(math.radians(78.0), 0.0, math.radians(-38.0)),
    )
    camera = bpy.context.object
    camera.name = "Card Close-Up Camera"
    camera.data.lens = 80
    camera.data.dof.use_dof = True
    camera.data.dof.focus_distance = 30.0
    return camera


def create_hero_camera(
    *,
    target: tuple[float, float, float] = (55.0, 0.0, 22.0),
    frame_start: int = 1,
    frame_end: int = 168,
    focus_distance_mm: float | None = None,
):
    """Create a slow animated camera for the polished single-view movie."""

    bpy = get_bpy()
    start_location = (target[0] - 20.0, target[1] - 210.0, target[2] + 60.0)
    end_location = (target[0] + 24.0, target[1] - 195.0, target[2] + 52.0)
    bpy.ops.object.camera_add(location=start_location)
    camera = bpy.context.object
    camera.name = "Hero Camera"
    camera.data.lens = 42
    camera.data.dof.use_dof = True
    camera.data.dof.aperture_fstop = 7.1

    camera.location = start_location
    distance = _look_at(camera, target)
    camera.data.dof.focus_distance = focus_distance_mm or distance
    camera.keyframe_insert(data_path="location", frame=frame_start)
    camera.keyframe_insert(data_path="rotation_euler", frame=frame_start)

    camera.location = end_location
    distance = _look_at(camera, target)
    camera.data.dof.focus_distance = focus_distance_mm or distance
    camera.keyframe_insert(data_path="location", frame=frame_end)
    camera.keyframe_insert(data_path="rotation_euler", frame=frame_end)

    return camera
