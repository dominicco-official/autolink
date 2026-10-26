"""23552_10239b96_0025_1 (joint_set_10420, body one): a disc with a center hole.
Graph: hole cylinder r=0.2 (reversed), outer cylinder r=1.4, planes at y=0 and y=0.4. Axis Y, centre (5.0, *, 6.1)."""
import cadquery as cq
ORIGIN = (5.0, 0.0, 6.1)
PARAMS = {"hole_radius": 0.2, "outer_radius": 1.4, "thickness": 0.4}
def build(hole_radius, outer_radius, thickness):
    pts = [(hole_radius, 0), (outer_radius, 0), (outer_radius, thickness), (hole_radius, thickness)]
    return cq.Workplane("XY").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0)).translate(ORIGIN)
