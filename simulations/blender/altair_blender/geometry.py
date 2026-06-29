"""Geometry builders for Blender optics alignment scenes."""

from __future__ import annotations

from collections.abc import Sequence
import math
from typing import Any

from .optics import spherical_surface_x
from .prescriptions import (
    AC254_100_A,
    ID25_IRIS,
    KM100CP_MOUNT,
    LMR1_MOUNT,
    PH2_POST_HOLDER,
    TR15_POST,
    AchromatPrescription,
    IrisPrescription,
    LensMountPrescription,
    LensSurface,
    MirrorMountPrescription,
    OpticalPostPrescription,
    PostHolderPrescription,
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


def _cylinder_object(
    name: str,
    *,
    collection: Any,
    parent: Any | None,
    radius_mm: float,
    depth_mm: float,
    location: tuple[float, float, float],
    material: Any,
    vertices: int = 64,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> Any:
    """Create a smoothed cylinder mesh.

    Parameters
    ----------
    name
        Object name.
    collection
        Blender collection that should contain the cylinder.
    parent
        Optional parent object.
    radius_mm
        Cylinder radius in millimeters.
    depth_mm
        Cylinder depth in millimeters.
    location
        Cylinder center location relative to the parent.
    material
        Material to assign to the cylinder.
    vertices
        Number of radial vertices.
    rotation
        Euler rotation applied when the cylinder is created.

    Returns
    -------
    object
        Blender mesh object.
    """

    bpy = get_bpy()
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius_mm,
        depth=depth_mm,
        location=(0.0, 0.0, 0.0),
        rotation=rotation,
    )
    cylinder = bpy.context.object
    cylinder.name = name
    cylinder.parent = parent
    cylinder.location = location
    cylinder.data.materials.append(material)
    _link_to_collection(cylinder, collection)
    bpy.ops.object.shade_smooth()
    _add_soft_edges(cylinder, width_mm=0.08, segments=1)
    return cylinder


def _torus_object(
    name: str,
    *,
    collection: Any,
    parent: Any | None,
    major_radius_mm: float,
    minor_radius_mm: float,
    location: tuple[float, float, float],
    material: Any,
    major_segments: int = 96,
    minor_segments: int = 8,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> Any:
    """Create a smoothed torus mesh.

    Parameters
    ----------
    name
        Object name.
    collection
        Blender collection that should contain the torus.
    parent
        Optional parent object.
    major_radius_mm
        Distance from torus center to tube centerline.
    minor_radius_mm
        Tube radius.
    location
        Torus center location relative to the parent.
    material
        Material to assign to the torus.
    major_segments
        Number of torus ring segments.
    minor_segments
        Number of tube segments.
    rotation
        Euler rotation applied when the torus is created.

    Returns
    -------
    object
        Blender mesh object.
    """

    bpy = get_bpy()
    bpy.ops.mesh.primitive_torus_add(
        major_segments=major_segments,
        minor_segments=minor_segments,
        major_radius=major_radius_mm,
        minor_radius=minor_radius_mm,
        location=(0.0, 0.0, 0.0),
        rotation=rotation,
    )
    torus = bpy.context.object
    torus.name = name
    torus.parent = parent
    torus.location = location
    torus.data.materials.append(material)
    _link_to_collection(torus, collection)
    bpy.ops.object.shade_smooth()
    return torus


def _annular_cylinder_x_object(
    name: str,
    *,
    collection: Any,
    parent: Any | None,
    outer_radius_mm: float,
    inner_radius_mm: float,
    depth_mm: float,
    location: tuple[float, float, float],
    material: Any,
    vertices: int = 96,
) -> Any:
    """Create an annular cylinder whose open aperture runs along local X.

    Parameters
    ----------
    name
        Object name.
    collection
        Blender collection that should contain the annular cylinder.
    parent
        Optional parent object.
    outer_radius_mm
        Outer radius in millimeters.
    inner_radius_mm
        Inner open radius in millimeters.
    depth_mm
        Cylinder depth along local X in millimeters.
    location
        Annulus center location relative to its parent.
    material
        Material to assign to the annular cylinder.
    vertices
        Number of radial vertices.

    Returns
    -------
    object
        Blender mesh object.
    """

    if inner_radius_mm <= 0.0 or outer_radius_mm <= inner_radius_mm:
        raise ValueError("outer_radius_mm must be larger than inner_radius_mm.")

    half_depth = depth_mm / 2.0
    cx, cy, cz = location
    mesh_vertices = []
    for x_mm in (cx - half_depth, cx + half_depth):
        for radius in (outer_radius_mm, inner_radius_mm):
            for index in range(vertices):
                angle = (2.0 * math.pi * index) / vertices
                mesh_vertices.append(
                    (
                        x_mm,
                        cy + (radius * math.cos(angle)),
                        cz + (radius * math.sin(angle)),
                    )
                )

    front_outer = 0
    front_inner = vertices
    back_outer = vertices * 2
    back_inner = vertices * 3
    faces = []
    for index in range(vertices):
        next_index = (index + 1) % vertices
        faces.append(
            (
                front_outer + index,
                front_outer + next_index,
                back_outer + next_index,
                back_outer + index,
            )
        )
        faces.append(
            (
                front_inner + next_index,
                front_inner + index,
                back_inner + index,
                back_inner + next_index,
            )
        )
        faces.append(
            (
                front_outer + next_index,
                front_outer + index,
                front_inner + index,
                front_inner + next_index,
            )
        )
        faces.append(
            (
                back_outer + index,
                back_outer + next_index,
                back_inner + next_index,
                back_inner + index,
            )
        )

    obj = _mesh_object(
        name,
        collection=collection,
        parent=parent,
        vertices=mesh_vertices,
        faces=faces,
        material=material,
    )
    _add_soft_edges(obj, width_mm=0.08, segments=1)
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


def iris_reticle_face_offsets(
    *,
    iris_thickness_mm: float,
    face_selection: str,
    face_clearance_mm: float = 0.62,
) -> tuple[float, ...]:
    """Return local X offsets for iris reticle face placement.

    Parameters
    ----------
    iris_thickness_mm
        Iris body thickness along local X.
    face_selection
        Face selection: ``front``, ``back``, or ``both``.
    face_clearance_mm
        Distance outside the iris body face for the reticle geometry.

    Returns
    -------
    tuple[float, ...]
        Local X offsets for one or two reticle faces.
    """

    if iris_thickness_mm <= 0.0:
        raise ValueError("iris_thickness_mm must be positive.")
    if face_clearance_mm < 0.0:
        raise ValueError("face_clearance_mm must be non-negative.")

    face_offset = (iris_thickness_mm / 2.0) + face_clearance_mm
    if face_selection == "front":
        return (-face_offset,)
    if face_selection == "back":
        return (face_offset,)
    if face_selection == "both":
        return (-face_offset, face_offset)
    raise ValueError("face_selection must be 'front', 'back', or 'both'.")


def create_optical_table(
    *,
    collection: Any,
    materials: dict[str, object],
    length_mm: float = 220.0,
    width_mm: float = 90.0,
    center_x_mm: float = 70.0,
    center_y_mm: float = 0.0,
    center_z_mm: float = -8.0,
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
    center_x_mm
        Table center X position in millimeters.
    center_y_mm
        Table center Y position in millimeters.
    center_z_mm
        Table center Z position in millimeters.
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
    table_thickness = 6.0
    bpy.ops.mesh.primitive_cube_add(
        size=1, location=(center_x_mm, center_y_mm, center_z_mm)
    )
    table = bpy.context.object
    table.name = "Optical Table"
    table.dimensions = (length_mm, width_mm, table_thickness)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    table.data.materials.append(materials["table"])
    _link_to_collection(table, collection)

    hole_radius = hole_diameter_mm / 2.0
    hole_geometry = optical_table_hole_geometry(
        table_z_mm=center_z_mm,
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
                center_x_mm + x_mm,
                center_y_mm + y_mm,
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
                center_x_mm + x_mm,
                center_y_mm + y_mm,
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


def create_post_holder(
    *,
    collection: Any,
    materials: dict[str, object],
    x_mm: float,
    y_mm: float,
    table_top_z_mm: float,
    holder: PostHolderPrescription = PH2_POST_HOLDER,
    name: str = "PH2-Style Post Holder",
) -> Any:
    """Create a simplified post holder and table foot.

    Parameters
    ----------
    collection
        Blender collection that should contain the holder.
    materials
        Material palette returned by ``create_materials``.
    x_mm
        Holder X position in millimeters.
    y_mm
        Holder Y position in millimeters.
    table_top_z_mm
        Z coordinate of the optical table top.
    holder
        Source-backed post-holder prescription.
    name
        Parent object name.

    Returns
    -------
    object
        Parent Blender object for the post-holder assembly.
    """

    parent = _new_parent(name, collection=collection, location=(x_mm, y_mm, 0.0))
    metal = materials["metal"]
    dark = materials["aperture"]
    sleeve_radius = (holder.accepted_post_diameter_mm / 2.0) + 3.0
    sleeve_center_z = table_top_z_mm + (holder.length_mm / 2.0)
    _cylinder_object(
        f"{holder.name} Sleeve",
        collection=collection,
        parent=parent,
        radius_mm=sleeve_radius,
        depth_mm=holder.length_mm,
        location=(0.0, 0.0, sleeve_center_z),
        material=metal,
        vertices=72,
    )
    _box_object(
        f"{holder.name} Base Foot",
        collection=collection,
        parent=parent,
        dimensions=(22.0, 22.0, 3.2),
        location=(0.0, 0.0, table_top_z_mm + 1.6),
        material=metal,
    )
    _box_object(
        f"{holder.name} Relief Cut",
        collection=collection,
        parent=parent,
        dimensions=(sleeve_radius * 1.75, 1.0, holder.length_mm * 0.72),
        location=(0.0, -sleeve_radius, sleeve_center_z + 2.5),
        material=dark,
    )
    _cylinder_object(
        f"{holder.name} Locking Thumbscrew",
        collection=collection,
        parent=parent,
        radius_mm=1.45,
        depth_mm=12.0,
        location=(0.0, sleeve_radius + 5.6, table_top_z_mm + holder.length_mm * 0.62),
        material=metal,
        vertices=24,
        rotation=(math.radians(90.0), 0.0, 0.0),
    )
    return parent


def create_optical_post(
    *,
    collection: Any,
    materials: dict[str, object],
    x_mm: float,
    y_mm: float,
    table_top_z_mm: float,
    post: OpticalPostPrescription = TR15_POST,
    name: str = "TR1.5-Style Optical Post",
) -> Any:
    """Create a simplified cylindrical optical post.

    Parameters
    ----------
    collection
        Blender collection that should contain the post.
    materials
        Material palette returned by ``create_materials``.
    x_mm
        Post X position in millimeters.
    y_mm
        Post Y position in millimeters.
    table_top_z_mm
        Z coordinate of the optical table top.
    post
        Source-backed optical-post prescription.
    name
        Parent object name.

    Returns
    -------
    object
        Parent Blender object for the optical post.
    """

    parent = _new_parent(name, collection=collection, location=(x_mm, y_mm, 0.0))
    post_material = materials.get("post_steel", materials["table"])
    _cylinder_object(
        f"{post.name} Stainless Post",
        collection=collection,
        parent=parent,
        radius_mm=post.diameter_mm / 2.0,
        depth_mm=post.length_mm,
        location=(0.0, 0.0, table_top_z_mm + (post.length_mm / 2.0)),
        material=post_material,
        vertices=72,
    )
    return parent


def create_post_mounted_iris(
    *,
    collection: Any,
    materials: dict[str, object],
    x_mm: float,
    y_mm: float,
    optical_axis_z_mm: float,
    iris: IrisPrescription = ID25_IRIS,
    display_aperture_mm: float | None = None,
    show_alignment_reticle: bool = True,
    reticle_radius_mm: float | None = None,
    reticle_faces: str = "front",
    holder: PostHolderPrescription = PH2_POST_HOLDER,
    post: OpticalPostPrescription = TR15_POST,
    table_top_z_mm: float = -5.0,
    support_visual_top_z_mm: float | None = None,
    name: str = "ID25-Style Post-Mounted Iris",
) -> Any:
    """Create a simplified post-mounted iris with its aperture on axis.

    Parameters
    ----------
    collection
        Blender collection that should contain the iris assembly.
    materials
        Material palette returned by ``create_materials``.
    x_mm
        Iris X position in millimeters.
    y_mm
        Iris Y position in millimeters.
    optical_axis_z_mm
        Shared optical-axis height in millimeters.
    iris
        Source-backed iris prescription.
    display_aperture_mm
        Optional visual aperture diameter. Defaults to the iris maximum
        aperture so the beam passes through a real open hole in the mesh.
    show_alignment_reticle
        Whether to draw a high-contrast ring and ticks around the displayed
        aperture.
    reticle_radius_mm
        Optional radius for the alignment reticle ring. Defaults just outside
        the displayed aperture.
    reticle_faces
        Reticle face selection: ``front``, ``back``, or ``both``.
    holder
        Source-backed post-holder prescription.
    post
        Source-backed optical-post prescription.
    table_top_z_mm
        Z coordinate of the optical table top.
    support_visual_top_z_mm
        Optional visual top of the post-holder support. Defaults below the
        iris body so the post does not pass through the aperture.
    name
        Parent object name.

    Returns
    -------
    object
        Parent Blender object for the post-mounted iris assembly.
    """

    parent = _new_parent(name, collection=collection, location=(x_mm, y_mm, 0.0))
    metal = materials["metal"]
    dark = materials["aperture"]
    post_material = materials.get("post_steel", materials["table"])
    reticle_material = materials.get("alignment_reference", materials["spot_a"])
    support_top_z = support_visual_top_z_mm
    if support_top_z is None:
        support_top_z = optical_axis_z_mm - (iris.outer_diameter_mm / 2.0) - 2.0
    support_length = max(6.0, support_top_z - table_top_z_mm)
    aperture_diameter = display_aperture_mm or iris.max_aperture_mm
    reticle_radius = reticle_radius_mm or ((aperture_diameter / 2.0) + 1.6)

    _cylinder_object(
        f"{post.name} Iris Support Post",
        collection=collection,
        parent=parent,
        radius_mm=post.diameter_mm / 2.0,
        depth_mm=support_length,
        location=(0.0, 0.0, table_top_z_mm + (support_length / 2.0)),
        material=post_material,
        vertices=72,
    )
    _cylinder_object(
        f"{holder.name} Iris Post Holder",
        collection=collection,
        parent=parent,
        radius_mm=(holder.accepted_post_diameter_mm / 2.0) + 3.0,
        depth_mm=support_length,
        location=(0.0, 0.0, table_top_z_mm + (support_length / 2.0)),
        material=metal,
        vertices=72,
    )
    _box_object(
        f"{iris.name} Pedestal Clamp",
        collection=collection,
        parent=parent,
        dimensions=(iris.thickness_mm + 2.0, 11.0, 3.0),
        location=(0.0, 0.0, support_top_z + 1.5),
        material=metal,
    )
    _annular_cylinder_x_object(
        f"{iris.name} Iris Body",
        collection=collection,
        parent=parent,
        outer_radius_mm=iris.outer_diameter_mm / 2.0,
        inner_radius_mm=aperture_diameter / 2.0,
        depth_mm=iris.thickness_mm,
        location=(0.0, 0.0, optical_axis_z_mm),
        material=metal,
        vertices=96,
    )
    _annular_cylinder_x_object(
        f"{iris.name} Aperture Edge Ring",
        collection=collection,
        parent=parent,
        outer_radius_mm=(aperture_diameter / 2.0) + 0.9,
        inner_radius_mm=aperture_diameter / 2.0,
        depth_mm=0.35,
        location=(-(iris.thickness_mm / 2.0) - 0.3, 0.0, optical_axis_z_mm),
        material=dark,
        vertices=96,
    )
    if show_alignment_reticle:
        for face_index, reticle_x in enumerate(
            iris_reticle_face_offsets(
                iris_thickness_mm=iris.thickness_mm,
                face_selection=reticle_faces,
            ),
            start=1,
        ):
            face_name = "Front" if reticle_x < 0.0 else "Back"
            _torus_object(
                f"{iris.name} {face_name} Alignment Reticle Ring",
                collection=collection,
                parent=parent,
                major_radius_mm=reticle_radius,
                minor_radius_mm=0.10,
                location=(reticle_x, 0.0, optical_axis_z_mm),
                material=reticle_material,
                major_segments=96,
                minor_segments=8,
                rotation=(0.0, math.radians(90.0), 0.0),
            )
            tick_offset = reticle_radius + 0.9
            for tick_name, tick_location, tick_dimensions in (
                (
                    "Top",
                    (reticle_x, 0.0, optical_axis_z_mm + tick_offset),
                    (0.24, 1.35, 0.10),
                ),
                (
                    "Bottom",
                    (reticle_x, 0.0, optical_axis_z_mm - tick_offset),
                    (0.24, 1.35, 0.10),
                ),
                (
                    "Left",
                    (reticle_x, -tick_offset, optical_axis_z_mm),
                    (0.24, 0.10, 1.35),
                ),
                (
                    "Right",
                    (reticle_x, tick_offset, optical_axis_z_mm),
                    (0.24, 0.10, 1.35),
                ),
            ):
                _box_object(
                    f"{iris.name} {face_name} Alignment Reticle {tick_name} "
                    f"Tick {face_index}",
                    collection=collection,
                    parent=parent,
                    dimensions=tick_dimensions,
                    location=tick_location,
                    material=reticle_material,
                )
    _box_object(
        f"{iris.name} Lever",
        collection=collection,
        parent=parent,
        dimensions=(1.0, 18.0, 1.8),
        location=(0.0, (iris.outer_diameter_mm / 2.0) + 7.5, optical_axis_z_mm + 4.0),
        material=metal,
    )
    return parent


def create_kinematic_mirror_mount(
    *,
    collection: Any,
    materials: dict[str, object],
    x_mm: float,
    y_mm: float,
    optical_axis_z_mm: float,
    yaw_deg: float,
    mount: MirrorMountPrescription = KM100CP_MOUNT,
    holder: PostHolderPrescription = PH2_POST_HOLDER,
    post: OpticalPostPrescription = TR15_POST,
    table_top_z_mm: float = -5.0,
    support_x_offset_mm: float | None = None,
    support_visual_top_z_mm: float | None = None,
    name: str = "KM100CP-Style Kinematic Mirror Mount",
) -> Any:
    """Create a simplified post-centered kinematic mirror mount.

    Parameters
    ----------
    collection
        Blender collection that should contain the mirror mount.
    materials
        Material palette returned by ``create_materials``.
    x_mm
        Mirror-mount X position in millimeters.
    y_mm
        Mirror-mount Y position in millimeters.
    optical_axis_z_mm
        Shared optical-axis height in millimeters.
    yaw_deg
        Rotation about the vertical axis in degrees.
    mount
        Source-backed mirror-mount prescription.
    holder
        Source-backed post-holder prescription used for the support.
    post
        Source-backed optical-post prescription used for the support.
    table_top_z_mm
        Z coordinate of the optical table top.
    support_x_offset_mm
        Optional mount-local X offset for the post support. Defaults behind
        the mirror frame so the support does not pass through the optic.
    support_visual_top_z_mm
        Optional visual top of the post-holder support. Defaults below the
        mirror frame bottom.
    name
        Parent object name.

    Returns
    -------
    object
        Parent Blender object for the kinematic mirror mount assembly.
    """

    parent = _new_parent(
        name, collection=collection, location=(x_mm, y_mm, optical_axis_z_mm)
    )
    parent.rotation_euler = (0.0, 0.0, math.radians(yaw_deg))
    metal = materials["metal"]
    mirror = materials.get("mirror", materials["glass"])
    post_material = materials.get("post_steel", materials["table"])
    dark = materials["aperture"]
    local_table_top_z = table_top_z_mm - optical_axis_z_mm
    support_x = (
        support_x_offset_mm
        if support_x_offset_mm is not None
        else (mount.body_depth_mm / 2.0) + 9.0
    )
    frame_bottom_z = -(mount.body_height_mm / 2.0)
    support_top_z = support_visual_top_z_mm
    if support_top_z is None:
        support_top_z = optical_axis_z_mm + frame_bottom_z - 1.0
    local_support_top_z = support_top_z - optical_axis_z_mm
    support_length = max(6.0, local_support_top_z - local_table_top_z)

    _cylinder_object(
        f"{post.name} Mirror Support Post",
        collection=collection,
        parent=parent,
        radius_mm=post.diameter_mm / 2.0,
        depth_mm=support_length,
        location=(support_x, 0.0, local_table_top_z + (support_length / 2.0)),
        material=post_material,
        vertices=72,
    )
    _cylinder_object(
        f"{holder.name} Mirror Post Holder",
        collection=collection,
        parent=parent,
        radius_mm=(holder.accepted_post_diameter_mm / 2.0) + 3.0,
        depth_mm=support_length,
        location=(support_x, 0.0, local_table_top_z + (support_length / 2.0)),
        material=metal,
        vertices=72,
    )
    side_width = (mount.body_width_mm - mount.clear_aperture_mm) / 2.0
    cap_height = (mount.body_height_mm - mount.clear_aperture_mm) / 2.0
    _box_object(
        f"{mount.name} Left Frame Rail",
        collection=collection,
        parent=parent,
        dimensions=(mount.body_depth_mm, side_width, mount.clear_aperture_mm),
        location=(0.0, -((mount.clear_aperture_mm + side_width) / 2.0), 0.0),
        material=metal,
    )
    _box_object(
        f"{mount.name} Right Frame Rail",
        collection=collection,
        parent=parent,
        dimensions=(mount.body_depth_mm, side_width, mount.clear_aperture_mm),
        location=(0.0, (mount.clear_aperture_mm + side_width) / 2.0, 0.0),
        material=metal,
    )
    _box_object(
        f"{mount.name} Top Frame Rail",
        collection=collection,
        parent=parent,
        dimensions=(mount.body_depth_mm, mount.body_width_mm, cap_height),
        location=(0.0, 0.0, (mount.clear_aperture_mm + cap_height) / 2.0),
        material=metal,
    )
    _box_object(
        f"{mount.name} Bottom Frame Rail",
        collection=collection,
        parent=parent,
        dimensions=(mount.body_depth_mm, mount.body_width_mm, cap_height),
        location=(0.0, 0.0, -((mount.clear_aperture_mm + cap_height) / 2.0)),
        material=metal,
    )
    _box_object(
        f"{mount.name} Rear Support Bracket",
        collection=collection,
        parent=parent,
        dimensions=(abs(support_x) + 3.0, 9.0, 3.0),
        location=(support_x / 2.0, 0.0, frame_bottom_z - 1.5),
        material=metal,
    )
    _cylinder_object(
        f"{mount.name} Mirror Optic",
        collection=collection,
        parent=parent,
        radius_mm=mount.optic_diameter_mm / 2.0,
        depth_mm=1.2,
        location=(-(mount.body_depth_mm / 2.0) - 0.7, 0.0, 0.0),
        material=mirror,
        vertices=96,
        rotation=(0.0, math.radians(90.0), 0.0),
    )
    for index, (y_mm, z_mm) in enumerate(
        (
            (mount.body_width_mm / 2.0 - 5.5, mount.body_height_mm / 2.0 - 6.0),
            (mount.body_width_mm / 2.0 - 5.5, -mount.body_height_mm / 2.0 + 6.0),
        ),
        start=1,
    ):
        _cylinder_object(
            f"{mount.name} Adjuster Shaft {index}",
            collection=collection,
            parent=parent,
            radius_mm=1.0,
            depth_mm=9.0,
            location=(mount.body_depth_mm / 2.0 + 4.5, y_mm, z_mm),
            material=metal,
            vertices=24,
            rotation=(0.0, math.radians(90.0), 0.0),
        )
        _cylinder_object(
            f"{mount.name} Adjuster Knob {index}",
            collection=collection,
            parent=parent,
            radius_mm=2.7,
            depth_mm=3.6,
            location=(mount.body_depth_mm / 2.0 + 10.0, y_mm, z_mm),
            material=dark,
            vertices=32,
            rotation=(0.0, math.radians(90.0), 0.0),
        )
    return parent
