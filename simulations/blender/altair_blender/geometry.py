"""Geometry builders for Blender optics alignment scenes."""

from __future__ import annotations

from collections.abc import Sequence
import math
from typing import Any

from .optics import spherical_surface_x
from .prescriptions import (
    AC254_100_A,
    LMR1_MOUNT,
    AchromatPrescription,
    LensMountPrescription,
    LensSurface,
)
from .scene import get_bpy


def _link_to_collection(obj: Any, collection: Any) -> None:
    """Move an object into the requested collection only.

    Parameters
    ----------
    obj
        Blender object to relink.
    collection
        Blender collection that should own the object.
    """

    for existing in obj.users_collection:
        existing.objects.unlink(obj)
    collection.objects.link(obj)


def _new_parent(
    name: str, *, collection: Any, location: tuple[float, float, float]
) -> Any:
    """Create an empty parent object in a collection.

    Parameters
    ----------
    name
        Parent object name.
    collection
        Blender collection that should contain the parent.
    location
        Parent location in scene coordinates.

    Returns
    -------
    object
        Blender empty object.
    """

    bpy = get_bpy()
    parent = bpy.data.objects.new(name, None)
    parent.empty_display_type = "PLAIN_AXES"
    parent.empty_display_size = 5.0
    parent.location = location
    collection.objects.link(parent)
    return parent


def _add_soft_edges(obj: Any, *, width_mm: float, segments: int = 2) -> None:
    """Add bevel and weighted-normal modifiers for cleaner rendered edges.

    Parameters
    ----------
    obj
        Blender mesh object to modify.
    width_mm
        Bevel width in millimeters.
    segments
        Number of bevel segments.
    """

    bevel = obj.modifiers.new("Softened Edges", "BEVEL")
    bevel.width = width_mm
    bevel.segments = segments
    if hasattr(bevel, "affect"):
        try:
            bevel.affect = "EDGES"
        except (TypeError, ValueError):
            pass
    obj.modifiers.new("Weighted Normals", "WEIGHTED_NORMAL")


def _mesh_object(
    name: str,
    *,
    collection: Any,
    parent: Any | None,
    vertices: Sequence[tuple[float, float, float]],
    faces: Sequence[tuple[int, ...]],
    material: Any,
) -> Any:
    """Create a smooth mesh object from raw vertex and face data.

    Parameters
    ----------
    name
        Mesh and object name.
    collection
        Blender collection that should contain the mesh object.
    parent
        Optional parent object.
    vertices
        Mesh vertices in object-local coordinates.
    faces
        Mesh faces expressed as vertex indices.
    material
        Material to assign to the mesh.

    Returns
    -------
    object
        Blender mesh object.
    """

    bpy = get_bpy()
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    obj.parent = parent
    obj.data.materials.append(material)
    collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth()
    obj.select_set(False)
    return obj


def _box_object(
    name: str,
    *,
    collection: Any,
    parent: Any | None,
    dimensions: tuple[float, float, float],
    location: tuple[float, float, float],
    material: Any,
) -> Any:
    """Create a softened rectangular prism mesh.

    Parameters
    ----------
    name
        Object name.
    collection
        Blender collection that should contain the box.
    parent
        Optional parent object.
    dimensions
        Box dimensions in millimeters.
    location
        Box center location relative to its parent.
    material
        Material to assign to the box.

    Returns
    -------
    object
        Blender mesh object.
    """

    dx, dy, dz = (dimension / 2.0 for dimension in dimensions)
    cx, cy, cz = location
    vertices = [
        (cx - dx, cy - dy, cz - dz),
        (cx + dx, cy - dy, cz - dz),
        (cx + dx, cy + dy, cz - dz),
        (cx - dx, cy + dy, cz - dz),
        (cx - dx, cy - dy, cz + dz),
        (cx + dx, cy - dy, cz + dz),
        (cx + dx, cy + dy, cz + dz),
        (cx - dx, cy + dy, cz + dz),
    ]
    faces = [
        (0, 1, 2, 3),
        (4, 7, 6, 5),
        (0, 4, 5, 1),
        (1, 5, 6, 2),
        (2, 6, 7, 3),
        (3, 7, 4, 0),
    ]
    obj = _mesh_object(
        name,
        collection=collection,
        parent=parent,
        vertices=vertices,
        faces=faces,
        material=material,
    )
    _add_soft_edges(obj, width_mm=0.18, segments=2)
    return obj


