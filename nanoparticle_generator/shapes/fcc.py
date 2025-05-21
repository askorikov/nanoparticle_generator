import numpy as np

from nanoparticle_generator.blender import BlenderObjectReference
from nanoparticle_generator.shapes import basic


class Sphere(BlenderObjectReference):
    def __init__(self, diameter=1.0):
        basic.Ellipsoid.__init__(self, diameter)


class Cube(BlenderObjectReference):
    def __init__(self, size=1.0, smoothing_degree=0.0):
        basic.Box.__init__(self, size)
        self.smooth_edges(smoothing_degree)
        self.scale(size / max(self.dimensions))


class Rod(BlenderObjectReference):
    def __init__(self, height=1.0, diameter=0.5):
        middle_section_height = height - diameter
        basic.SphericallyCappedCylinder.__init__(self, diameter,
                                                 middle_section_height)


class Octahedron(BlenderObjectReference):
    def __init__(self, size=1.0, smoothing_degree=0.0):
        basic.Octahedron.__init__(self, size)
        self.smooth_edges(smoothing_degree)
        self.scale(size / self.enclosing_sphere_diameter)


class TruncatedOctahedron(BlenderObjectReference):
    def __init__(self, size=1.0, truncation_degree=0.0, smoothing_degree=0.0):
        basic.Octahedron.__init__(self, size, truncation_degree)
        self.smooth_edges(smoothing_degree)
        self.scale(size / self.enclosing_sphere_diameter)


class Icosahedron(BlenderObjectReference):
    def __init__(self, size=1.0, smoothing_degree=0.0):
        basic.Icosahedron.__init__(self, size)
        self.smooth_edges(smoothing_degree)
        self.scale(size / self.enclosing_sphere_diameter)


class Triangle(BlenderObjectReference):
    def __init__(self, size=1.0, height=0.2, tips_smoothing_degree=0.0,
                 edges_smoothing_degree=0.0):
        n_sides = 3
        truncation_degree = 0.0
        basic.Prism.__init__(self, n_sides, size, height,
                             truncation_degree, tips_smoothing_degree,
                             edges_smoothing_degree)
        self.scale(size / np.hypot(self.dimensions.x, self.dimensions.y))


class TruncatedTriangle(BlenderObjectReference):
    def __init__(self, size=1.0, height=0.2, truncation_degree=0.5,
                 tips_smoothing_degree=0.0, edges_smoothing_degree=0.0):
        n_sides = 3
        basic.Prism.__init__(self, n_sides, size, height,
                             truncation_degree, tips_smoothing_degree,
                             edges_smoothing_degree)


class Square(BlenderObjectReference):
    def __init__(self, size=1.0, height=0.2, truncation_degree=0.0,
                 tips_smoothing_degree=0.0, edges_smoothing_degree=0.0):
        n_sides = 4
        basic.Prism.__init__(self, n_sides, size, height,
                             truncation_degree, tips_smoothing_degree,
                             edges_smoothing_degree)


class Hexagon(BlenderObjectReference):
    def __init__(self, size=1.0, height=0.2, truncation_degree=0.5,
                 tips_smoothing_degree=0.0, edges_smoothing_degree=0.0):
        n_sides = 6
        basic.Prism.__init__(self, n_sides, size, height,
                             truncation_degree, tips_smoothing_degree,
                             edges_smoothing_degree)


class Decahedron(BlenderObjectReference):
    def __init__(self, size=1.0, smoothing_degree=0.0):
        """Oblate pentagonal bipyramid defined by {111} FCC lattice planes."""
        n_sides = 5
        height = 1.547 * size / 2
        basic.Bipyramid.__init__(self, n_sides, size, height)
        self.smooth_edges(smoothing_degree)
        self.scale(size / np.hypot(self.dimensions.x, self.dimensions.y))


class Bipyramid(BlenderObjectReference):
    def __init__(self, height=1.0, tips_truncation_degree=0.0, smoothing_degree=0.0):
        """Typical Au pentagonal bipyramid (tip angle ~30 deg)."""
        n_sides = 5
        diameter = height / 3.7321
        basic.Bipyramid.__init__(self, n_sides, diameter, height, tips_truncation_degree)
        self.smooth_edges(smoothing_degree)
        self.scale(height / self.dimensions.z)
