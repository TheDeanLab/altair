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


def create_card_closeup_camera(*, card_x_mm: float):
    bpy = get_bpy()
    bpy.ops.object.camera_add(
        location=(card_x_mm - 24.0, -28.0, 20.0),
        rotation=(math.radians(78.0), 0.0, math.radians(-38.0)),
    )
    camera = bpy.context.object
    camera.name = "Card Close-Up Camera"
    camera.data.lens = 80
    camera.data.dof.use_dof = True
    camera.data.dof.focus_distance = 30.0
    return camera
