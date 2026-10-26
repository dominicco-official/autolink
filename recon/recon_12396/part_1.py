"""55634_3b61fa4d_0008_1 (joint_set_12396, body one): a rivet-like button along +X at (y=5, z=0), x 7.492254..8.142254.
Through bore r=0.08; flange r=0.22 (0.08 long, with a hair of taper), 30-degree chamfer down to the shank r=0.12, shank to x=7.85,
then a near-spherical head: arc of radius 0.2 centred at x=8.007442 (0.0034 below the axis) ending at r=0.144399 on the flat end."""
import math, cadquery as cq
ORIGIN = (0.0, 5.0, 0.0)
PARAMS = {"x0": 7.492254, "bore_radius": 0.08, "flange_radius": 0.22, "flange_length": 0.08, "flange_end_radius": 0.220019, "shank_radius": 0.12, "chamfer_end_x": 7.63,
          "shank_end_x": 7.85, "head_arc_radius": 0.2, "head_arc_cx": 8.007442, "head_arc_cr": -0.0034, "x_end": 8.142254, "end_radius": 0.144399}
def build(x0, bore_radius, flange_radius, flange_length, flange_end_radius, shank_radius, chamfer_end_x, shank_end_x, head_arc_radius, head_arc_cx, head_arc_cr, x_end, end_radius):
    A = (shank_end_x, shank_radius); B = (x_end, end_radius); C = (head_arc_cx, head_arc_cr)
    a1 = math.atan2(A[1] - C[1], A[0] - C[0]); a2 = math.atan2(B[1] - C[1], B[0] - C[0]); am = (a1 + a2) / 2
    M = (C[0] + head_arc_radius * math.cos(am), C[1] + head_arc_radius * math.sin(am))
    wp = (cq.Workplane("XY").moveTo(x0, bore_radius).lineTo(x0, flange_radius).lineTo(x0 + flange_length, flange_end_radius).lineTo(chamfer_end_x, shank_radius)
          .lineTo(*A).threePointArc(M, B).lineTo(x_end, bore_radius).close())
    return wp.revolve(360, (0, 0, 0), (1, 0, 0)).translate(ORIGIN)
