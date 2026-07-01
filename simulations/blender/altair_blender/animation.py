"""Animation helpers for Blender optics simulations."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any


def keyframe_transform(
    obj: Any,
    *,
    frame: int,
    location: tuple[float, float, float] | None = None,
    rotation_euler: tuple[float, float, float] | None = None,
) -> None:
    """Set optional transforms and insert keyframes for them.

    Parameters
    ----------
    obj
        Blender object to animate.
    frame
        Timeline frame where keyframes should be inserted.
    location
        Optional object location to set before keyframing.
    rotation_euler
        Optional Euler rotation to set before keyframing.
    """

    if location is not None:
        obj.location = location
        obj.keyframe_insert(data_path="location", frame=frame)
    if rotation_euler is not None:
        obj.rotation_euler = rotation_euler
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)


def keyframe_visibility(obj: Any, *, frame: int, visible: bool) -> None:
    """Keyframe viewport and render visibility together.

    Parameters
    ----------
    obj
        Blender object whose visibility should be animated.
    frame
        Timeline frame where keyframes should be inserted.
    visible
        Whether the object should be visible at the frame.
    """

    obj.hide_viewport = not visible
    obj.hide_render = not visible
    obj.keyframe_insert(data_path="hide_viewport", frame=frame)
    obj.keyframe_insert(data_path="hide_render", frame=frame)


def _iter_action_fcurves(action: Any) -> Iterator[Any]:
    """Yield f-curves from both legacy and Blender 5 action layouts.

    Parameters
    ----------
    action
        Blender animation action to inspect.

    Yields
    ------
    object
        F-curve objects attached to the action.
    """

    fcurves = getattr(action, "fcurves", None)
    if fcurves is not None:
        yield from fcurves
        return

    for layer in getattr(action, "layers", ()):
        for strip in getattr(layer, "strips", ()):
            for channelbag in getattr(strip, "channelbags", ()):
                yield from getattr(channelbag, "fcurves", ())


def set_linear_interpolation(obj: Any) -> None:
    """Set all animation curves for an object to linear interpolation.

    Parameters
    ----------
    obj
        Blender object whose object and data-block action keyframes should be
        linearized.
    """

    animation_owners = (obj, getattr(obj, "data", None))
    for owner in animation_owners:
        if owner is None:
            continue
        if owner.animation_data is None or owner.animation_data.action is None:
            continue
        for fcurve in _iter_action_fcurves(owner.animation_data.action):
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = "LINEAR"
