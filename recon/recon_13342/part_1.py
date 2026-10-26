"""21237_7887a24b_0048_1 (joint_set_13342, body one): a stepped pin along +X: tip r=0.1 (x 0..0.135), collar r=0.25 (x 0.135..0.36),
shank r=0.144 (x 0.36..0.71), chamfer cone to r=0.104 at x=0.81, flat end."""
import cadquery as cq
PARAMS = {"tip_radius": 0.1, "tip_length": 0.135, "collar_radius": 0.25, "collar_length": 0.225, "shank_radius": 0.144, "shank_length": 0.35, "chamfer_length": 0.1, "end_radius": 0.104}
def build(tip_radius, tip_length, collar_radius, collar_length, shank_radius, shank_length, chamfer_length, end_radius):
    x1 = tip_length; x2 = x1 + collar_length; x3 = x2 + shank_length; x4 = x3 + chamfer_length
    pts = [(0, 0), (0, tip_radius), (x1, tip_radius), (x1, collar_radius), (x2, collar_radius), (x2, shank_radius), (x3, shank_radius), (x4, end_radius), (x4, 0)]
    return cq.Workplane("XY").polyline(pts).close().revolve(360, (0, 0, 0), (1, 0, 0))
