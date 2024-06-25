import os
from contextlib import AbstractContextManager, contextmanager, redirect_stdout

import bpy
import numpy as np
import pyvista as pv
import vtk
from mathutils import Vector


BLENDER_EPS = 1e-5  # Tolerance for Blender floating point operations


def _suppress_stdout(func):
    """Function wrapper that removes all standard output"""
    def wrapper(*a, **ka):
        with open(os.devnull, 'w') as devnull:
            with redirect_stdout(devnull):
                func(*a, **ka)
    return wrapper


class BlenderScene(AbstractContextManager):
    def __init__(self):
        """Blender scene that gets cleared on exit from the context"""
        bpy.ops.scene.new()

    def __exit__(self, *args):
        bpy.ops.scene.delete()


class BlenderObjectReference:
    def __init__(self, object):
        self.blender_object = object

    def delete(self):
        """Delete the referenced object"""
        with self.selected(mode='object'):
            bpy.ops.object.delete()

    def copy(self):
        with self.selected(mode='object'):
            bpy.ops.object.duplicate()
            return BlenderObjectReference(bpy.context.active_object)

    @classmethod
    def from_stl(cls, filepath):
        bpy.ops.import_mesh.stl(filepath=filepath)
        return cls(bpy.context.object)

    @property
    def location(self):
        """Bounding box center."""
        return self.bounding_box[0] + self.dimensions/2

    def translate(self, transation_vector):
        self.blender_object.location = transation_vector
        self.apply_all_transforms()

    @property
    def rotation(self):
        return self.blender_object.rotation_euler

    def rotate(self, euler_angles=None, quaternion=None):
        rotation_mode_init = self.blender_object.rotation_mode
        if euler_angles is not None:
            self.blender_object.rotation_mode = 'XYZ'
            self.blender_object.rotation_euler = euler_angles
        elif quaternion is not None:
            self.blender_object.rotation_mode = 'QUATERNION'
            self.blender_object.rotation_quaternion = quaternion
        self.blender_object.rotation_mode = rotation_mode_init
        self.apply_all_transforms()

    def scale(self, scale_vector):
        if isinstance(scale_vector, (float, int)):
            scale_vector = (scale_vector,) * 3
        self.blender_object.scale = scale_vector
        self.apply_all_transforms()

    def apply_all_transforms(self):
        with self.selected(mode='object'):
            bpy.ops.object.transform_apply()

    @property
    def dimensions(self):
        return self.blender_object.dimensions

    @property
    def bounding_box(self):
        return [Vector(x) for x in self.blender_object.bound_box]

    @property
    def enclosing_sphere_diameter(self):
        distances = [(v.co - self.location).length for v in self.vertices]
        return 2 * max(distances)

    @property
    def vertices(self):
        return self.blender_object.data.vertices

    @property
    def edges(self):
        return self.blender_object.data.edges

    @property
    def vertices_vtk(self):
        vertices = self.blender_object.data.vertices
        points = vtk.vtkPoints()
        coords = vtk.vtkFloatArray()
        coords.SetNumberOfComponents(3)
        coords.SetNumberOfTuples(len(vertices))
        for i, vertex in enumerate(vertices):
            coords.SetTuple3(i, *vertex.co)
        points.SetData(coords)
        return points

    @property
    def faces_vtk(self):
        faces = vtk.vtkCellArray()
        for polygon in self.blender_object.data.polygons:
            faces.InsertNextCell(len(polygon.vertices))
            for vertex in polygon.vertices:
                faces.InsertCellPoint(vertex)
        return faces

    @property
    def mesh_vtk(self):
        mesh = vtk.vtkPolyData()
        mesh.SetPoints(self.vertices_vtk)
        mesh.SetPolys(self.faces_vtk)
        return mesh

    @property
    def mesh_pyvista(self):
        mesh = pv.PolyData()
        mesh.SetPoints(self.vertices_vtk)
        mesh.SetPolys(self.faces_vtk)
        return mesh

    def position_randomly(self, bounding_box=None, fit_in_cylinder=True):
        x_min, x_max, y_min, y_max, z_min, z_max = bounding_box
        min_shift = (Vector([x_min, y_min, z_min])
                     - (self.location - self.dimensions/2))
        max_shift = (Vector([x_max, y_max, z_max])
                     - (self.location + self.dimensions/2))
        shift = Vector(np.random.uniform(low=min_shift, high=max_shift))

        if fit_in_cylinder:
            cylinder_radius = max(y_max - y_min, z_max - z_min)
            cylinder_axis = Vector([(y_min + y_max)/2, (z_min + z_max)/2])
            def point_fits_in_cylinder(point):
                    return (point.yz - cylinder_axis).length < cylinder_radius
            def objects_fits_in_cylinder():
                return all(point_fits_in_cylinder(v.co + shift) for v in self.vertices)
            while not objects_fits_in_cylinder():
                shift = Vector(np.random.uniform(low=min_shift, high=max_shift))

        self.translate(shift)
        return shift

    def apply_random_rotation(self):
        # Use multiplication by a random unit quaternion
        # https://en.wikipedia.org/wiki/Rotation_matrix#Uniform_random_rotation_matrices
        rotation_quaternion = np.random.uniform(low=0.0, high=1.0, size=4)
        rotation_quaternion /= np.linalg.norm(rotation_quaternion)
        self.rotate(quaternion=rotation_quaternion)
        return rotation_quaternion

    def select(self, mode=None):
        bpy.context.view_layer.objects.active = self.blender_object
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        self.blender_object.select_set(True)
        if mode is not None:
            bpy.ops.object.mode_set(mode=mode.upper())

    @contextmanager
    def selected(self, mode=None):
        """Temporarily select the object and revert selection on exiting context

        Also sets and reverts the active object and optionally object/edit mode.
        """
        active_object_initial = bpy.context.active_object
        selected_objects_initial = bpy.context.selected_objects
        mode_initial = bpy.context.object.mode
        self.select(mode=mode)
        try:
            yield
        finally:
            try:
                bpy.context.view_layer.objects.active = active_object_initial
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                for obj in selected_objects_initial:
                    obj.select_set(True)
                bpy.ops.object.mode_set(mode=mode_initial)
            except ReferenceError:
                # The original object got deleted
                pass

    def clear_selection(self):
        """Clears selection disregarding selection mode (vertex/edge/face)."""
        with self.selected(mode='edit'):
            bpy.ops.mesh.select_all(action='DESELECT')

    def select_vertices(self, criterion_func):
        # Ensure vertex selection mode beforehand, otherwise blender may e.g.
        # select all edges connected to specified vertices
        with self.selected(mode='edit'):
            bpy.ops.mesh.select_mode(type='VERT')
            bpy.ops.mesh.select_all(action='DESELECT')
        # Switching back to object mode is required for selecting(!)
        with self.selected(mode='object'):
            for vertex in self.vertices:
                if criterion_func(vertex):
                    vertex.select = True

    def select_edges(self, criterion_func):
        # Ensure edge selection mode beforehand, otherwise blender may e.g.
        # select all vertices connected to specified edges
        with self.selected(mode='edit'):
            bpy.ops.mesh.select_mode(type='EDGE')
            bpy.ops.mesh.select_all(action='DESELECT')
        # Switching back to object mode is required for selecting(!)
        with self.selected(mode='object'):
            for edge in self.edges:
                if criterion_func(edge):
                    edge.select = True

    @_suppress_stdout
    def remove_duplicate_vertices(self):
        with self.selected(mode='edit'):
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles()

    def smooth_edges(self, degree=0.05, n_segments=3):
        """Smooth all edges using bevel modifier"""
        with self.selected(mode='object'):
            bevel_width = degree * max(self.dimensions)
            if bevel_width < BLENDER_EPS:
                return
            bpy.ops.object.modifier_add(type='BEVEL')
            bpy.context.object.modifiers['Bevel'].width = bevel_width
            bpy.context.object.modifiers['Bevel'].segments = n_segments
            bpy.ops.object.modifier_apply(modifier='Bevel')

    def apply_boolean(self, other, operation='intersect'):
        """Apply a boolean operation based on another object"""
        with self.selected(mode='object'):
            bpy.ops.object.modifier_add(type='BOOLEAN')
            bpy.context.object.modifiers['Boolean'].operation = operation.upper()
            bpy.context.object.modifiers['Boolean'].object = other.blender_object
            bpy.ops.object.modifier_apply(modifier='Boolean')

    def export_stl(self, filepath):
        with self.selected(mode='object'):
            filepath = os.path.join(os.getcwd(), filepath)
            bpy.ops.export_mesh.stl(filepath=filepath, use_selection=True)