def _surface_vertices(
    surface: LensSurface, *, radial_steps: int, angular_steps: int
) -> list[tuple[float, float, float]]:
    """Sample vertices across a spherical lens surface.

    Parameters
    ----------
    surface
        Lens surface to sample.
    radial_steps
        Number of radial subdivisions.
    angular_steps
        Number of angular subdivisions.

    Returns
    -------
    list[tuple[float, float, float]]
        Surface vertices in lens-local coordinates.
    """

    vertices = []
    for radial_index in range(radial_steps + 1):
        radial = surface.clear_radius_mm * (radial_index / radial_steps)
        x = spherical_surface_x(surface, radial_mm=radial)
        for angular_index in range(angular_steps):
            angle = (2.0 * math.pi * angular_index) / angular_steps
            vertices.append((x, radial * math.cos(angle), radial * math.sin(angle)))
    return vertices


def _element_mesh(
    name: str,
    *,
    collection: Any,
    parent: Any,
    front_surface: LensSurface,
    back_surface: LensSurface,
    material: Any,
    radial_steps: int = 18,
    angular_steps: int = 96,
) -> Any:
    """Create a lens element mesh bounded by two spherical surfaces.

    Parameters
    ----------
    name
        Element object name.
    collection
        Blender collection that should contain the element.
    parent
        Parent object for the lens assembly.
    front_surface
        Front optical surface.
    back_surface
        Back optical surface.
    material
        Material to assign to the element.
    radial_steps
        Number of radial mesh subdivisions.
    angular_steps
        Number of angular mesh subdivisions.

    Returns
    -------
    object
        Blender mesh object.
    """

    front_vertices = _surface_vertices(
        front_surface, radial_steps=radial_steps, angular_steps=angular_steps
    )
    back_vertices = _surface_vertices(
        back_surface, radial_steps=radial_steps, angular_steps=angular_steps
    )
    vertices = front_vertices + back_vertices
    back_offset = len(front_vertices)
    faces = []

    for radial_index in range(radial_steps):
        for angular_index in range(angular_steps):
            next_angular = (angular_index + 1) % angular_steps
            a = (radial_index * angular_steps) + angular_index
            b = (radial_index * angular_steps) + next_angular
            c = ((radial_index + 1) * angular_steps) + next_angular
            d = ((radial_index + 1) * angular_steps) + angular_index
            faces.append((a, b, c, d))
            faces.append(
                (back_offset + d, back_offset + c, back_offset + b, back_offset + a)
            )

    outer_front = radial_steps * angular_steps
    outer_back = back_offset + outer_front
    for angular_index in range(angular_steps):
        next_angular = (angular_index + 1) % angular_steps
        faces.append(
            (
                outer_front + angular_index,
                outer_front + next_angular,
                outer_back + next_angular,
                outer_back + angular_index,
            )
        )

    return _mesh_object(
        name,
        collection=collection,
        parent=parent,
        vertices=vertices,
        faces=faces,
        material=material,
    )


def _grid_offsets(
    *, span_mm: float, spacing_mm: float, border_mm: float
) -> tuple[float, ...]:
    """Return centered grid offsets within a bounded span.

    Parameters
    ----------
    span_mm
        Total span available for grid points.
    spacing_mm
        Grid spacing in millimeters.
    border_mm
        Minimum distance from each edge to the nearest grid point.

    Returns
    -------
    tuple[float, ...]
        Symmetric offsets from the span center.
    """

    if spacing_mm <= 0.0:
        raise ValueError("spacing_mm must be positive.")
    if border_mm < 0.0:
        raise ValueError("border_mm must be non-negative.")
    max_offset = (span_mm / 2.0) - border_mm
    if max_offset < 0.0:
        return (0.0,)
    steps = int(math.floor((max_offset / spacing_mm) + 1e-9))
    return tuple(round(index * spacing_mm, 6) for index in range(-steps, steps + 1))


def optical_table_hole_centers(
    *,
    length_mm: float,
    width_mm: float,
    spacing_mm: float = 25.4,
    border_mm: float = 12.7,
) -> tuple[tuple[float, float], ...]:
    """Return local XY centers for a 1 inch / 25.4 mm optical-table hole grid.

    Parameters
    ----------
    length_mm
        Table length in millimeters.
    width_mm
        Table width in millimeters.
    spacing_mm
        Hole spacing in millimeters.
    border_mm
        Minimum border from the table edge to a hole center.

    Returns
    -------
    tuple[tuple[float, float], ...]
        Hole-center offsets in the table-local XY plane.
    """

    return tuple(
        (x_mm, y_mm)
        for x_mm in _grid_offsets(
            span_mm=length_mm, spacing_mm=spacing_mm, border_mm=border_mm
        )
        for y_mm in _grid_offsets(
            span_mm=width_mm, spacing_mm=spacing_mm, border_mm=border_mm
        )
    )


