import bpy
import numpy as np

from nanoparticle_generator.blender import BLENDER_EPS, BlenderObjectReference


class Ellipsoid(BlenderObjectReference):
    def __init__(self, dimensions=(1.0, 1.0, 1.0), subdivisions=5):
        if isinstance(dimensions, (float, int)):
            dimensions = (dimensions,) * 3
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions,
                                              radius=0.5)
        BlenderObjectReference.__init__(self, bpy.context.object)
        self.scale(dimensions)


class Box(BlenderObjectReference):
    def __init__(self, dimensions=(1.0, 1.0, 1.0)):
        if isinstance(dimensions, (float, int)):
            dimensions = (dimensions,) * 3
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        BlenderObjectReference.__init__(self, bpy.context.object)
        self.scale(dimensions)


class Cylinder(BlenderObjectReference):
    def __init__(self, diameter=1.0, height=1.0, vertices=32):
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,
                                            radius=diameter/2, depth=height)
        BlenderObjectReference.__init__(self, bpy.context.object)


class SphericallyCappedCylinder(BlenderObjectReference):
    def __init__(self, diameter=0.5, middle_section_height=0.5, subdivisions=5):
        Ellipsoid.__init__(self, diameter, subdivisions=subdivisions)
        with self.selected(mode='edit'):
            # Extrude upper cap
            self.select_vertices(criterion_func=lambda v: v.co[2] > -BLENDER_EPS)
            bpy.ops.mesh.extrude_region_move(
                TRANSFORM_OT_translate={'value': (0, 0, middle_section_height/2)}
            )
            # Move lower cap
            self.select_vertices(criterion_func=lambda v: v.co[2] < BLENDER_EPS)
            bpy.ops.transform.translate(value=(0, 0, -middle_section_height/2))


class Octahedron(BlenderObjectReference):
    def __init__(self, size=1.0, truncation_degree=0.0):
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        BlenderObjectReference.__init__(self, bpy.context.object)
        bpy.ops.object.modifier_add(type='BEVEL')
        bpy.context.object.modifiers['Bevel'].offset_type = 'PERCENT'
        bpy.context.object.modifiers['Bevel'].width_pct = 100
        bpy.ops.object.modifier_apply(modifier='Bevel')  # To actually apply it
        self.remove_duplicate_vertices()
        if truncation_degree > 0:
            bpy.ops.object.modifier_add(type='BEVEL')
            bpy.context.object.modifiers['Bevel'].offset_type = 'PERCENT'
            truncation_degree /= 3  # Since edges meet at 33.3% offset
            bpy.context.object.modifiers['Bevel'].width_pct = 100 * truncation_degree
            bpy.ops.object.modifier_apply(modifier='Bevel')
            self.remove_duplicate_vertices()
        # Adjust object size after truncation
        self.scale(size / self.enclosing_sphere_diameter)


class Icosahedron(BlenderObjectReference):
    def __init__(self, size=1.0):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=size/2)
        BlenderObjectReference.__init__(self, bpy.context.object)


class Prism(BlenderObjectReference):
    def __init__(self, n_sides, size=1.0, height=1.0, truncation_degree=0.0,
                 tips_smoothing_degree=0.0, edges_smoothing_degree=0.0,
                 smoothing_bevel_segments=3):
        """Diameter corresponds to enclosing cylinder."""
        bpy.ops.mesh.primitive_cylinder_add(vertices=n_sides, radius=size/2,
                                            depth=height)
        BlenderObjectReference.__init__(self, bpy.context.object)

        def is_edge_vertical(edge):
            v1_id, v2_id = edge.vertices
            x1, y1, _ = self.vertices[v1_id].co
            x2, y2, _ = self.vertices[v2_id].co
            return abs(x2 - x1) < BLENDER_EPS and abs(y2 - y1) < BLENDER_EPS

        if truncation_degree > 0:
            with self.selected(mode='edit'):
                self.select_edges(criterion_func=is_edge_vertical)
                truncation_degree *= 0.5  # Since edges meet at 50% offset
                bpy.ops.mesh.bevel(offset_type='PERCENT',
                                offset_pct=100*truncation_degree,
                                clamp_overlap=True)
            # Bevel is applied upon switching back to object mode
            self.remove_duplicate_vertices()

        # Smooth tips and horizontal edges separately because of high anisotropy
        if tips_smoothing_degree > 0:
            with self.selected(mode='edit'):
                self.select_edges(criterion_func=is_edge_vertical)
                bpy.ops.mesh.bevel(offset=tips_smoothing_degree*self.dimensions.x,
                                   segments=smoothing_bevel_segments,
                                   clamp_overlap=True)
            self.remove_duplicate_vertices()
        if edges_smoothing_degree > 0:
            with self.selected(mode='edit'):
                self.select_edges(criterion_func=lambda x: not is_edge_vertical(x))
                bpy.ops.mesh.bevel(offset=edges_smoothing_degree*self.dimensions.z,
                                segments=smoothing_bevel_segments,
                                clamp_overlap=True)
            self.remove_duplicate_vertices()
        # Adjust object size after truncation
        self.scale(size / np.hypot(self.dimensions.x, self.dimensions.y))


class Bipyramid(BlenderObjectReference):
    def __init__(self, n_sides=5, diameter=1.0, height=1.0,
                 tips_truncation_degree=0.0):
        """Diameter corresponds to enclosing cylinder."""
        bpy.ops.mesh.primitive_circle_add(vertices=n_sides, radius=diameter/2)
        BlenderObjectReference.__init__(self, bpy.context.object)
        with self.selected(mode='edit'):
            bpy.ops.mesh.select_all(action='SELECT')
            # Upper half
            bpy.ops.mesh.extrude_region_move(
                TRANSFORM_OT_translate={'value': (0, 0, height/2)}
            )
            # Bring all extruded vertices together on the axis
            bpy.ops.transform.resize(value=(0, 0, 0))
            # Lower half
            self.select_vertices(criterion_func=lambda v: v.co[2] < BLENDER_EPS)
            bpy.ops.mesh.extrude_region_move(
                TRANSFORM_OT_translate={'value': (0, 0, -height/2)}
            )
            bpy.ops.transform.resize(value=(0, 0, 0))
            self.remove_duplicate_vertices()

            if tips_truncation_degree > 0:
                def is_vertex_out_of_plane(vertex):
                    return abs(vertex.co[2]) > BLENDER_EPS
                self.select_vertices(criterion_func=is_vertex_out_of_plane)
                bevel_width = tips_truncation_degree * max(self.dimensions)
                if bevel_width < BLENDER_EPS:
                    return
                bpy.ops.mesh.bevel(affect='VERTICES', offset_type='WIDTH', offset=bevel_width,
                                   segments=1, clamp_overlap=True)
                self.remove_duplicate_vertices()
