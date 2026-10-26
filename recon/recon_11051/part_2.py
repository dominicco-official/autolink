"""
Reconstruction of dataset body 41653_71b50655_0004_2 (joint_set_11051, body two).
Written by the assistant from the B-Rep graph JSON, not from the mesh.

Graph said: 3 faces = plane (x=-3.5, normal -X), cylinder (radius 2.5, axis +X,
centroid x=-1.75), plane (x=0, normal +X). Bounding box x in [-3.5, 0].
"""
import cadquery as cq

PARAMS = {"radius": 2.5, "length": 3.5}


def build(radius=2.5, length=3.5):
    return cq.Workplane("YZ", origin=(-length, 0, 0)).circle(radius).extrude(length)
