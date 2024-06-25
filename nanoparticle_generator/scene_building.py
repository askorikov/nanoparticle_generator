import random

import numpy as np

from nanoparticle_generator.blender import BlenderScene
from nanoparticle_generator.shapes.randomized import fcc


class Scene(BlenderScene):
    def __init__(self, extent=(-0.5, 0.5, -0.5, 0.5, -0.5, 0.5)):
        """Blender scene used for composing shapes"""
        self.extent = extent
        BlenderScene.__init__(self)

    def add_random_shape(self, shape_package=fcc):
        shape = random.choice(shape_package.ALL_SHAPES)()
        shape.apply_random_rotation()
        scale_factor = np.random.uniform(low=0.75, high=0.9)
        shape.scale(scale_factor / max(shape.dimensions))
        shape.position_randomly(bounding_box=[0.95*x for x in self.extent])
        return shape

    def add_random_core_shell_shape(self, shape_package=fcc):
        shell_shape = random.choice(shape_package.CORE_SHELL_SUITABLE_SHAPES)()
        shell_rotation_quaternion = shell_shape.apply_random_rotation()
        shell_scale_factor = np.random.uniform(low=0.75, high=0.9)
        shell_shape.scale(shell_scale_factor / max(shell_shape.dimensions))
        shell_shift = shell_shape.position_randomly(
            bounding_box=[0.95*x for x in self.extent])

        core_shape = random.choice(shape_package.CORE_SHELL_SUITABLE_SHAPES)()
        core_shape.rotate(quaternion=shell_rotation_quaternion)
        core_scale_factor = np.random.uniform(low=0.5, high=0.9)
        core_shape.scale(core_scale_factor * shell_shape.enclosing_sphere_diameter
                         / core_shape.enclosing_sphere_diameter)
        core_shape.translate(shell_shift)

        # Subtract shapes from each other. Use core copy to avoid boundary artifacts
        core_shape_copy = core_shape.copy()
        core_shape.apply_boolean(other=shell_shape, operation='intersect')
        shell_shape.apply_boolean(other=core_shape_copy, operation='difference')
        del core_shape_copy

        return core_shape, shell_shape
