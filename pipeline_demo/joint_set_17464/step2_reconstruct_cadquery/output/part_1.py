"""89527_b3bf425d_0031_1 (joint_set_17464, body one): a stepped bushing, axis -Y from y=0 down to y=-1.3.
Bore r=0.2 through; outer r=0.3 for y in [-0.8, 0]; outer r=0.24505 for y in [-1.3, -0.8]; shoulder at y=-0.8."""
import cadquery as cq
PARAMS = {"bore_radius": 0.2, "head_radius": 0.3, "head_length": 0.8, "shank_radius": 0.24505, "shank_length": 0.5}
def build(bore_radius, head_radius, head_length, shank_radius, shank_length):
    b, R, h, r, l = bore_radius, head_radius, head_length, shank_radius, shank_length
    pts = [(b, 0), (R, 0), (R, -h), (r, -h), (r, -h - l), (b, -h - l)]
    return cq.Workplane("XY").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0))
