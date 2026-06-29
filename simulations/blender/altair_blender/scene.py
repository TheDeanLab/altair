"""Scene-level helpers for Blender-generated optics simulations."""

from __future__ import annotations

from pathlib import Path
from types import ModuleType
from typing import Any

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

WORLD_BACKGROUND_COLOR = (0.24, 0.25, 0.26)


def get_bpy() -> ModuleType:
    """Return Blender's `bpy` module or raise a clear runtime error.

    Returns
    -------
    ModuleType
        Imported Blender Python module.
    """

    try:
        import bpy  # pyright: ignore[reportMissingImports]
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


def _set_render_engine(scene: Any, preferred: str, fallbacks: tuple[str, ...]) -> str:
    """Select the first render engine accepted by the active Blender runtime.

    Parameters
    ----------
    scene
        Blender scene whose render engine should be configured.
    preferred
        Preferred render engine identifier.
    fallbacks
        Render engine identifiers to try if the preferred engine fails.

    Returns
    -------
    str
        Actual render engine selected by Blender.
    """

    for engine in (preferred, *fallbacks):
        if engine == "CYCLES":
            try:
                import addon_utils  # pyright: ignore[reportMissingImports]

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


def _try_setattr(obj: Any, attr: str, value: Any) -> None:
    """Set an optional Blender attribute when the runtime supports it.

    Parameters
    ----------
    obj
        Object whose attribute should be assigned.
    attr
        Attribute name.
    value
        Attribute value.
    """

    try:
        setattr(obj, attr, value)
    except (AttributeError, TypeError, ValueError):
        return


def _configure_color_management(scene: Any) -> None:
    """Apply robust color-management defaults across Blender versions.

    Parameters
    ----------
    scene
        Blender scene whose view settings should be configured.
    """

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
    """Apply a reusable preview or final render preset to the active scene.

    Parameters
    ----------
    preset_name
        Name of the render preset to apply.

    Returns
    -------
    str
        Actual render engine selected by Blender.
    """

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


def configure_cycles_device(device_name: str) -> str:
    """Configure the active Cycles scene to use a requested render device.

    Parameters
    ----------
    device_name
        Requested Cycles device name, such as ``CPU``, ``CUDA``, or
        ``OPTIX+CPU``.

    Returns
    -------
    str
        Device selection status.
    """

    requested = device_name.strip().upper()
    if not requested or requested == "DEFAULT":
        return "default"

    bpy = get_bpy()
    scene = bpy.context.scene
    if scene.render.engine != "CYCLES" or not hasattr(scene, "cycles"):
        return f"ignored for {scene.render.engine}"

    include_cpu = requested.endswith("+CPU")
    device_type = requested.removesuffix("+CPU")
    if device_type == "CPU":
        _try_setattr(scene.cycles, "device", "CPU")
        return "CPU"

    try:
        import addon_utils  # pyright: ignore[reportMissingImports]

        addon_utils.enable("cycles", default_set=False, persistent=False)
        preferences = bpy.context.preferences.addons["cycles"].preferences
        preferences.compute_device_type = device_type
        preferences.refresh_devices()
    except Exception as exc:
        raise RuntimeError(f"Could not configure Cycles device {requested!r}.") from exc

    for device in preferences.devices:
        use_device = device.type == device_type or (
            include_cpu and device.type == "CPU"
        )
        device.use = use_device

    if not any(device.type == device_type for device in preferences.devices):
        raise RuntimeError(f"No Cycles {device_type} device is available.")

    _try_setattr(scene.cycles, "device", "GPU")
    return requested


def configure_scene(
    *,
    frame_start: int,
    frame_end: int,
    fps: int = 24,
    render_preset: str = "preview",
) -> None:
    """Configure units, timeline, render defaults, and world background.

    Parameters
    ----------
    frame_start
        First frame in the scene timeline.
    frame_end
        Last frame in the scene timeline.
    fps
        Rendered movie frame rate.
    render_preset
        Render preset name to apply.
    """

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
    scene.world.color = WORLD_BACKGROUND_COLOR
    apply_render_preset(render_preset)


def add_area_light(
    *,
    name: str,
    location: tuple[float, float, float],
    power: float,
    size: float,
) -> Any:
    """Add a soft area light suitable for shadowed educational renders.

    Parameters
    ----------
    name
        Name for the light object.
    location
        World-space light location in millimeters.
    power
        Light energy in Blender units.
    size
        Area-light size in millimeters.

    Returns
    -------
    object
        Blender light object.
    """

    bpy = get_bpy()
    bpy.ops.object.light_add(type="AREA", location=location)
    light = bpy.context.object
    light.name = name
    light.data.energy = power
    light.data.size = size
    return light


def ensure_collection(name: str) -> Any:
    """Return a named collection, creating and linking it when needed.

    Parameters
    ----------
    name
        Collection name.

    Returns
    -------
    object
        Blender collection object.
    """

    bpy = get_bpy()
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def validate_output_path(output_path: str | None) -> Path | None:
    """Validate an optional `.blend` output path.

    Parameters
    ----------
    output_path
        Optional path where the generated Blender file should be saved.

    Returns
    -------
    pathlib.Path or None
        Expanded output path, or ``None`` when no output was requested.
    """

    if output_path is None:
        return None

    path = Path(output_path).expanduser()
    if not path.parent.exists():
        raise ValueError(f"Output directory does not exist: {path.parent}")
    return path
