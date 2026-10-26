"""55717_8ee13ef1_0007_2 (joint_set_08045, body two): a long rod with a bored head.
Graph: rod cylinder r=0.508 for x in [-12.7, 0]; head cylinder r=0.635 for x in [0, 1.27];
bore cylinder r=0.3175 (reversed) for x in [0, 1.27] with its floor plane at x=0; end planes at x=-12.7 and x=1.27 (annulus). Axis X."""
import cadquery as cq
PARAMS = {"rod_radius": 0.508, "rod_length": 12.70, "head_radius": 0.635, "head_length": 1.27, "bore_radius": 0.3175}
def build(rod_radius, rod_length, head_radius, head_length, bore_radius):
    r, L, R, H, b = rod_radius, rod_length, head_radius, head_length, bore_radius
    pts = [(-L, 0), (-L, r), (0, r), (0, R), (H, R), (H, b), (0, b), (0, 0)]
    return cq.Workplane("XY").polyline(pts).close().revolve(360, (0, 0, 0), (1, 0, 0))
