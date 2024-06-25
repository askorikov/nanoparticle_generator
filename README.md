# Nanoparticle generator

A simple Python module to generate and randomize typical nanoparticle shapes
using Blender.

## Installation

`pip install .`

## Usage

See the [demo notebook](notebooks/demo.ipynb).

## Features

Following shapes are available:
* Basic
  - Bipyramid
  - Box
  - Cylinder
  - Ellipsoid
  - Icosahedron
  - Octahedron
  - Prism
  - SphericallyCappedCylinder
* Shapes typical for FCC materials
  - Bipyramid
  - Cube
  - Decahedron
  - Hexagon
  - Icosahedron
  - Octahedron
  - Rod
  - Sphere
  - Square
  - Triangle
  - Truncated octahedron
  - Truncated triangle

FCC shapes are also implemented as a randomized generator containing reasonable
ranges of variable shape parameters (aspect ratio, smoothing degree, etc.)

Every shape can be modified using the following (+native Blender modifiers):
* Translation
* Rotation
* Scaling
* Edge smoothing

These transformations are also implemented as a randomized generator with
suitable parameter ranges.
