"""Animation helpers for Blender optics simulations."""

from __future__ import annotations


def keyframe_transform(obj, *, frame: int, location=None, rotation_euler=None) -> None:
    """Set optional transforms and insert keyframes for them."""

    if location is not None:
        obj.location = location
        obj.keyframe_insert(data_path="location", frame=frame)
    if rotation_euler is not None:
        obj.rotation_euler = rotation_euler
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)


def keyframe_visibility(obj, *, frame: int, visible: bool) -> None:
    """Keyframe viewport and render visibility together."""

    obj.hide_viewport = not visible
    obj.hide_render = not visible
    obj.keyframe_insert(data_path="hide_viewport", frame=frame)
    obj.keyframe_insert(data_path="hide_render", frame=frame)


def _iter_action_fcurves(action):
    fcurves = getattr(action, "fcurves", None)
    if fcurves is not None:
        yield from fcurves
        return

    for layer in getattr(action, "layers", ()):
        for strip in getattr(layer, "strips", ()):
            for channelbag in getattr(strip, "channelbags", ()):
                yield from getattr(channelbag, "fcurves", ())


def set_linear_interpolation(obj) -> None:
    """Set all animation curves for an object to linear interpolation."""

    if obj.animation_data is None or obj.animation_data.action is None:
        return
    for fcurve in _iter_action_fcurves(obj.animation_data.action):
        for keyframe in fcurve.keyframe_points:
            keyframe.interpolation = "LINEAR"
