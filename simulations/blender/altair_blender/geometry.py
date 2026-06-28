"""Geometry builders for Blender optics alignment scenes."""

from __future__ import annotations

import math

from .scene import get_bpy


def _link_to_collection(obj, collection) -> None:
    for existing in obj.users_collection:
        existing.objects.unlink(obj)
    collection.objects.link(obj)


def create_optical_table(
    *,
    collection,
    materials: dict[str, object],
    length_mm: float = 220.0,
    width_mm: float = 90.0,
):
    bpy = get_bpy()
    bpy.ops.mesh.primitive_cube_add(size=1, location=(70.0, 0.0, -8.0))
    table = bpy.context.object
    table.name = "Optical Table"
    table.dimensions = (length_mm, width_mm, 6.0)
    table.data.materials.append(materials["table"])
    _link_to_collection(table, collection)
    return table


def create_business_card(
    *,
    collection,
    materials: dict[str, object],
    x_mm: float,
    width_mm: float,
    height_mm: float,
    aperture_diameter_mm: float,
):
    bpy = get_bpy()
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x_mm, 0.0, 15.0))
    card = bpy.context.object
    card.name = "Business Card Target"
    card.dimensions = (1.2, width_mm, height_mm)
    card.data.materials.append(materials["card"])
    _link_to_collection(card, collection)

    bpy.ops.mesh.primitive_torus_add(
        major_radius=aperture_diameter_mm * 0.72,
        minor_radius=0.08,
        major_segments=48,
        minor_segments=8,
        location=(x_mm - 0.7, 0.0, 15.0),
        rotation=(0.0, math.radians(90.0), 0.0),
    )
    aperture = bpy.context.object
    aperture.name = "Card Aperture"
    aperture.data.materials.append(materials["aperture"])
    _link_to_collection(aperture, collection)
    return card, aperture


def create_achromat(
    *,
    collection,
    materials: dict[str, object],
    x_mm: float,
    diameter_mm: float,
    thickness_mm: float,
):
    bpy = get_bpy()
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=96,
        radius=diameter_mm / 2.0,
        depth=thickness_mm,
        location=(x_mm, 0.0, 15.0),
        rotation=(0.0, math.radians(90.0), 0.0),
    )
    lens = bpy.context.object
    lens.name = "AC254-100-A-ML Teaching Achromat"
    lens.data.materials.append(materials["glass"])
    _link_to_collection(lens, collection)
    return lens


def create_lens_mount(
    *, collection, materials: dict[str, object], x_mm: float, diameter_mm: float
):
    bpy = get_bpy()
    bpy.ops.mesh.primitive_torus_add(
        major_radius=(diameter_mm / 2.0) + 2.0,
        minor_radius=1.4,
        major_segments=96,
        minor_segments=12,
        location=(x_mm, 0.0, 15.0),
        rotation=(0.0, math.radians(90.0), 0.0),
    )
    mount = bpy.context.object
    mount.name = "Simplified Lens Mount"
    mount.data.materials.append(materials["metal"])
    _link_to_collection(mount, collection)
    return mount
