"""Reusable material helpers for Blender optics scenes."""

from __future__ import annotations

from .scene import get_bpy


def _material(
    name: str, color: tuple[float, float, float, float], *, emission: float = 0.0
):
    bpy = get_bpy()
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Alpha"].default_value = color[3]
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = color
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emission
    material.blend_method = "BLEND"
    return material


def create_materials() -> dict[str, object]:
    """Create the standard material palette for the simulation."""

    return {
        "table": _material("Optical Table Matte Black", (0.025, 0.028, 0.03, 1.0)),
        "metal": _material("Black Anodized Metal", (0.08, 0.085, 0.09, 1.0)),
        "card": _material("Business Card Stock", (0.92, 0.88, 0.78, 1.0)),
        "aperture": _material("Aperture Edge", (0.02, 0.02, 0.018, 1.0)),
        "glass": _material("Coated Achromat Glass", (0.55, 0.82, 0.95, 0.32)),
        "laser": _material("561 nm Laser Beam", (0.35, 1.0, 0.18, 0.65), emission=2.5),
        "spot_a": _material("Return Spot A", (0.45, 1.0, 0.22, 1.0), emission=3.0),
        "spot_b": _material("Return Spot B", (0.18, 0.85, 1.0, 1.0), emission=2.6),
        "label": _material("Subtle Label", (0.9, 0.95, 1.0, 1.0)),
    }