def optical_table_hole_geometry(
    *,
    table_z_mm: float,
    table_thickness_mm: float,
    well_recess_mm: float = 0.28,
) -> dict[str, float]:
    """Compute Z positions and depths for optical-table hole details.

    Parameters
    ----------
    table_z_mm
        Table center Z position in millimeters.
    table_thickness_mm
        Table thickness in millimeters.
    well_recess_mm
        Recess depth below the table top.

    Returns
    -------
    dict[str, float]
        Named Z positions and depths for cutters and visible wells.
    """

    table_top_z = table_z_mm + (table_thickness_mm / 2.0)
    cutter_depth = table_thickness_mm + 0.4
    well_depth = table_thickness_mm - (well_recess_mm * 2.0)
    well_top_z = table_top_z - well_recess_mm
    return {
        "table_top_z_mm": table_top_z,
        "cutter_center_z_mm": table_z_mm,
        "cutter_depth_mm": cutter_depth,
        "well_center_z_mm": well_top_z - (well_depth / 2.0),
        "well_depth_mm": well_depth,
        "well_top_z_mm": well_top_z,
    }


def create_optical_table(
    *,
    collection: Any,
    materials: dict[str, object],
    length_mm: float = 220.0,
    width_mm: float = 90.0,
    hole_spacing_mm: float = 25.4,
    hole_diameter_mm: float = 5.6,
    hole_border_mm: float = 12.7,
    hole_recess_mm: float = 0.28,
) -> Any:
    """Create the optical table surface and visible grid of threaded holes.

    Parameters
    ----------
    collection
        Blender collection that should contain the table objects.
    materials
        Material palette returned by ``create_materials``.
    length_mm
        Table length in millimeters.
    width_mm
        Table width in millimeters.
    hole_spacing_mm
        Grid spacing between holes in millimeters.
    hole_diameter_mm
        Diameter of each visual table hole.
    hole_border_mm
        Minimum border from table edge to hole centers.
    hole_recess_mm
        Recess distance below the table top.

    Returns
    -------
    object
        Blender mesh object for the table body.
    """

    bpy = get_bpy()
    table_x = 70.0
    table_z = -8.0
    table_thickness = 6.0
    bpy.ops.mesh.primitive_cube_add(size=1, location=(70.0, 0.0, -8.0))
    table = bpy.context.object
    table.name = "Optical Table"
    table.dimensions = (length_mm, width_mm, table_thickness)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    table.data.materials.append(materials["table"])
    _link_to_collection(table, collection)

    hole_radius = hole_diameter_mm / 2.0
    hole_geometry = optical_table_hole_geometry(
        table_z_mm=table_z,
        table_thickness_mm=table_thickness,
        well_recess_mm=hole_recess_mm,
    )
    for index, (x_mm, y_mm) in enumerate(
        optical_table_hole_centers(
            length_mm=length_mm,
            width_mm=width_mm,
            spacing_mm=hole_spacing_mm,
            border_mm=hole_border_mm,
        ),
        start=1,
    ):
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=48,
            radius=hole_radius,
            depth=hole_geometry["cutter_depth_mm"],
            location=(
                table_x + x_mm,
                y_mm,
                hole_geometry["cutter_center_z_mm"],
            ),
        )
        cutter = bpy.context.object
        cutter.name = f"Optical Table Hole Cutter {index:03d}"
        boolean = table.modifiers.new(f"Hole Cut {index:03d}", "BOOLEAN")
        boolean.operation = "DIFFERENCE"
        boolean.object = cutter
        if hasattr(boolean, "solver"):
            try:
                boolean.solver = "EXACT"
            except (TypeError, ValueError):
                pass
        bpy.context.view_layer.objects.active = table
        table.select_set(True)
        bpy.ops.object.modifier_apply(modifier=boolean.name)
        bpy.data.objects.remove(cutter, do_unlink=True)

        bpy.ops.mesh.primitive_cylinder_add(
            vertices=48,
            radius=hole_radius * 0.88,
            depth=hole_geometry["well_depth_mm"],
            location=(
                table_x + x_mm,
                y_mm,
                hole_geometry["well_center_z_mm"],
            ),
        )
        well = bpy.context.object
        well.name = f"Optical Table Hole Well {index:03d}"
        well.data.materials.append(materials["table_hole"])
        _link_to_collection(well, collection)
        bpy.ops.object.shade_smooth()

    _add_soft_edges(table, width_mm=0.16, segments=2)
    return table


