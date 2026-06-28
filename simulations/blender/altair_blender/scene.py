"""Scene-level helpers for Blender-generated optics simulations."""

from __future__ import annotations

from pathlib import Path
from types import ModuleType


RENDER_PRESETS = {
    "preview": {
        "engine": "BLENDER_EEVEE",
        "samples": 96,
        "description": "Fast EEVEE preview render for iteration and smoke checks.",
    },
    "final": {
        "engine": "CYCLES",
        "samples": 128,
        "description": "Cycles beauty render for deliverable movies.",
    },
}


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


def _set_render_engine(scene, preferred: str, fallbacks: tuple[str, ...]) -> str:
    for engine in (preferred, *fallbacks):
        if engine == "CYCLES":
            try:
                import addon_utils  # type: ignore[import-not-found]

                addon_utils.enable("cycles", default_set=False, persistent=False)
            except Exception:
                pass
        try:
            scene.render.engine = engine
        except (TypeError, ValueError):
            continue
        if scene.render.engine == engine:
            return engine
    return scene.render.engine


def _try_setattr(obj, attr: str, value) -> None:
    try:
        setattr(obj, attr, value)
    except (AttributeError, TypeError, ValueError):
        return


def _configure_color_management(scene) -> None:
    for view_transform in ("Filmic", "AgX"):
        try:
            scene.view_settings.view_transform = view_transform
            break
        except (TypeError, ValueError):
            continue

    for look in ("Medium High Contrast", "High Contrast", "Medium Contrast"):
        try:
            scene.view_settings.look = look
            break
        except (TypeError, ValueError):
            continue

    _try_setattr(scene.view_settings, "exposure", -0.15)
    _try_setattr(scene.view_settings, "gamma", 1.0)


def apply_render_preset(preset_name: str) -> str:
    """Apply a reusable preview or final render preset to the active scene."""

    if preset_name not in RENDER_PRESETS:
        valid = ", ".join(sorted(RENDER_PRESETS))
        raise ValueError(f"Unknown render preset {preset_name!r}; expected {valid}.")

    bpy = get_bpy()
    scene = bpy.context.scene
    preset = RENDER_PRESETS[preset_name]
    requested_engine = str(preset["engine"])

    if preset_name == "final":
        actual_engine = _set_render_engine(
            scene, requested_engine, ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE")
        )
        if actual_engine == "CYCLES" and hasattr(scene, "cycles"):
            _try_setattr(scene.cycles, "samples", int(preset["samples"]))
            _try_setattr(scene.cycles, "preview_samples", 32)
            _try_setattr(scene.cycles, "use_denoising", True)
            _try_setattr(scene.cycles, "max_bounces", 8)
            _try_setattr(scene.cycles, "diffuse_bounces", 3)
            _try_setattr(scene.cycles, "glossy_bounces", 4)
            _try_setattr(scene.cycles, "transparent_max_bounces", 8)
    else:
        actual_engine = _set_render_engine(
            scene, requested_engine, ("BLENDER_EEVEE_NEXT",)
        )

    eevee = getattr(scene, "eevee", None)
    if eevee is not None:
        _try_setattr(eevee, "taa_render_samples", int(preset["samples"]))
        if hasattr(eevee, "use_gtao"):
            eevee.use_gtao = True
            eevee.gtao_distance = 24
            eevee.gtao_factor = 1.25

    _configure_color_management(scene)
    return actual_engine


def configure_scene(
    *,
    frame_start: int,
    frame_end: int,
    fps: int = 24,
    render_preset: str = "preview",
) -> None:
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
    scene.world.color = (0.015, 0.018, 0.022)
    apply_render_preset(render_preset)


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
