"""56488_7a606724_0007_2 (joint_set_07243, body two): a plain pin.
Graph: cylinder r=0.096675, end planes at y=5.0 (+Y) and y=4.5 (-Y). Axis Y."""
import cadquery as cq
ORIGIN = (8.347287, 4.500000, 10.000204)
PARAMS = {"radius": 0.096675, "length": 0.50}
def build(radius, length):
    return cq.Workplane("XZ", origin=ORIGIN).circle(radius).extrude(-length)   # XZ normal is -Y, so extrude -length goes +Y