def create_studio_backdrop(
    *,
    collection: Any,
    materials: dict[str, object],
    center_x_mm: float = 70.0,
    y_mm: float = 58.0,
    center_z_mm: float = 38.0,
) -> Any:
    """Create a neutral vertical backdrop behind the scene.

    Parameters
    ----------
    collection
        Blender collection that should contain the backdrop.
    materials
        Material palette returned by ``create_materials``.
    center_x_mm
        Backdrop center X position.
    y_mm
        Backdrop Y position.
    center_z_mm
        Backdrop center Z position.

    Returns
    -------
    object
        Blender mesh object for the backdrop.
    """

    half_width = 130.0
    half_height = 60.0
    vertices = [
        (center_x_mm - half_width, y_mm, center_z_mm - half_height),
        (center_x_mm + half_width, y_mm, center_z_mm - half_height),
        (center_x_mm + half_width, y_mm, center_z_mm + half_height),
        (center_x_mm - half_width, y_mm, center_z_mm + half_height),
    ]
    return _mesh_object(
        "Dark Studio Backdrop",
        collection=collection,
        parent=None,
        vertices=vertices,
        faces=[(0, 1, 2, 3)],
        material=materials["backdrop"],
    )


def create_business_card(
    *,
    collection: Any,
    materials: dict[str, object],
    x_mm: float,
    width_mm: float,
    height_mm: float,
    aperture_diameter_mm: float,
    optical_axis_z_mm: float = 15.0,
) -> tuple[Any, Any]:
    """Create the aperture card and visible aperture ring.

    Parameters
    ----------
    collection
        Blender collection that should contain the card objects.
    materials
        Material palette returned by ``create_materials``.
    x_mm
        Card X position in millimeters.
    width_mm
        Card width in millimeters.
    height_mm
        Card height in millimeters.
    aperture_diameter_mm
        Aperture diameter in millimeters.
    optical_axis_z_mm
        Optical-axis height in millimeters.

    Returns
    -------
    tuple[object, object]
        Blender objects for the card body and aperture ring.
    """

    bpy = get_bpy()
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x_mm, 0.0, optical_axis_z_mm))
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
        location=(x_mm - 0.7, 0.0, optical_axis_z_mm),
        rotation=(0.0, math.radians(90.0), 0.0),
    )
    aperture = bpy.context.object
    aperture.name = "Card Aperture"
    aperture.data.materials.append(materials["aperture"])
    _link_to_collection(aperture, collection)
    return card, aperture


def create_scene_label(
    *,
    collection: Any,
    materials: dict[str, object],
    name: str,
    text: str,
    location: tuple[float, float, float],
    size_mm: float = 3.0,
) -> Any:
    """Create a small text label for a teaching scene.

    Parameters
    ----------
    collection
        Blender collection that should contain the label.
    materials
        Material palette returned by ``create_materials``.
    name
        Label object name.
    text
        Text displayed in the scene.
    location
        Label location in scene coordinates.
    size_mm
        Text size in millimeters.

    Returns
    -------
    object
        Blender text object.
    """

    bpy = get_bpy()
    bpy.ops.object.text_add(
        location=location,
        rotation=(math.radians(90.0), 0.0, 0.0),
    )
    label = bpy.context.object
    label.name = name
    label.data.name = f"{name} Text"
    label.data.body = text
    label.data.align_x = "CENTER"
    label.data.align_y = "CENTER"
    label.data.size = size_mm
    label.data.extrude = 0.015
    label.data.materials.append(materials["label"])
    _link_to_collection(label, collection)
    return label


def create_achromat(
    *,
    collection: Any,
    materials: dict[str, object],
    x_mm: float,
    diameter_mm: float | None = None,
    thickness_mm: float | None = None,
    optical_axis_z_mm: float = 15.0,
    prescription: AchromatPrescription = AC254_100_A,
) -> Any:
    """Create the cemented achromat assembly from its prescription.

    Parameters
    ----------
    collection
        Blender collection that should contain the achromat.
    materials
        Material palette returned by ``create_materials``.
    x_mm
        Lens X position in millimeters.
    diameter_mm
        Deprecated compatibility parameter; the prescription controls diameter.
    thickness_mm
        Deprecated compatibility parameter; the prescription controls thickness.
    optical_axis_z_mm
        Optical-axis height in millimeters.
    prescription
        Source-backed achromat prescription.

    Returns
    -------
    object
        Parent Blender object for the achromat assembly.
    """

    del diameter_mm, thickness_mm
    parent = _new_parent(
        "AC254-100-A Doublet Assembly",
        collection=collection,
        location=(x_mm, 0.0, optical_axis_z_mm),
    )
    _element_mesh(
        "N-BK7 Crown Element",
        collection=collection,
        parent=parent,
        front_surface=prescription.surfaces[0],
        back_surface=prescription.surfaces[1],
        material=materials["bk7_glass"],
    )
    _element_mesh(
        "SF5 Flint Element",
        collection=collection,
        parent=parent,
        front_surface=prescription.surfaces[1],
        back_surface=prescription.surfaces[2],
        material=materials["sf5_glass"],
    )
    _element_mesh(
        "Cemented Interface Glint",
        collection=collection,
        parent=parent,
        front_surface=prescription.surfaces[1],
        back_surface=prescription.surfaces[1],
        material=materials["coating"],
        radial_steps=8,
        angular_steps=96,
    )
    return parent


