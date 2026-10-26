"""56488_7a606724_0007_1 (joint_set_07243, body one): a small washer.
Graph: hole cylinder r=0.08115 (reversed), outer cylinder r=0.247287, planes at y=5.0 (+Y) and y=4.85 (-Y). Axis Y."""
import cadquery as cq
ORIGIN = (-9.985479, 4.850000, 33.353140)
PARAMS = {"inner_radius": 0.081150, "outer_radius": 0.247287, "thickness": 0.15}
def build(inner_radius, outer_radius, thickness):
    pts = [(inner_radius, 0), (outer_radius, 0), (outer_radius, thickness), (inner_radius, thickness)]
    return cq.Workplane("XY").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0)).translate(ORIGIN)
