"""Scene-level helpers for Blender-generated optics simulations."""

from __future__ import annotations

from pathlib import Path
from types import ModuleType


def get_bpy() -> ModuleType:
    """Return Blender's `bpy` module or raise a clear runtime error."""

    try:
        import bpy  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "This function must be run inside Blender with bpy available."
        ) from exc
    return bpy


def reset_scene() -> None:
    """Delete existing objects so the generated scene is deterministic."""

    bpy = get_bpy()
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def configure_scene(*, frame_start: int, frame_end: int, fps: int = 24) -> None:
    """Configure units, timeline, render defaults, and world background."""

    bpy = get_bpy()
    scene = bpy.context.scene
    scene.frame_start = frame_start
    scene.frame_end = frame_end
    scene.frame_set(frame_start)
    scene.render.fps = fps
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 0.001
    scene.eevee.taa_render_samples = 96
    if hasattr(scene.eevee, "use_gtao"):
        scene.eevee.use_gtao = True
        scene.eevee.gtao_distance = 24
        scene.eevee.gtao_factor = 1.2
    scene.world.color = (0.015, 0.018, 0.022)


def add_area_light(
    *,
    name: str,
    location: tuple[float, float, float],
    power: float,
    size: float,
):
    """Add a soft area light suitable for shadowed educational renders."""

    bpy = get_bpy()
    bpy.ops.object.light_add(type="AREA", location=location)
    light = bpy.context.object
    light.name = name
    light.data.energy = power
    light.data.size = size
    return light


def ensure_collection(name: str):
    """Return a named collection, creating and linking it when needed."""

    bpy = get_bpy()
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def validate_output_path(output_path: str | None) -> Path | None:
    """Validate an optional `.blend` output path."""

    if output_path is None:
        return None

    path = Path(output_path).expanduser()
    if not path.parent.exists():
        raise ValueError(f"Output directory does not exist: {path.parent}")
    return path
