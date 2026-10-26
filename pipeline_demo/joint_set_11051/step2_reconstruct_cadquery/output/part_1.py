"""
Reconstruction of dataset body 41653_71b50655_0004_1 (joint_set_11051, body one).
Written by the assistant from the B-Rep graph JSON, not from the mesh.

Graph said: 3 faces = plane (x=0, normal +X), plane (x=-1.5, normal -X),
cylinder (radius 2.0, axis +X, centroid x=-0.75). Bounding box x in [-1.5, 0].
Units: cm (Fusion 360 default).
"""
import cadquery as cq

PARAMS = {"radius": 2.0, "length": 1.5}


def build(radius=2.0, length=1.5):
    # Disc on the YZ plane, extruded along +X so it spans x in [-length, 0]
    return cq.Workplane("YZ", origin=(-length, 0, 0)).circle(radius).extrude(length)
