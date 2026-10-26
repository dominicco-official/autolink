"""23552_10239b96_0025_2 (joint_set_10420, body two): a small washer / spacer.
Graph: hole cylinder r=0.2 (reversed), outer cylinder r=0.3, planes at y=0 and y=0.3. Axis Y, centre (1.5, *, 5.5)."""
import cadquery as cq
ORIGIN = (1.5, 0.0, 5.5)
PARAMS = {"hole_radius": 0.2, "outer_radius": 0.3, "thickness": 0.3}
def build(hole_radius, outer_radius, thickness):
    pts = [(hole_radius, 0), (outer_radius, 0), (outer_radius, thickness), (hole_radius, thickness)]
    return cq.Workplane("XY").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0)).translate(ORIGIN)
