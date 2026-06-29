"""Reusable material helpers for Blender optics scenes."""

from __future__ import annotations

from typing import Any

from .scene import get_bpy

TABLE_STAINLESS_COLOR = (0.82, 0.84, 0.83, 1.0)
TABLE_BRUSH_LOW_COLOR = (0.74, 0.76, 0.75, 1.0)
TABLE_BRUSH_HIGH_COLOR = (0.95, 0.96, 0.93, 1.0)
TABLE_HOLE_COLOR = (0.035, 0.038, 0.04, 1.0)
BACKDROP_NEUTRAL_COLOR = (0.56, 0.58, 0.59, 1.0)


def _set_input_if_present(bsdf: Any, names: tuple[str, ...], value: Any) -> None:
    """Set the first available node input from a list of candidate names.

    Parameters
    ----------
    bsdf
        Blender shader node whose inputs should be inspected.
    names
        Candidate input names in preference order.
    value
        Value to assign to the first matching input.
    """

    for name in names:
        if name in bsdf.inputs:
            bsdf.inputs[name].default_value = value
            return


def _material(
    name: str,
    color: tuple[float, float, float, float],
    *,
    emission: float = 0.0,
    roughness: float = 0.45,
    metallic: float = 0.0,
    transmission: float = 0.0,
    anisotropic: float = 0.0,
) -> Any:
    """Create a Blender material with a configured Principled BSDF.

    Parameters
    ----------
    name
        Material name.
    color
        RGBA diffuse and base color.
    emission
        Emission strength.
    roughness
        Surface roughness value.
    metallic
        Metallic material value.
    transmission
        Transmission weight when supported by the Blender runtime.
    anisotropic
        Anisotropy value when supported by the Blender runtime.

    Returns
    -------
    object
        Blender material object.
    """

    bpy = get_bpy()
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        _set_input_if_present(bsdf, ("Base Color",), color)
        _set_input_if_present(bsdf, ("Alpha",), color[3])
        _set_input_if_present(bsdf, ("Emission Color",), color)
        _set_input_if_present(bsdf, ("Emission Strength",), emission)
        _set_input_if_present(bsdf, ("Roughness",), roughness)
        _set_input_if_present(bsdf, ("Metallic",), metallic)
        _set_input_if_present(bsdf, ("Transmission Weight",), transmission)
        _set_input_if_present(bsdf, ("IOR",), 1.52)
        _set_input_if_present(
            bsdf, ("Anisotropic", "Anisotropic IOR Level"), anisotropic
        )
    material.blend_method = "BLEND"
    material.use_screen_refraction = color[3] < 1.0
    return material


def _add_brushed_steel_nodes(material: Any) -> None:
    """Add subtle directional brushing to the optical table material.

    Parameters
    ----------
    material
        Blender material to receive procedural brushing nodes.
    """

    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    if bsdf is None:
        return

    wave = nodes.new("ShaderNodeTexWave")
    wave.name = "Long Brushed Grain"
    if hasattr(wave, "wave_type"):
        wave.wave_type = "BANDS"
    if hasattr(wave, "bands_direction"):
        wave.bands_direction = "Y"
    _set_input_if_present(wave, ("Scale",), 36.0)
    _set_input_if_present(wave, ("Distortion",), 8.0)

    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.name = "Brushed Steel Tone"
    ramp.color_ramp.elements[0].position = 0.22
    ramp.color_ramp.elements[0].color = TABLE_BRUSH_LOW_COLOR
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = TABLE_BRUSH_HIGH_COLOR

    bump = nodes.new("ShaderNodeBump")
    bump.name = "Fine Brushed Relief"
    _set_input_if_present(bump, ("Strength",), 0.01)
    _set_input_if_present(bump, ("Distance",), 0.022)

    links.new(wave.outputs["Color"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(wave.outputs["Color"], bump.inputs["Height"])
    if "Normal" in bsdf.inputs:
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])


def create_materials() -> dict[str, object]:
    """Create the standard material palette for the simulation.

    Returns
    -------
    dict[str, object]
        Mapping from semantic material names to Blender material objects.
    """

    table = _material(
        "Brushed Ferromagnetic Stainless Optical Table",
        TABLE_STAINLESS_COLOR,
        emission=0.06,
        roughness=0.24,
        metallic=0.24,
        anisotropic=0.65,
    )
    _add_brushed_steel_nodes(table)

    return {
        "table": table,
        "table_hole": _material(
            "Recessed Table Hole",
            TABLE_HOLE_COLOR,
            roughness=0.36,
            metallic=0.25,
        ),
        "backdrop": _material(
            "Neutral Gray Studio Backdrop",
            BACKDROP_NEUTRAL_COLOR,
            emission=0.05,
            roughness=0.62,
        ),
        "metal": _material(
            "Black Anodized Metal", (0.12, 0.125, 0.13, 1.0), roughness=0.32
        ),
        "post_steel": _material(
            "Polished Stainless Optical Post",
            (0.70, 0.72, 0.70, 1.0),
            roughness=0.22,
            metallic=0.55,
        ),
        "mirror": _material(
            "Protected Silver Mirror",
            (0.88, 0.93, 0.96, 1.0),
            emission=0.02,
            roughness=0.08,
            metallic=0.78,
        ),
        "card": _material("Business Card Stock", (0.92, 0.88, 0.78, 1.0)),
        "aperture": _material("Aperture Edge", (0.02, 0.02, 0.018, 1.0)),
        "glass": _material(
            "Coated Achromat Glass",
            (0.55, 0.82, 0.95, 0.32),
            transmission=0.35,
        ),
        "bk7_glass": _material(
            "N-BK7 Crown Glass",
            (0.56, 0.84, 1.0, 0.30),
            roughness=0.08,
            transmission=0.42,
        ),
        "sf5_glass": _material(
            "SF5 Flint Glass",
            (0.75, 0.66, 1.0, 0.34),
            roughness=0.1,
            transmission=0.32,
        ),
        "coating": _material("BBAR Coating Glint", (0.48, 0.95, 0.72, 0.22)),
        "laser": _material("561 nm Laser Beam", (0.35, 1.0, 0.18, 0.65), emission=2.5),
        "reflection_beam": _material(
            "Faint Reflected Beam", (0.28, 1.0, 0.35, 0.24), emission=1.2
        ),
        "spot_a": _material("Return Spot A", (0.45, 1.0, 0.22, 1.0), emission=3.0),
        "spot_b": _material("Return Spot B", (0.18, 0.85, 1.0, 1.0), emission=2.6),
        "label": _material("Subtle Label", (0.95, 0.98, 1.0, 1.0), emission=0.38),
    }
