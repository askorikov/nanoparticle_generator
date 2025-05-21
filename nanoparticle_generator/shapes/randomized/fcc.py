import numpy as np

from nanoparticle_generator.blender import BlenderObjectReference
from nanoparticle_generator.shapes import fcc


class Sphere(BlenderObjectReference):
    def __init__(self):
        fcc.Sphere.__init__(self)


class Cube(BlenderObjectReference):
    def __init__(self):
        size = 1.0
        smoothing_degree = np.random.uniform(low=0.0, high=0.1)
        fcc.Cube.__init__(self, size, smoothing_degree)


class Rod(BlenderObjectReference):
    def __init__(self):
        height = 1.0
        diameter = np.random.uniform(low=0.25, high=1.0)
        fcc.Rod.__init__(self, height, diameter)


class Octahedron(BlenderObjectReference):
    def __init__(self):
        size = 1.0
        smoothing_degree = np.random.uniform(low=0.0, high=0.1)
        fcc.Octahedron.__init__(self, size, smoothing_degree)


class TruncatedOctahedron(BlenderObjectReference):
    def __init__(self):
        size = 1.0
        truncation_degree = np.random.uniform(low=0.0, high=1.0)
        smoothing_degree = np.random.uniform(low=0.0, high=0.1)
        fcc.TruncatedOctahedron.__init__(self, size, truncation_degree, smoothing_degree)


class Icosahedron(BlenderObjectReference):
    def __init__(self):
        size = 1.0
        smoothing_degree = np.random.uniform(low=0.0, high=0.1)
        fcc.Icosahedron.__init__(self, size, smoothing_degree)


class Triangle(BlenderObjectReference):
    def __init__(self):
        size = 1.0
        height = np.random.uniform(low=0.1, high=0.3)
        tips_smoothing_degree = np.random.uniform(low=0.0, high=0.1)
        edges_smoothing_degree = np.random.uniform(low=0.0, high=0.1)
        fcc.Triangle.__init__(self, size, height, tips_smoothing_degree,
                              edges_smoothing_degree)


class TruncatedTriangle(BlenderObjectReference):
    def __init__(self):
        size= 1.0
        height = np.random.uniform(low=0.1, high=0.3)
        truncation_degree = np.random.uniform(low=0.0, high=1.0)
        tips_smoothing_degree = np.random.uniform(low=0.0, high=0.1)
        edges_smoothing_degree = np.random.uniform(low=0.0, high=0.1)
        fcc.TruncatedTriangle.__init__(self, size, height, truncation_degree,
                                       tips_smoothing_degree,
                                       edges_smoothing_degree)


class Square(BlenderObjectReference):
    def __init__(self):
        size = 1.0
        height = np.random.uniform(low=0.1, high=0.3)
        truncation_degree = 0.0
        tips_smoothing_degree = np.random.uniform(low=0.0, high=0.1)
        edges_smoothing_degree = np.random.uniform(low=0.0, high=0.1)
        fcc.Square.__init__(self, size, height, truncation_degree,
                            tips_smoothing_degree, edges_smoothing_degree)


class Hexagon(BlenderObjectReference):
    def __init__(self):
        size = 1.0
        height = np.random.uniform(low=0.1, high=0.3)
        truncation_degree = 0.0
        tips_smoothing_degree = np.random.uniform(low=0.0, high=0.1)
        edges_smoothing_degree = np.random.uniform(low=0.0, high=0.1)
        fcc.Hexagon.__init__(self,size, height, truncation_degree,
                             tips_smoothing_degree, edges_smoothing_degree)


class Decahedron(BlenderObjectReference):
    def __init__(self):
        """Oblate pentagonal bipyramid defined by {111} FCC lattice planes."""
        size = 1.0
        smoothing_degree = np.random.uniform(low=0.0, high=0.1)
        fcc.Decahedron.__init__(self, size, smoothing_degree)


class Bipyramid(BlenderObjectReference):
    def __init__(self):
        """Typical Au pentagonal bipyramid (tip angle ~30 deg)."""
        height = 1.0
        smoothing_degree = np.random.uniform(low=0.0, high=0.1)
        fcc.Bipyramid.__init__(self, height, tips_truncation_degree=smoothing_degree,
                               smoothing_degree=smoothing_degree)


ALL_SHAPES = (Sphere, Cube, Rod, Octahedron, TruncatedOctahedron, Icosahedron,
              Triangle, TruncatedTriangle, Square, Hexagon, Decahedron, Bipyramid)


CORE_SHELL_SUITABLE_SHAPES = (Sphere, Cube, Rod, Octahedron,
                              TruncatedOctahedron, Icosahedron,
                              Decahedron, Bipyramid)
