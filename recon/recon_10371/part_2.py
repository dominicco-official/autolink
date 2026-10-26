"""41729_b5092135_0006_1 (joint_set_10371, body two): an axle rod.
Graph: cylinder r=2.5, end planes at y=0 and y=41.5. Axis Y."""
import cadquery as cq
PARAMS = {"radius": 2.5, "length": 41.5}
def build(radius, length):
    return cq.Workplane("XZ").circle(radius).extrude(-length)