def create_lens_mount(
    *,
    collection: Any,
    materials: dict[str, object],
    x_mm: float,
    diameter_mm: float | None = None,
    optical_axis_z_mm: float = 15.0,
    mount: LensMountPrescription = LMR1_MOUNT,
) -> Any:
    """Create a simplified LMR1-style lens mount.

    Parameters
    ----------
    collection
        Blender collection that should contain the mount.
    materials
        Material palette returned by ``create_materials``.
    x_mm
        Mount X position in millimeters.
    diameter_mm
        Deprecated compatibility parameter; the mount prescription controls
        aperture size.
    optical_axis_z_mm
        Optical-axis height in millimeters.
    mount
        Source-backed lens-mount prescription.

    Returns
    -------
    object
        Parent Blender object for the lens mount assembly.
    """

    del diameter_mm
    bpy = get_bpy()
    parent = _new_parent(
        "LMR1-Style Fixed Lens Mount",
        collection=collection,
        location=(x_mm, 0.0, optical_axis_z_mm),
    )
    side_width = (mount.body_width_mm - mount.clear_aperture_mm) / 2.0
    cap_height = (mount.body_height_mm - mount.clear_aperture_mm) / 2.0
    _box_object(
        "LMR1 Left Frame Rail",
        collection=collection,
        parent=parent,
        dimensions=(mount.body_depth_mm, side_width, mount.clear_aperture_mm),
        location=(0.0, -((mount.clear_aperture_mm + side_width) / 2.0), 0.0),
        material=materials["metal"],
    )
    _box_object(
        "LMR1 Right Frame Rail",
        collection=collection,
        parent=parent,
        dimensions=(mount.body_depth_mm, side_width, mount.clear_aperture_mm),
        location=(0.0, (mount.clear_aperture_mm + side_width) / 2.0, 0.0),
        material=materials["metal"],
    )
    _box_object(
        "LMR1 Top Frame Rail",
        collection=collection,
        parent=parent,
        dimensions=(mount.body_depth_mm, mount.body_width_mm, cap_height),
        location=(0.0, 0.0, (mount.clear_aperture_mm + cap_height) / 2.0),
        material=materials["metal"],
    )
    _box_object(
        "LMR1 Bottom Frame Rail",
        collection=collection,
        parent=parent,
        dimensions=(mount.body_depth_mm, mount.body_width_mm, cap_height),
        location=(0.0, 0.0, -((mount.clear_aperture_mm + cap_height) / 2.0)),
        material=materials["metal"],
    )
    bpy.ops.mesh.primitive_torus_add(
        major_radius=(mount.clear_aperture_mm / 2.0) + 0.7,
        minor_radius=0.7,
        major_segments=96,
        minor_segments=12,
        location=(0.0, 0.0, 0.0),
        rotation=(0.0, math.radians(90.0), 0.0),
    )
    ring = bpy.context.object
    ring.name = "SM1 Retaining Ring"
    ring.parent = parent
    ring.location = (-(mount.body_depth_mm / 2.0) - 0.2, 0.0, 0.0)
    ring.data.materials.append(materials["metal"])
    _link_to_collection(ring, collection)
    for name, y_mm in (
        ("LMR1 Lower Spanner Slot", -mount.clear_aperture_mm / 2.6),
        ("LMR1 Upper Spanner Slot", mount.clear_aperture_mm / 2.6),
    ):
        _box_object(
            name,
            collection=collection,
            parent=parent,
            dimensions=(1.2, 3.4, 1.0),
            location=(-(mount.body_depth_mm / 2.0) - 0.9, y_mm, 0.0),
            material=materials["aperture"],
        )
    _box_object(
        "LMR1 Mounting Foot",
        collection=collection,
        parent=parent,
        dimensions=(12.0, 16.0, 3.0),
        location=(0.0, 0.0, -(mount.optical_axis_height_mm + 1.5)),
        material=materials["metal"],
    )
    return parent
